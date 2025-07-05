import http.server
import socketserver
import cgi
import os
import urllib.parse
import json

PORT = 8040
UPLOAD_DIR = "/sdcard/upload"

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/files.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("files.html", "rb") as f:
                self.wfile.write(f.read())

        elif self.path.startswith("/files/"):
            filename = urllib.parse.unquote(self.path[len("/files/"):])
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                self.send_response(200)
                self.send_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found.")

        elif self.path == "/list":
            # Return JSON list of files
            try:
                files = os.listdir(UPLOAD_DIR)
            except FileNotFoundError:
                files = []
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode())

        else:
            self.send_error(404, "File not found.")

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        files = form["file"]
        if not isinstance(files, list):
            files = [files]

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        for file_item in files:
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_item.file.read())

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Multiple files uploaded successfully.')


os.chdir(os.path.dirname(os.path.abspath(__file__)))

httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)
print(f"Server running on port {PORT}")
httpd.serve_forever()
