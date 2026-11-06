"""Dependency-free local application server. Not a public multi-tenant service."""
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from engine import solve
ROOT = Path(__file__).parent
class Handler(BaseHTTPRequestHandler):
    def send(self, data, status=200, content_type="application/json"):
        raw = json.dumps(data, allow_nan=False).encode() if content_type == "application/json" else data
        self.send_response(status)
        for key, value in {"Content-Type":content_type, "Content-Length":str(len(raw)), "Cache-Control":"no-store", "X-Content-Type-Options":"nosniff", "Content-Security-Policy":"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"}.items():
            self.send_header(key, value)
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/sample":
            self.send(json.loads((ROOT / "examples/scenario.json").read_text())); return
        if path == "/api/health": self.send({"status":"ok"}); return
        allowed={"/":"index.html", "/app.js":"app.js", "/style.css":"style.css"}
        if path not in allowed: self.send({"error":"Not found"},404); return
        file=ROOT / "web" / allowed[path]
        self.send(file.read_bytes(), content_type=mimetypes.guess_type(file.name)[0] or "application/octet-stream")
    def do_POST(self):
        if urlsplit(self.path).path != "/api/solve": self.send({"error":"Not found"},404); return
        origin=self.headers.get("Origin")
        if origin and urlsplit(origin).netloc != self.headers.get("Host"):
            self.send({"error":"Cross-origin request rejected"},403); return
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0 < length <= 200000: raise ValueError("Request must be between 1 and 200,000 bytes")
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise ValueError("Scenario must be a JSON object")
            result=solve(body)
            self.send(result)
        except (ValueError,TypeError,KeyError,IndexError,OverflowError) as exc:
            self.send({"error":str(exc)},400)
        except Exception:
            import traceback; traceback.print_exc()
            self.send({"error":"Unexpected solver error"},500)
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=4313)
    args=parser.parse_args()
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    print(f"Open http://127.0.0.1:{args.port} — Ctrl+C to stop",flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
