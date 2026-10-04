import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from music_database.config import DatabaseSettings


class DatabaseSettingsTests(unittest.TestCase):
    def test_reads_complete_configuration(self):
        settings = DatabaseSettings.from_environment(
            {
                "DB_NAME": "music_database",
                "DB_USER": "postgres",
                "DB_PASSWORD": "local-password",
                "DB_HOST": "localhost",
                "DB_PORT": "5432",
            }
        )

        self.assertEqual(settings.name, "music_database")
        self.assertEqual(settings.port, 5432)

    def test_rejects_missing_password(self):
        with self.assertRaisesRegex(ValueError, "DB_PASSWORD"):
            DatabaseSettings.from_environment(
                {
                    "DB_NAME": "music_database",
                    "DB_USER": "postgres",
                    "DB_HOST": "localhost",
                    "DB_PORT": "5432",
                }
            )

    def test_rejects_invalid_port(self):
        with self.assertRaisesRegex(ValueError, "DB_PORT"):
            DatabaseSettings.from_environment(
                {
                    "DB_NAME": "music_database",
                    "DB_USER": "postgres",
                    "DB_PASSWORD": "local-password",
                    "DB_HOST": "localhost",
                    "DB_PORT": "invalid",
                }
            )


if __name__ == "__main__":
    unittest.main()
