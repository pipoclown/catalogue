import unittest
from pathlib import Path

from metrics import dora

LOG = Path(__file__).parent.parent / "metrics" / "releases.csv"


class DoraTest(unittest.TestCase):
    def setUp(self):
        self.releases = dora.read_releases(LOG)

    def test_five_releases_in_the_log(self):
        self.assertEqual(len(self.releases), 5)

    def test_deployment_frequency_is_per_week(self):
        self.assertAlmostEqual(dora.deployment_frequency(self.releases), 0.15, places=2)

    def test_lead_time_is_the_median_in_hours(self):
        self.assertAlmostEqual(dora.lead_time(self.releases), 1356.0, places=1)

    def test_three_of_five_failed(self):
        self.assertEqual(dora.change_failure_rate(self.releases), 60)

    def test_time_to_restore_is_the_mean_of_the_failures(self):
        self.assertAlmostEqual(dora.time_to_restore(self.releases), 38.17, places=2)

    def test_no_failures_means_no_time_to_restore(self):
        self.assertIsNone(dora.time_to_restore(self.releases[1:2]))


if __name__ == "__main__":
    unittest.main()
