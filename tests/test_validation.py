import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from music_database.validation import is_valid_email


class EmailValidationTests(unittest.TestCase):
    def test_accepts_common_email_address(self):
        self.assertTrue(is_valid_email("listener@example.com"))

    def test_rejects_incomplete_address(self):
        self.assertFalse(is_valid_email("listener@example"))

    def test_rejects_empty_address(self):
        self.assertFalse(is_valid_email(""))


if __name__ == "__main__":
    unittest.main()
