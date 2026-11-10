import unittest
from pathlib import Path

from metrics import dora

HERE = Path(__file__).parent.parent / "metrics"


class BandsTest(unittest.TestCase):
    def bands(self, name):
        return dora.classify(dora.read_releases(HERE / name))

    def test_the_old_way_is_low_almost_everywhere(self):
        self.assertEqual(self.bands("releases.csv"), {
            "deployment frequency": "low",
            "lead time": "low",
            "change failure rate": "low",
            "time to restore": "medium",
        })

    def test_the_devops_way(self):
        self.assertEqual(self.bands("releases-devops.csv"), {
            "deployment frequency": "high",
            "lead time": "elite",
            "change failure rate": "low",
            "time to restore": "elite",
        })

    def test_a_boundary_belongs_to_the_better_band(self):
        self.assertEqual(dora.band_at_least(7, dora.FREQUENCY_BANDS), "elite")
        self.assertEqual(dora.band_below(23.9, dora.LEAD_TIME_BANDS), "elite")
        self.assertEqual(dora.band_below(24, dora.LEAD_TIME_BANDS), "high")


if __name__ == "__main__":
    unittest.main()
