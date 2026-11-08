"""Usage: serve.py --repo <path> --port <n>"""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<!doctype html><title>veri dashboard</title>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    HTTPServer(("", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
