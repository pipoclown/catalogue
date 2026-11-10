import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import make_server


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0, log_requests=False)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_health(self):
        self.assertEqual(self.get("/health"), (200, {"status": "ok"}))

    def test_version_names_the_environment(self):
        status, body = self.get("/version")
        self.assertEqual(status, 200)
        self.assertEqual(body["environment"], "development")

    def test_one_course(self):
        status, body = self.get("/courses/DEV100")
        self.assertEqual(status, 200)
        self.assertEqual(body["days"], 2)

    def test_courses_by_category(self):
        status, body = self.get("/courses?category=data")
        self.assertEqual(status, 200)
        self.assertEqual([c["code"] for c in body], ["JSN200"])

    def test_unknown_category_is_an_empty_list(self):
        self.assertEqual(self.get("/courses?category=cooking"), (200, []))

    def test_category_ignores_case(self):
        status, body = self.get("/courses?category=DevOps")
        self.assertEqual(len(body), 4)

    def test_unknown_course_is_404(self):
        status, _ = self.get("/courses/XXX999")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
