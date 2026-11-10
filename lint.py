"""House rules for every Python file, checked by a machine instead of a reviewer.

    python lint.py

Prints one line per problem as file:line: message, and exits 1 when there is
at least one. The rules:

    long-line       a line longer than 100 characters
    trailing-space  whitespace at the end of a line
    tab             a tab used for indentation
    breakpoint      a call to the debugger left behind
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SKIP = {"dist", ".git", ".venv", "__pycache__", "envs"}
MAX_LINE = 100


def problems(path):
    text = path.read_text(encoding="utf-8")
    for n, line in enumerate(text.splitlines(), 1):
        if len(line) > MAX_LINE:
            yield n, f"long-line ({len(line)} > {MAX_LINE})"
        if line != line.rstrip():
            yield n, "trailing-space"
        if line.startswith("\t"):
            yield n, "tab"
        if re.search(r"\bbreakpoint\(\)", line) and not line.lstrip().startswith("#"):
            yield n, "breakpoint"


def main():
    files = [p for p in sorted(ROOT.rglob("*.py")) if not SKIP & set(p.relative_to(ROOT).parts)]
    count = 0
    for path in files:
        for n, message in problems(path):
            print(f"{path.relative_to(ROOT).as_posix()}:{n}: {message}")
            count += 1
    print(f"lint: {len(files)} files, {count} problems")
    return 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
