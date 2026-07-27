import sys
import os
import json
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from send_daily import run_digest


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get("Authorization", "")
        cron_secret = os.getenv("CRON_SECRET", "")
        if cron_secret and auth_header != f"Bearer {cron_secret}":
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Unauthorized"}).encode("utf-8"))
            return

        try:
            result = run_digest()
            status = 200 if result["success"] else 500
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode("utf-8"))

    def log_message(self, format, *args):
        return
