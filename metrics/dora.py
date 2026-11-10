"""The four DORA metrics, computed from a log of releases.

    python -m metrics.dora metrics/releases.csv

Each row of the log is one release: when its first commit was made, when it
reached production, whether it failed there and, if it did, when service was
restored.
"""

import csv
import statistics
import sys
from datetime import datetime

FORMAT = "%Y-%m-%d %H:%M"


def read_releases(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["committed"] = datetime.strptime(row["committed"], FORMAT)
        row["deployed"] = datetime.strptime(row["deployed"], FORMAT)
        row["failed"] = row["failed"] == "yes"
        row["restored"] = datetime.strptime(row["restored"], FORMAT) if row["restored"] else None
    return rows


def hours(delta):
    return delta.total_seconds() / 3600


def deployment_frequency(releases):
    """Deployments per week, over the period from the first to the last one."""
    first = min(r["deployed"] for r in releases)
    last = max(r["deployed"] for r in releases)
    weeks = max(hours(last - first) / (24 * 7), 1)
    return len(releases) / weeks


def lead_time(releases):
    """Median hours from first commit to running in production."""
    return statistics.median(hours(r["deployed"] - r["committed"]) for r in releases)


def change_failure_rate(releases):
    """Percentage of deployments that caused a failure in production."""
    return 100 * sum(r["failed"] for r in releases) / len(releases)


def time_to_restore(releases):
    """Mean hours from a failed deployment to restored service, or None."""
    failed = [hours(r["restored"] - r["deployed"]) for r in releases if r["failed"]]
    return statistics.mean(failed) if failed else None


# The lower bound of each band, best band first. Frequency: higher is better.
FREQUENCY_BANDS = [("elite", 7), ("high", 1), ("medium", 0.25)]
# Upper bounds, best band first. Lead time, failures, restore: lower is better.
# A lead time or restore below the bound is in the band; a failure rate at most it.
LEAD_TIME_BANDS = [("elite", 24), ("high", 168), ("medium", 720)]
FAILURE_BANDS = [("elite", 5), ("high", 10), ("medium", 15)]
RESTORE_BANDS = [("elite", 1), ("high", 24), ("medium", 168)]


def band_at_least(value, bands):
    return next((name for name, bound in bands if value >= bound), "low")


def band_below(value, bands):
    return next((name for name, bound in bands if value < bound), "low")


def band_at_most(value, bands):
    return next((name for name, bound in bands if value <= bound), "low")


def classify(releases):
    """The performance band of each metric: elite, high, medium or low."""
    restore = time_to_restore(releases)
    return {
        "deployment frequency": band_at_least(deployment_frequency(releases), FREQUENCY_BANDS),
        "lead time": band_below(lead_time(releases), LEAD_TIME_BANDS),
        "change failure rate": band_at_most(change_failure_rate(releases), FAILURE_BANDS),
        "time to restore": "elite" if restore is None else band_below(restore, RESTORE_BANDS),
    }


def main(path):
    releases = read_releases(path)
    restore = time_to_restore(releases)
    bands = classify(releases)
    print(f"Releases               {len(releases)}")
    print(f"Deployment frequency   {deployment_frequency(releases):.2f} per week"
          f"   {bands['deployment frequency']}")
    print(f"Lead time for changes  {lead_time(releases):.1f} hours (median)"
          f"   {bands['lead time']}")
    print(f"Change failure rate    {change_failure_rate(releases):.0f} %"
          f"   {bands['change failure rate']}")
    print(f"Time to restore        {'-' if restore is None else f'{restore:.1f} hours'} (mean)"
          f"   {bands['time to restore']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "metrics/releases.csv")
