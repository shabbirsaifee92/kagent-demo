#!/usr/bin/env python3
"""demo-app - a minimal HTTP service used by the kagent POC."""
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = "1.4.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-app")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            body = {"status": "ok", "version": VERSION}
        else:
            body = {"service": "demo-app", "version": VERSION}
        payload = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        log.info("%s - %s", self.address_string(), fmt % args)


def main():
    port = int(os.environ.get("PORT", "8080"))
    log.info("starting demo-app version=%s port=%d", VERSION, port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
