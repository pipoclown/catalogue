"""The catalogue itself: the courses, and the ways to look them up."""

import json
from pathlib import Path

DATA = Path(__file__).with_name("courses.json")


class Catalogue:
    def __init__(self, courses):
        self._courses = {c["code"]: c for c in courses}

    @classmethod
    def load(cls, path=DATA):
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def all(self):
        return sorted(self._courses.values(), key=lambda c: c["code"])

    def in_category(self, category):
        return [c for c in self.all() if c["category"] == category.lower()]

    def find(self, code):
        return self._courses.get(code.upper())
