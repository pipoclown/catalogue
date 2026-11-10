"""Ask the running catalogue for a page and print the answer.

    python get.py courses
    python get.py courses/DEV100 --port 8001

The path goes without its leading slash: Git Bash turns /courses into
C:/Program Files/Git/courses before Python ever sees it.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="health")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    url = f"http://127.0.0.1:{args.port}/{args.path.lstrip('/')}"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read()
    except OSError as e:
        print(f"No answer from {url}: {getattr(e, 'reason', e)}")
        return 2
    print(status)
    try:
        print(json.dumps(json.loads(body), indent=2))
    except ValueError:
        print(body.decode("utf-8"))
    return 0 if status < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
