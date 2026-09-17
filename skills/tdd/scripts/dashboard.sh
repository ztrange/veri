#!/usr/bin/env bash
# dashboard.sh — serve the local web dashboard over this repository's veri runs.
#
# Run from a target repo. Binds 127.0.0.1 only, never another interface: a leaf log holds
# the repo's own code and prompts, so the page must not be reachable from the network.
# The server is stdlib-only python3 — no build step, no npm — and the page it serves is
# the `dashboard.html` sitting beside this script, so a foreign repo gets both through
# the installed symlink.
#
# Usage:   dashboard.sh
#          Serves http://127.0.0.1:8765/ until interrupted. Ctrl-C (SIGINT) is how it is
#          meant to be stopped, so that is a clean stop and not a failure.
# Exit:    0 served and was interrupted
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

exec python3 - "$HERE/dashboard.html" 8765 <<'PY'
import http.server
import signal
import sys

# SIGINT back to the handler that raises KeyboardInterrupt, explicitly. A non-interactive
# shell starts a background child with SIGINT ignored, `exec` keeps that disposition, and
# python only installs its own handler where it finds SIG_DFL — so a server launched in
# the background (which is how anything but a human at a terminal launches it) would
# otherwise ignore the very signal it is meant to stop on and hang forever.
signal.signal(signal.SIGINT, signal.default_int_handler)

page = open(sys.argv[1], "rb").read()
port = int(sys.argv[2])


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        else:
            self.send_error(404)

    # One line per request on stderr would race the page's polling into a wall of noise,
    # and nothing reads it: the run's own log is events.jsonl.
    def log_message(self, fmt, *args):
        pass


# HTTPServer rather than a bare TCPServer for its SO_REUSEADDR: without it the port is
# unbindable for a minute after the last client's connection closes, so a restart — or a
# second run of the suite — would fail on a port nothing is listening on.
with http.server.HTTPServer(("127.0.0.1", port), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        # SIGINT is the documented way to stop this, so it is exit 0 — not the 130 a
        # process killed by the signal would otherwise report.
        pass
PY
