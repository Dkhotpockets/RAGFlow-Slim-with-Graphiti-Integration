import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><head><title>Mock</title></head><body>OK</body></html>")
        elif self.path == '/robots.txt':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"User-agent: *\nDisallow:")
        else:
            self.send_response(404)
            self.end_headers()

class MockServer:
    def __init__(self, host='127.0.0.1', port=8000):
        self.server = HTTPServer((host, port), SimpleHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True

    def start(self):
        self.thread.start()
        time.sleep(0.1)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
