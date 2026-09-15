#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "site"
PREFIX = "/singlink-field-notes"


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = path[len(PREFIX) :] or "/"
        return str(ROOT / path.lstrip("/"))


if __name__ == "__main__":
    print("http://127.0.0.1:8765/singlink-field-notes/")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
