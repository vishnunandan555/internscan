"""Unit tests for root README.md and regional markdown generators."""
import os
import tempfile
import unittest
from scraper import render_readme, render_list
from scraper.countries import SUPPORTED_COUNTRIES


class TestRenderers(unittest.TestCase):
    def test_render_readme_and_regional_jobs(self):
        sample_state = {
            "updated_at": "2026-10-16T12:00:00Z",
            "jobs": {
                "google:101": {
                    "company": "Google",
                    "title": "SWE Intern 2027",
                    "url": "https://careers.google.com/jobs/101",
                    "locations": ["Bengaluru, India"],
                    "city_tag": "Bengaluru",
                    "category": "Software",
                    "country": "in",
                    "posted": "2026-10-10",
                    "first_seen": "2026-10-14",
                    "active": True,
                },
                "amazon:202": {
                    "company": "Amazon",
                    "title": "SDE Intern 2027",
                    "url": "https://amazon.jobs/202",
                    "locations": ["Seattle, WA, USA"],
                    "city_tag": "Seattle",
                    "category": "Software",
                    "country": "us",
                    "posted": "2026-10-12",
                    "first_seen": "2026-10-14",
                    "active": True,
                },
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            orig_readme = render_readme.README_PATH
            orig_regions = render_readme.REGIONS_DIR

            try:
                render_readme.README_PATH = os.path.join(tmpdir, "README.md")
                render_readme.REGIONS_DIR = os.path.join(tmpdir, "regions")

                render_readme.render(sample_state)

                # Check root README.md
                self.assertTrue(os.path.exists(render_readme.README_PATH))
                with open(render_readme.README_PATH, encoding="utf-8") as f:
                    readme_content = f.read()
                self.assertIn("The Global Directory for Tech Internships", readme_content)
                self.assertIn("regions/in/jobs.md", readme_content)
                self.assertIn("regions/us/jobs.md", readme_content)

                # Check regional jobs.md for each supported country
                for code in SUPPORTED_COUNTRIES:
                    job_file = os.path.join(render_readme.REGIONS_DIR, code, "jobs.md")
                    self.assertTrue(os.path.exists(job_file), f"Missing {job_file}")
                    with open(job_file, encoding="utf-8") as f:
                        content = f.read()
                    self.assertIn("Active Tech & Software Internship Listings", content)
                    self.assertIn("companies.md", content)

            finally:
                render_readme.README_PATH = orig_readme
                render_readme.REGIONS_DIR = orig_regions

    def test_render_regional_companies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_regions = render_list.REGIONS_DIR

            try:
                render_list.REGIONS_DIR = os.path.join(tmpdir, "regions")
                render_list.render_list(succeeded=["Google", "Meta", "Amazon"], failed={})

                # Check regional companies.md for each supported country
                for code in SUPPORTED_COUNTRIES:
                    comp_file = os.path.join(render_list.REGIONS_DIR, code, "companies.md")
                    self.assertTrue(os.path.exists(comp_file), f"Missing {comp_file}")
                    with open(comp_file, encoding="utf-8") as f:
                        content = f.read()
                    self.assertIn("Tracked Employers & ATS Coverage", content)
                    self.assertIn("jobs.md", content)
                    self.assertIn("Directly Scraped Employers", content)

            finally:
                render_list.REGIONS_DIR = orig_regions


if __name__ == "__main__":
    unittest.main()
