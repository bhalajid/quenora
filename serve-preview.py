#!/usr/bin/env python3
"""Serve the preview the way Vercel does: cleanUrls, and /c and /w answered.
   Run:  python3 serve-preview.py     then open http://127.0.0.1:8800/"""
import http.server, os, json, urllib.parse, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quenora')
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8800

class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, p):
        path = urllib.parse.urlparse(p).path
        f = os.path.join(ROOT, path.lstrip('/'))
        if os.path.isdir(f):
            f = os.path.join(f, 'index.html')
        elif not os.path.exists(f) and os.path.exists(f + '.html'):
            f += '.html'
        return f
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ('/c', '/w') or u.path.startswith('/api/'):
            body = json.dumps({"google": False, "apple": False}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        return super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
    def log_message(self, *a): pass

print('preview  http://127.0.0.1:%d/' % PORT)
print('main     run  python3 serve-preview.py 8801  from ../Quenora  to compare')
http.server.HTTPServer(('127.0.0.1', PORT), H).serve_forever()
