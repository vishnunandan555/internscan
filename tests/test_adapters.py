"""Unit tests for adapters including Keka and Greenhouse."""
import unittest
from unittest.mock import patch

from scraper.adapters import keka


class TestKekaAdapter(unittest.TestCase):
    @patch("scraper.adapters.keka.request_json")
    def test_keka_fetch(self, mock_request_json):
        mock_request_json.return_value = [
            {
                "id": 164757,
                "title": "AI Engineer Intern",
                "jobNumber": "DD00109-05",
                "jobLocations": [
                    {
                        "id": 5588,
                        "name": "Bangalore",
                        "city": "Bangalore",
                        "countryName": "India",
                    }
                ],
                "publishedOn": "2026-10-08T14:46:37.853Z",
            },
            {
                "id": 145733,
                "title": "Assistant Manager - Business & Partnerships",
                "jobNumber": "TM001",
                "jobLocations": [],
                "publishedOn": "2026-10-10T10:00:00.000Z",
            },
        ]
        cfg = {"name": "Discover Dollar", "subdomain": "discoverdollar"}
        jobs = keka.fetch(cfg)
        self.assertEqual(len(jobs), 2)

        j1 = jobs[0]
        self.assertEqual(j1.company, "Discover Dollar")
        self.assertEqual(j1.external_id, "164757")
        self.assertEqual(j1.title, "AI Engineer Intern")
        self.assertEqual(j1.url, "https://discoverdollar.keka.com/careers/jobdetails/164757")
        self.assertEqual(j1.locations, ["Bangalore, India"])
        self.assertEqual(j1.posted, "2026-10-08")
        self.assertTrue(j1.looks_like_internship())

        j2 = jobs[1]
        self.assertEqual(j2.company, "Discover Dollar")
        self.assertEqual(j2.external_id, "145733")
        self.assertFalse(j2.looks_like_internship())


if __name__ == "__main__":
    unittest.main()
