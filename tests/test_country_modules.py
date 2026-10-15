"""Unit tests for modular country registry in scraper.countries."""
import unittest

from scraper.countries import (
    COUNTRY_METADATA,
    SUPPORTED_COUNTRIES,
    get_companies_for_country,
    get_unsupported_for_country,
)


class TestCountryModules(unittest.TestCase):
    def test_supported_countries(self):
        self.assertIn("in", SUPPORTED_COUNTRIES)
        self.assertIn("us", SUPPORTED_COUNTRIES)
        self.assertIn("ca", SUPPORTED_COUNTRIES)
        self.assertIn("uk", SUPPORTED_COUNTRIES)
        self.assertIn("eu", SUPPORTED_COUNTRIES)

    def test_country_metadata(self):
        for code in SUPPORTED_COUNTRIES:
            self.assertIn(code, COUNTRY_METADATA)
            meta = COUNTRY_METADATA[code]
            self.assertEqual(meta["code"], code)
            self.assertIn("name", meta)
            self.assertIn("flag", meta)
            self.assertIn("currency", meta)
            self.assertIn("hubs", meta)
            self.assertGreater(len(meta["hubs"]), 0)

    def test_india_companies_count(self):
        direct = get_companies_for_country("in", include_fallback=False)
        self.assertEqual(len(direct), 60)
        names = {c["name"] for c in direct}
        self.assertIn("Google", names)
        self.assertIn("Swiggy", names)
        self.assertIn("Razorpay", names)
        self.assertIn("Target", names)

        unsupported = get_unsupported_for_country("in")
        self.assertEqual(len(unsupported), 32)
        self.assertIn("Juspay", unsupported)
        self.assertIn("Dream11", unsupported)

    def test_usa_companies_count(self):
        direct = get_companies_for_country("us", include_fallback=False)
        self.assertGreaterEqual(len(direct), 50)
        names = {c["name"] for c in direct}
        self.assertIn("Google", names)
        self.assertIn("Microsoft", names)
        self.assertIn("Apple", names)
        self.assertIn("Roblox", names)
        self.assertIn("DoorDash", names)
        self.assertIn("Palantir", names)
        # Domestic India startups must NOT be present in US
        self.assertNotIn("Swiggy", names)
        self.assertNotIn("Meesho", names)
        self.assertNotIn("CRED", names)


if __name__ == "__main__":
    unittest.main()
