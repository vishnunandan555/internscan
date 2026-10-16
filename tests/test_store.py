"""Unit tests for store persistence, atomic writes, corruption recovery, and diff merging."""
import os
import tempfile
import unittest
from scraper import store
from scraper.models import Job


class TestStore(unittest.TestCase):
    def test_atomic_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "jobs.json")
            orig_data = store.DATA_PATH
            orig_tmp = store._TMP_PATH
            try:
                store.DATA_PATH = test_path
                store._TMP_PATH = test_path + ".tmp"

                state = store.load()
                self.assertEqual(state["jobs"], {})

                state["jobs"]["sample:1"] = {"company": "Sample", "active": True}
                store.save(state)

                self.assertTrue(os.path.exists(test_path))
                self.assertFalse(os.path.exists(store._TMP_PATH))

                loaded = store.load()
                self.assertIn("sample:1", loaded["jobs"])
                self.assertTrue(loaded["jobs"]["sample:1"]["active"])
            finally:
                store.DATA_PATH = orig_data
                store._TMP_PATH = orig_tmp

    def test_corruption_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "jobs.json")
            orig_data = store.DATA_PATH
            orig_tmp = store._TMP_PATH
            try:
                store.DATA_PATH = test_path
                store._TMP_PATH = test_path + ".tmp"

                with open(test_path, "w") as fh:
                    fh.write("{broken-json...")

                loaded = store.load()
                self.assertEqual(loaded["jobs"], {})

                # Verify backup file created
                corrupt_backups = [f for f in os.listdir(tmpdir) if ".corrupt." in f]
                self.assertEqual(len(corrupt_backups), 1)
            finally:
                store.DATA_PATH = orig_data
                store._TMP_PATH = orig_tmp

    def test_merge_lifecycle_add_close_reopen(self):
        state = {
            "updated_at": None,
            "jobs": {
                "google:old1": {"company": "Google", "external_id": "old1", "active": True},
                "meta:m1": {"company": "Meta", "external_id": "m1", "active": False},
            },
        }

        # Google has a new job and old1 disappeared
        new_google_job = Job(company="Google", external_id="new1", title="SWE Intern", url="https://google.com/new1")
        # Meta reopens m1
        reopened_meta_job = Job(company="Meta", external_id="m1", title="AI Intern", url="https://meta.com/m1")

        succeeded = {"Google", "Meta"}
        added, closed, reopened = store.merge(state, [new_google_job, reopened_meta_job], succeeded)

        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["external_id"], "new1")

        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0]["external_id"], "old1")
        self.assertFalse(state["jobs"]["google:old1"]["active"])

        self.assertEqual(len(reopened), 1)
        self.assertEqual(reopened[0]["external_id"], "m1")
        self.assertTrue(state["jobs"]["meta:m1"]["active"])

    def test_country_partitioned_load_and_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_data_dir = store.DATA_DIR
            orig_data_path = store.DATA_PATH
            orig_tmp_path = store._TMP_PATH
            try:
                store.DATA_DIR = tmpdir
                store.DATA_PATH = os.path.join(tmpdir, "jobs.json")
                store._TMP_PATH = os.path.join(tmpdir, "jobs.json.tmp")

                state = {
                    "updated_at": None,
                    "jobs": {
                        "google:in1": {"company": "Google", "country": "in", "active": True},
                        "meta:us1": {"company": "Meta", "country": "us", "active": True},
                    },
                }
                store.save(state)

                # Verify main file
                self.assertTrue(os.path.exists(store.DATA_PATH))
                # Verify partition files
                in_path = os.path.join(tmpdir, "in", "jobs.json")
                us_path = os.path.join(tmpdir, "us", "jobs.json")
                self.assertTrue(os.path.exists(in_path))
                self.assertTrue(os.path.exists(us_path))

                # Load with country filter
                in_loaded = store.load(country="in")
                self.assertIn("google:in1", in_loaded["jobs"])
                self.assertNotIn("meta:us1", in_loaded["jobs"])

                us_loaded = store.load(country="us")
                self.assertIn("meta:us1", us_loaded["jobs"])
                self.assertNotIn("google:in1", us_loaded["jobs"])
            finally:
                store.DATA_DIR = orig_data_dir
                store.DATA_PATH = orig_data_path
                store._TMP_PATH = orig_tmp_path

    def test_typing_annotations_evaluation(self):
        import typing
        hints = typing.get_type_hints(store.load)
        self.assertIn("country", hints)
        self.assertIn("return", hints)


if __name__ == "__main__":
    unittest.main()

