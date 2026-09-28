import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSION = "1.5.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("demo-app")


def connect_cache(url):
    """Resolve the configured cache backend.
    
    If url is empty, logs a warning and returns None (no caching).
    Otherwise validates that the URL has a supported scheme (redis or memcached).
    """
    if not url or not url.strip():
        log.warning("cache backend not configured, running without caching")
        return None
    
    scheme = url.split("://", 1)[0] if "://" in url else ""
    if scheme not in ("redis", "memcached"):
        raise ValueError(f"unsupported cache backend: {scheme!r}")
    log.info("cache backend resolved scheme=%s", scheme)
    return scheme


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        log.info(fmt, *args)


def main():
    port = int(os.environ.get("PORT", "8080"))
    log.info("starting demo-app version=%s port=%d", VERSION, port)
    connect_cache(os.environ.get("CACHE_URL", ""))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
