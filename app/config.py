"""Settings come from the environment, with defaults that suit a laptop.

    CATALOGUE_PORT   the port to listen on            8000
    CATALOGUE_ENV    the name of this environment     development
    CATALOGUE_DATA   the courses file to serve        app/courses.json
"""

import os

from app.catalogue import DATA


def settings(environ=None):
    environ = os.environ if environ is None else environ
    return {
        "port": int(environ.get("CATALOGUE_PORT", "8000")),
        "env": environ.get("CATALOGUE_ENV", "development"),
        "data": environ.get("CATALOGUE_DATA", str(DATA)),
    }
