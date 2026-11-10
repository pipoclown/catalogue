import unittest

from app.config import settings


class ConfigTest(unittest.TestCase):
    def test_defaults_suit_a_laptop(self):
        config = settings({})
        self.assertEqual(config["port"], 8000)
        self.assertEqual(config["env"], "development")

    def test_the_environment_wins(self):
        config = settings({"CATALOGUE_PORT": "9090", "CATALOGUE_ENV": "staging"})
        self.assertEqual(config["port"], 9090)
        self.assertEqual(config["env"], "staging")

    def test_a_port_must_be_a_number(self):
        with self.assertRaises(ValueError):
            settings({"CATALOGUE_PORT": "eighty"})


if __name__ == "__main__":
    unittest.main()
