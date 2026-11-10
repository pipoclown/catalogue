# Catalogue

The SpiralTrain course catalogue service: a small HTTP service that answers
with JSON. Python 3.10 or later, standard library only.

| Command | Does |
|---|---|
| `python -m app.server` | Starts the service on http://localhost:8000 |
| `python get.py courses` | Asks the running service for a page |
| `python -m unittest` | Runs every test in `tests/` |
| `python -m metrics.dora metrics/releases.csv` | The four DORA metrics of a release log |
| `python build.py` | Compiles, tests and packages into `dist/` |
| `python lint.py` | Checks the house rules of every Python file |
| `python smoke.py` | Starts the built package and asks it two questions |
| `python pipeline.py` | Runs the whole pipeline: lint, build, smoke |

| Page | Answers |
|---|---|
| `/health` | `{"status": "ok"}` while the service runs |
| `/version` | The version and the name of the environment |
| `/courses` | Every course in the catalogue, sorted by course code; `?category=<name>` keeps one category |
| `/courses/<code>` | One course, or 404 |

The courses live in `app/courses.json`.

| Setting | Means | Default |
|---|---|---|
| `CATALOGUE_PORT` | The port to listen on | `8000` |
| `CATALOGUE_ENV` | The name of this environment | `development` |
| `CATALOGUE_DATA` | The courses file to serve | `app/courses.json` |
