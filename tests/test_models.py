"""Unit tests for Job data model, date parsing, and location normalization."""
import unittest
from scraper.models import Job, as_date, normalize_locations


class TestModels(unittest.TestCase):
    def test_job_uid_generation(self):
        job = Job(
            company="Google LLC",
            external_id="12345",
            title="Software Engineering Intern",
            url="https://careers.google.com/jobs/results/12345",
        )
        self.assertEqual(job.uid, "google-llc:12345")

    def test_job_to_dict_and_normalization(self):
        job = Job(
            company="Amazon",
            external_id="A9876",
            title="  SDE Intern  ",
            url="https://amazon.jobs/en/jobs/A9876",
            locations="Bengaluru, India; Hyderabad, India",
        )
        d = job.to_dict()
        self.assertEqual(d["company"], "Amazon")
        self.assertEqual(d["title"], "SDE Intern")
        self.assertIn("Bengaluru, India", d["locations"])
        self.assertIn("Hyderabad, India", d["locations"])

    def test_normalize_locations_various_shapes(self):
        self.assertEqual(normalize_locations("Bengaluru; Hyderabad"), ["Bengaluru", "Hyderabad"])
        self.assertEqual(normalize_locations("Pune\nChennai"), ["Pune", "Chennai"])
        self.assertEqual(normalize_locations(["Delhi", "Gurgaon"]), ["Delhi", "Gurgaon"])
        raw_dicts = [{"city": "Bengaluru", "country": "India"}, {"city": "Hyderabad", "country": "India"}]
        self.assertEqual(normalize_locations(raw_dicts), ["Bengaluru, India", "Hyderabad, India"])
        self.assertEqual(normalize_locations(None), [])
        self.assertEqual(normalize_locations(""), [])

    def test_as_date_parsing(self):
        cases = [
            ("2026-07-09", "2026-07-09"),
            ("2026-07-09T14:30:00Z", "2026-07-09"),
            ("July 09, 2026", "2026-07-09"),
            ("Jul 09, 2026", "2026-07-09"),
            (1783584000, "2026-07-09"),
            (1783584000000, "2026-07-09"),
            ("invalid-date", None),
            (None, None),
        ]
        for val, expected in cases:
            with self.subTest(val=val):
                self.assertEqual(as_date(val), expected)

    def test_is_internship(self):
        from scraper.models import is_internship
        self.assertTrue(is_internship("Software Engineering Intern"))
        self.assertTrue(is_internship("Graduate Apprentice 2026"))
        self.assertTrue(is_internship("Technical Apprentice - Software"))
        self.assertTrue(is_internship("Student Trainee - AI/ML"))
        self.assertTrue(is_internship("Project Trainee"))
        self.assertTrue(is_internship("Graduate Engineer Trainee"))
        self.assertFalse(is_internship("Internal Software Engineer"))
        self.assertFalse(is_internship("International Sales Director"))


if __name__ == "__main__":
    unittest.main()
