"""Unit tests for public API endpoint and RSS feed generation."""
import json
import os
import tempfile
import unittest
from scraper import api


class TestApiGenerator(unittest.TestCase):
    def test_generate_apis_output(self):
        sample_state = {
            "updated_at": "2026-10-14T03:00:00Z",
            "jobs": {
                "google:101": {
                    "company": "Google",
                    "title": "SWE Intern 2027",
                    "url": "https://careers.google.com/jobs/101",
                    "locations": ["Bengaluru, Karnataka, India"],
                    "city_tag": "Bengaluru",
                    "category": "Software",
                    "posted": "2026-10-10",
                    "first_seen": "2026-10-14",
                    "active": True,
                },
                "meta:202": {
                    "company": "Meta",
                    "title": "Old Intern",
                    "url": "https://metacareers.com/202",
                    "locations": ["Hyderabad, Telangana, India"],
                    "city_tag": "Hyderabad",
                    "category": "AI/ML",
                    "posted": "2026-08-01",
                    "first_seen": "2026-08-01",
                    "active": False,
                },
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            orig_docs = api.DOCS_DIR
            orig_api = api.API_DIR
            orig_feed = api.FEED_PATH
            orig_latest = api.LATEST_API_PATH
            orig_active = api.ACTIVE_API_PATH
            orig_metrics = api.METRICS_PATH

            try:
                api.DOCS_DIR = tmpdir
                api.API_DIR = os.path.join(tmpdir, "api")
                api.FEED_PATH = os.path.join(tmpdir, "feed.xml")
                api.LATEST_API_PATH = os.path.join(tmpdir, "api", "latest.json")
                api.ACTIVE_API_PATH = os.path.join(tmpdir, "api", "active.json")
                api.METRICS_PATH = os.path.join(tmpdir, "metrics.json")

                res = api.generate_apis(sample_state)

                self.assertEqual(res["active_count"], 1)
                self.assertTrue(os.path.exists(api.ACTIVE_API_PATH))
                self.assertTrue(os.path.exists(api.LATEST_API_PATH))
                self.assertTrue(os.path.exists(api.FEED_PATH))

                with open(api.ACTIVE_API_PATH, encoding="utf-8") as f:
                    active_data = json.load(f)
                    self.assertEqual(active_data["total_active"], 1)
                    self.assertEqual(active_data["jobs"][0]["company"], "Google")

                with open(api.FEED_PATH, encoding="utf-8") as f:
                    rss_text = f.read()
                    self.assertIn("<rss version=\"2.0\"", rss_text)
                    self.assertIn("SWE Intern 2027", rss_text)

                # Check country partitions and metrics.json
                metrics_path = os.path.join(tmpdir, "metrics.json")
                self.assertTrue(os.path.exists(metrics_path))
                with open(metrics_path, encoding="utf-8") as f:
                    metrics = json.load(f)
                    self.assertIn("countries", metrics)
                    self.assertIn("in", metrics["countries"])
                    self.assertIn("us", metrics["countries"])

                in_active_path = os.path.join(tmpdir, "in", "api", "active.json")
                self.assertTrue(os.path.exists(in_active_path))

            finally:
                api.DOCS_DIR = orig_docs
                api.API_DIR = orig_api
                api.FEED_PATH = orig_feed
                api.LATEST_API_PATH = orig_latest
                api.ACTIVE_API_PATH = orig_active
                api.METRICS_PATH = orig_metrics


if __name__ == "__main__":
    unittest.main()
