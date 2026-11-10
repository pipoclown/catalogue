import unittest

from app.catalogue import Catalogue


class CatalogueTest(unittest.TestCase):
    def setUp(self):
        self.catalogue = Catalogue.load()

    def test_every_course_has_a_title(self):
        for course in self.catalogue.all():
            self.assertTrue(course["title"], course["code"])

    def test_courses_come_sorted_by_code(self):
        codes = [c["code"] for c in self.catalogue.all()]
        self.assertEqual(codes, sorted(codes))

    def test_find_ignores_case(self):
        self.assertEqual(self.catalogue.find("dev100")["title"], "DevOps Fundamentals")

    def test_puppet_course_is_listed(self):
        self.assertEqual(self.catalogue.find("DEV300")["days"], 3)

    def test_in_category_keeps_only_that_category(self):
        codes = [c["code"] for c in self.catalogue.in_category("containers")]
        self.assertEqual(codes, ["DEV500", "TLG550"])

    def test_find_unknown_code_gives_none(self):
        self.assertIsNone(self.catalogue.find("XXX999"))


if __name__ == "__main__":
    unittest.main()
