"""One command from source to a deployable package.

    python build.py

Three steps, in order, and the first one that fails stops the build:

    compile   every .py file must at least compile
    test      every test in tests/ must pass
    package   app/ and get.py go into dist/catalogue-<version>.zip
"""

import compileall
import json
import re
import subprocess
import sys
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from app import VERSION

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PACKAGED = ["app", "get.py", "README.md"]
SKIP = re.compile(r"[\\/](dist|\.git|\.venv)[\\/]")


def compile_step():
    return compileall.compile_dir(ROOT, quiet=1, rx=SKIP)


def test_step():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    return result.wasSuccessful()


def commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def package_step():
    DIST.mkdir(exist_ok=True)
    target = DIST / f"catalogue-{VERSION}.zip"
    info = {"version": VERSION, "commit": commit(),
            "built": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name in PACKAGED:
            path = ROOT / name
            files = [path] if path.is_file() else sorted(path.rglob("*"))
            for f in files:
                if f.is_file() and "__pycache__" not in f.parts:
                    z.write(f, f.relative_to(ROOT).as_posix())
        z.writestr("build-info.json", json.dumps(info, indent=2))
    print(f"  {target.relative_to(ROOT).as_posix()}  ({target.stat().st_size} bytes)")
    return True


STEPS = [("compile", compile_step), ("test", test_step), ("package", package_step)]


def main():
    for name, step in STEPS:
        print(f"== {name}", flush=True)
        if not step():
            print(f"BUILD FAILED at step '{name}'")
            return 1
    print(f"BUILD OK  catalogue {VERSION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
