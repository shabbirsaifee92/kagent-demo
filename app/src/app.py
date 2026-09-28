#!/usr/bin/env python3
"""demo-app - a small HTTP service with a minimal web UI."""
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = "1.5.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-app")

BUTTON_COLOR = "#22c55e"
BUTTON_LABEL = "Check status"


def connect_cache(url):
    """Resolve the configured cache backend. Absent configuration is not fatal."""
    scheme = url.split("://", 1)[0] if "://" in url else ""
    if not url:
        log.warning("CACHE_URL is not set; running without a cache")
        return None
    if scheme not in ("redis", "memcached"):
        raise ValueError(f"unsupported cache backend: {scheme!r}")
    log.info("cache backend resolved scheme=%s", scheme)
    return scheme


def render_page(version, cache):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>demo-app</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 3rem auto; max-width: 34rem; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; }}
    .status {{ color: #6b7280; font-size: 0.9rem; }}
    button {{
      background: {BUTTON_COLOR};
      color: #fff; border: 0; border-radius: 8px;
      padding: 0.6rem 1.1rem; font-size: 1rem; cursor: pointer;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>demo-app</h1>
    <p class="status">version {version} &middot; cache: {cache or "disabled"}</p>
    <button id="refresh" onclick="location.reload()">{BUTTON_LABEL}</button>
  </div>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    cache = None

    def _send(self, body, content_type):
        payload = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/healthz":
            self._send(json.dumps({"status": "ok", "version": VERSION}), "application/json")
        elif self.path == "/api/status":
            self._send(
                json.dumps({"service": "demo-app", "version": VERSION, "cache": self.cache}),
                "application/json",
            )
        else:
            self._send(render_page(VERSION, self.cache), "text/html; charset=utf-8")

    def log_message(self, fmt, *args):
        log.info("%s - %s", self.address_string(), fmt % args)


def main():
    port = int(os.environ.get("PORT", "8080"))
    Handler.cache = connect_cache(os.environ.get("CACHE_URL", ""))
    log.info("starting demo-app version=%s port=%d", VERSION, port)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
