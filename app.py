import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent import analyze_document, attach_reviews


ROOT = Path(__file__).resolve().parent
SAMPLE = json.loads((ROOT / "sample_data" / "synthetic_filing.json").read_text(encoding="utf-8"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "static"), **kwargs)

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/api/health":
            return self._json({"status": "ok"})
        if self.path == "/api/sample":
            return self._json(SAMPLE)
        return super().do_GET()

    def do_POST(self):
        try:
            payload = self._body()
            if self.path == "/api/analyze":
                result = analyze_document(
                    payload.get("company_id", "SYN-DEMO"),
                    payload.get("company_name", "합성기업"),
                    payload.get("text", ""),
                )
                return self._json(result)
            if self.path == "/api/review":
                return self._json(attach_reviews(payload["result"], payload.get("reviews", [])))
            return self._json({"error": "not found"}, 404)
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            return self._json({"error": str(error)}, 400)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8010), Handler)
    print("Demo running at http://127.0.0.1:8010")
    server.serve_forever()

