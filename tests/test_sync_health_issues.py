"""Unit tests for scripts/sync_health_issues.py."""
import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch

import scripts.sync_health_issues as syncer


class TestSyncHealthIssues(unittest.TestCase):
    def test_format_issue_body(self):
        failed = {
            "Accenture": "HTTP 429",
            "Adobe": "HTTP 429",
        }
        body = syncer.format_issue_body(failed)
        self.assertIn("Automated Scraper Health Report", body)
        self.assertIn("- **Accenture**: `HTTP 429`", body)
        self.assertIn("- **Adobe**: `HTTP 429`", body)
        self.assertIn("preserved in `data/jobs.json`", body)

    @patch("scripts.sync_health_issues.HEALTH_FILE", "/non/existent/path/health.json")
    def test_sync_no_health_file(self):
        ret = syncer.sync()
        self.assertEqual(ret, 0)

    @patch("scripts.sync_health_issues.run_gh")
    def test_sync_all_healthy_closes_open_issues(self, mock_run_gh):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            json.dump({"failed": {}, "succeeded": ["Google"]}, tf)
            tf_path = tf.name

        try:
            with patch("scripts.sync_health_issues.HEALTH_FILE", tf_path):
                with patch("scripts.sync_health_issues.get_open_health_issues", return_value=[{"number": 11, "title": "Old"}]):
                    ret = syncer.sync()
                    self.assertEqual(ret, 0)
                    mock_run_gh.assert_called_with(
                        "issue",
                        "close",
                        "11",
                        "--comment",
                        "🎉 All scrapers passed successfully in the latest scrape run. Auto-closing.",
                        "--reason",
                        "completed",
                    )
        finally:
            os.remove(tf_path)

    @patch("scripts.sync_health_issues.run_gh")
    def test_sync_deduplicates_and_updates_open_issues(self, mock_run_gh):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            json.dump({"failed": {"Adobe": "HTTP 429"}}, tf)
            tf_path = tf.name

        try:
            with patch("scripts.sync_health_issues.HEALTH_FILE", tf_path):
                open_issues = [
                    {"number": 6, "title": "Old 6"},
                    {"number": 11, "title": "Old 11"},
                    {"number": 10, "title": "Old 10"},
                ]
                with patch("scripts.sync_health_issues.get_open_health_issues", return_value=open_issues):
                    ret = syncer.sync()
                    self.assertEqual(ret, 0)

                    # Should edit primary (#11)
                    edit_calls = [
                        c for c in mock_run_gh.call_args_list
                        if len(c.args) > 1 and c.args[0] == "issue" and c.args[1] == "edit"
                    ]
                    self.assertEqual(len(edit_calls), 1)
                    self.assertEqual(edit_calls[0].args[2], "11")
                    self.assertEqual(edit_calls[0].args[4], syncer.ISSUE_TITLE)

                    # Should close #10 and #6 as superseded
                    close_calls = [
                        c for c in mock_run_gh.call_args_list
                        if len(c.args) > 1 and c.args[0] == "issue" and c.args[1] == "close"
                    ]
                    self.assertEqual(len(close_calls), 2)
                    closed_nums = {c.args[2] for c in close_calls}
                    self.assertEqual(closed_nums, {"10", "6"})
        finally:
            os.remove(tf_path)

    @patch("scripts.sync_health_issues.run_gh")
    def test_sync_creates_issue_when_none_open(self, mock_run_gh):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            json.dump({"failed": {"Adobe": "HTTP 429"}}, tf)
            tf_path = tf.name

        try:
            with patch("scripts.sync_health_issues.HEALTH_FILE", tf_path):
                with patch("scripts.sync_health_issues.get_open_health_issues", return_value=[]):
                    ret = syncer.sync()
                    self.assertEqual(ret, 0)

                    create_calls = [
                        c for c in mock_run_gh.call_args_list
                        if len(c.args) > 1 and c.args[0] == "issue" and c.args[1] == "create"
                    ]
                    self.assertEqual(len(create_calls), 1)
                    self.assertEqual(create_calls[0].args[3], syncer.ISSUE_TITLE)
        finally:
            os.remove(tf_path)


if __name__ == "__main__":
    unittest.main()
