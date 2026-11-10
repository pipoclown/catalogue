"""The continuous integration pipeline, runnable on any laptop.

    python pipeline.py
    python pipeline.py --from build

Runs the stages in pipeline.json in order. A stage passes when its command
exits 0; the first stage that fails stops the pipeline, and so does the
pipeline's own exit code. The CI server runs this same file, so a green run
here predicts a green run there.
"""

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent


def load_stages():
    with open(ROOT / "pipeline.json", encoding="utf-8") as f:
        return json.load(f)["stages"]


def run(stage):
    command = shlex.split(stage["run"])
    if command[0] == "python":
        command[0] = sys.executable
    started = time.monotonic()
    code = subprocess.run(command, cwd=ROOT).returncode
    return code, time.monotonic() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="start", help="skip the stages before this one")
    args = parser.parse_args()
    stages = load_stages()
    names = [s["name"] for s in stages]
    if args.start:
        stages = stages[names.index(args.start):]
    results = []
    for stage in stages:
        print(f"\n>>> stage {stage['name']}: {stage['run']}", flush=True)
        code, seconds = run(stage)
        results.append((stage["name"], code, seconds))
        if code != 0:
            break
    print("\n--- pipeline")
    for name, code, seconds in results:
        print(f"{name:10} {'passed' if code == 0 else 'FAILED':8} {seconds:5.1f}s")
    for name in names[names.index(results[-1][0]) + 1:]:
        print(f"{name:10} skipped")
    ok = all(code == 0 for _, code, _ in results) and len(results) == len(stages)
    print(f"PIPELINE {'GREEN' if ok else 'RED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
