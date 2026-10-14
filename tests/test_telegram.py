"""Unit tests for Telegram notification formatting and dispatch handling."""
import unittest
from scraper import telegram


class TestTelegramNotifier(unittest.TestCase):
    def test_format_job_message_new(self):
        job = {
            "company": "Amazon",
            "title": "Software Development Engineer Intern",
            "category": "Software",
            "city_tag": "Bengaluru",
            "locations": ["Bengaluru, Karnataka, India"],
            "posted": "2026-10-14",
            "url": "https://amazon.jobs/en/jobs/123",
        }
        msg = telegram.format_job_message(job, is_reopened=False)
        self.assertIn("NEW INTERNSHIP OPENING", msg)
        self.assertIn("Amazon", msg)
        self.assertIn("Software Development Engineer Intern", msg)
        self.assertIn("https://amazon.jobs/en/jobs/123", msg)

    def test_format_job_message_reopened(self):
        job = {
            "company": "Google",
            "title": "Hardware Intern",
            "category": "Hardware/Silicon",
            "city_tag": "Hyderabad",
            "url": "https://careers.google.com/jobs/456",
        }
        msg = telegram.format_job_message(job, is_reopened=True)
        self.assertIn("INTERNSHIP REOPENED", msg)
        self.assertIn("Google", msg)
        self.assertIn("Hardware/Silicon", msg)

    def test_notify_updates_no_env(self):
        # Should gracefully return 0 when no token or chat_id is provided
        sent = telegram.notify_updates(added=[{"company": "Google"}], token="", chat_id="")
        self.assertEqual(sent, 0)


if __name__ == "__main__":
    unittest.main()
