"""The HTTP front of the catalogue: JSON in, JSON out, standard library only.

    python -m app.server
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from app import VERSION
from app.catalogue import Catalogue
from app.config import settings


class Handler(BaseHTTPRequestHandler):
    catalogue = None
    env = "development"
    log_requests = True

    def do_GET(self):
        path, _, query = self.path.partition("?")
        params = parse_qs(query)
        if path == "/health":
            self.send_json(200, {"status": "ok"})
        elif path == "/version":
            self.send_json(200, {"version": VERSION, "environment": self.env})
        elif path == "/courses" and "category" in params:
            self.send_json(200, self.catalogue.in_category(params["category"][0]))
        elif path == "/courses":
            self.send_json(200, self.catalogue.all())
        elif path.startswith("/courses/"):
            course = self.catalogue.find(path[len("/courses/"):])
            if course:
                self.send_json(200, course)
            else:
                self.send_json(404, {"error": "no such course"})
        else:
            self.send_json(404, {"error": "no such page"})

    def send_json(self, status, body):
        data = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        if self.log_requests:
            super().log_message(format, *args)


class Server(ThreadingHTTPServer):
    # On Windows, address reuse lets a second copy bind the same port silently
    allow_reuse_address = sys.platform != "win32"


def make_server(port=8000, catalogue=None, env="development", log_requests=True):
    Handler.catalogue = catalogue or Catalogue.load()
    Handler.env = env
    Handler.log_requests = log_requests
    return Server(("127.0.0.1", port), Handler)


def main():
    config = settings()
    server = make_server(config["port"], Catalogue.load(config["data"]), config["env"])
    print(f"Catalogue {VERSION} ({config['env']}) listening on http://localhost:{config['port']}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped")


if __name__ == "__main__":
    main()
