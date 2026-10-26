"""Local server for the site and its tools. Serves the folder like `python3 -m http.server`, and lets
tools/pages.html and tools/tag.html save into it (Chrome will not let a page pick a folder inside WSL).

    python3 scripts/serve.py [port]        # default 8026, this machine only; then open http://localhost:8026/

Saving is a PUT / DELETE that must come from this server's own pages (Origin + the X-Skimart-Save header, which
another site cannot send without a preflight this server never grants), and only onto the files the tools write.
SKIMART_ROOT=<dir> serves another folder (tests/serve_test.py uses a copy).
"""
import http.server
import os
import re
import sys
import urllib.parse

ROOT = os.path.abspath(os.environ.get('SKIMART_ROOT') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8026
WRITABLE = re.compile(r'(index\.html|assets/home/labels\.js|data/(photos|refs)\.json|assets/home/(t/)?[\w-]+\.jpg|assets/archive/t/[\w-]+\.jpg)')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path == '/__can-save':  # the tools ask before choosing how to save
            self.send_response(204); self.end_headers(); return
        super().do_GET()

    def target(self):
        """The file a save may touch, or None after answering 403."""
        origin = self.headers.get('Origin')
        if self.headers.get('X-Skimart-Save') != '1' or origin not in (None, f'http://localhost:{PORT}', f'http://127.0.0.1:{PORT}'):
            self.send_error(403, 'saves only come from this server\'s own pages'); return None
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path).lstrip('/')
        if not WRITABLE.fullmatch(path):
            self.send_error(403, 'not a file the tools write'); return None
        return os.path.join(ROOT, path)

    def do_PUT(self):
        p = self.target()
        if not p: return
        data = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p + '.part', 'wb') as f: f.write(data)
        os.replace(p + '.part', p)  # a reader never sees half a file
        self.send_response(204); self.end_headers()

    def do_DELETE(self):
        p = self.target()
        if not p: return
        if os.path.exists(p): os.remove(p)
        self.send_response(204); self.end_headers()


if __name__ == '__main__':
    print(f'serving {ROOT} at http://localhost:{PORT}/  (page editor: /tools/pages.html, tagging: /tools/tag.html)')
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
