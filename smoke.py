"""Start the packaged service and ask it two questions, the way production would.

    python smoke.py
    python smoke.py dist/catalogue-1.1.0.zip

Unpacks the package into a temporary folder, starts it on a free port, and
checks that /health answers ok and /version reports the version that was
built. Tests the artefact, not the source tree.
"""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from app import VERSION

ROOT = Path(__file__).parent


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=2) as r:
        return json.loads(r.read())


def wait_for_health(port, seconds=10, proc=None):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if proc is not None and proc.poll() is not None:
            return None
        try:
            return get(port, "/health")
        except OSError:
            time.sleep(0.2)
    return None


def check_folder(folder, expected_version, env="smoke"):
    """Start the service unpacked in folder; return a list of failures."""
    port = free_port()
    environ = dict(os.environ, CATALOGUE_PORT=str(port), CATALOGUE_ENV=env)
    proc = subprocess.Popen([sys.executable, "-m", "app.server"], cwd=folder, env=environ,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    failures = []
    try:
        health = wait_for_health(port, proc=proc)
        if health is None and proc.poll() is not None:
            failures = ["the service stopped before it answered /health"]
        elif health is None:
            failures = ["no answer on /health within 10 seconds"]
        elif health != {"status": "ok"}:
            failures = [f"/health answered {health}"]
        else:
            version = get(port, "/version")["version"]
            if version != expected_version:
                failures = [f"/version answered {version}, expected {expected_version}"]
    finally:
        died = proc.poll() is not None
        proc.terminate()
        _, errors = proc.communicate(timeout=10)
    if died and errors.strip():
        failures.append(f"the service said: {errors.strip().splitlines()[-1]}")
    return failures


def smoke(package, expected_version, env="smoke"):
    """Run the package in a temporary folder; return a list of failures."""
    with tempfile.TemporaryDirectory() as folder:
        with zipfile.ZipFile(package) as z:
            z.extractall(folder)
        return check_folder(folder, expected_version, env)


def main():
    package = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / f"catalogue-{VERSION}.zip"
    if not package.exists():
        print(f"SMOKE FAILED  no package at {package.as_posix()} - run python build.py first")
        return 1
    failures = smoke(package, VERSION)
    for failure in failures:
        print(f"  {failure}")
    print(f"SMOKE {'FAILED' if failures else 'OK'}  {package.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
