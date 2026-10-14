"""Unit tests for company registry, Target config, and fallback adapters."""
import os
import unittest
from unittest.mock import patch

from scraper.companies import (
    COMPANIES,
    FALLBACK_COMPANIES,
    UNSUPPORTED,
    get_all_known_companies,
    get_companies,
    has_fallback_keys,
)


class TestCompanies(unittest.TestCase):
    def test_direct_companies_validity(self):
        self.assertGreaterEqual(len(COMPANIES), 60)
        names = set()
        for c in COMPANIES:
            self.assertIn("name", c)
            self.assertIn("fetch", c)
            self.assertTrue(callable(c["fetch"]))
            self.assertNotIn(c["name"], names, f"Duplicate company name: {c['name']}")
            names.add(c["name"])

    def test_target_configuration(self):
        target = next((c for c in COMPANIES if c["name"] == "Target"), None)
        self.assertIsNotNone(target, "Target must be configured in COMPANIES")
        self.assertEqual(target.get("host"), "target.wd5.myworkdayjobs.com")
        self.assertEqual(target.get("site"), "targetcareers")
        self.assertIn("applied_facets", target)
        self.assertIn("Location_Country", target["applied_facets"])
        self.assertNotIn("Target", UNSUPPORTED, "Target must not be listed in UNSUPPORTED")

    def test_fallback_companies_configuration(self):
        fallback_names = {c["name"] for c in FALLBACK_COMPANIES}
        self.assertTrue({"Uber", "Flipkart", "SAP", "HP", "Atlassian"}.issubset(fallback_names))
        for c in FALLBACK_COMPANIES:
            self.assertIn("query", c)
            self.assertTrue(callable(c["fetch"]))

    def test_get_companies_dynamic_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SERP_API_KEY", None)
            os.environ.pop("RAPIDAPI_KEY", None)
            self.assertFalse(has_fallback_keys())
            active = get_companies()
            self.assertEqual(len(active), len(COMPANIES))
            self.assertNotIn("Uber", [c["name"] for c in active])

        with patch.dict(os.environ, {"SERP_API_KEY": "test-key"}):
            self.assertTrue(has_fallback_keys())
            active = get_companies()
            self.assertEqual(len(active), len(COMPANIES) + len(FALLBACK_COMPANIES))
            self.assertIn("Uber", [c["name"] for c in active])
            self.assertIn("Flipkart", [c["name"] for c in active])

    def test_get_all_known_companies(self):
        all_known = get_all_known_companies()
        self.assertEqual(len(all_known), len(COMPANIES) + len(FALLBACK_COMPANIES))


if __name__ == "__main__":
    unittest.main()
