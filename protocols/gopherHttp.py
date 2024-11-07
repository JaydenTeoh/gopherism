import asyncio
import http.server
import urllib.parse
import mimetypes
import os
import ssl

# Gopher Server Configuration
GOPHER_HOST = '127.0.0.1'
GOPHER_PORT = 7070  # Changed from 70 to 7070 to avoid needing root permissions
PUB_DIR = 'pub/'  # Directory to serve
TLS = False
TLS_CERT_CHAIN = 'cacert.pem'
TLS_PRIVATE_KEY = 'privkey.pem'

# HTTP Server Configuration
HTTP_PORT = 8080  # HTTP port to serve Gopher content over HTTP


class GopherProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        print('Gopher Client connected:', self.peername)

    def data_received(self, data):
        request = data.decode('utf-8').strip()
        print(f"Received Gopher request: {request}")

        parts = request.split('\t')
        path = parts[0] if parts else '/'
        query = parts[1] if len(parts) > 1 else None
        response, mime_type = self.handle_gopher_request(path, query)

        self.transport.write(response if isinstance(response, bytes) else response.encode())
        self.transport.close()
        print(f"Served Gopher request for {path}")

    def handle_gopher_request(self, path, query):
        file_path = os.path.join(PUB_DIR, path.lstrip('/'))
        
        if os.path.isdir(file_path):
            entries = os.listdir(file_path)
            response = f"iDirectory listing for {path}\t\t\n"
            for entry in entries:
                entry_path = os.path.join(path, entry)
                if os.path.isdir(os.path.join(PUB_DIR, entry_path.lstrip('/'))):
                    response += f"1{entry}\t{entry_path}\t{GOPHER_HOST}\t{GOPHER_PORT}\n"
                else:
                    response += f"0{entry}\t{entry_path}\t{GOPHER_HOST}\t{GOPHER_PORT}\n"
            return response, "text/plain"
        
        elif os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as f:
                return f.read(), mime_type or 'application/octet-stream'
        
        return "3Error: Resource not found\t\t\n", "text/plain"


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><head><title>Gopher over HTTP</title></head>")
            self.wfile.write(b"<body><h1>Welcome to the Gopher over HTTP server</h1>")
            self.wfile.write(b'<ul><li><a href="/pub/">Browse Gopher pub directory</a></li></ul>')
            self.wfile.write(b"</body></html>")
            return

        if path.startswith('/pub/'):
            relative_path = path[len('/pub/'):]
        else:
            relative_path = path.lstrip('/')

        response, mime_type = self.handle_http_gopher_request(relative_path)

        if isinstance(response, bytes):
            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body>")
            self.wfile.write(response.encode())
            self.wfile.write(b"</body></html>")

    def handle_http_gopher_request(self, path):
        file_path = os.path.join(PUB_DIR, path)

        # Check if directory contains a gophermap and use it if present
        if os.path.isdir(file_path):
            gophermap_path = os.path.join(file_path, 'gophermap')
            if os.path.isfile(gophermap_path):
                # Parse gophermap as Gopher menu
                response = "<h2>Gopher Menu</h2><div>"
                with open(gophermap_path, 'r') as f:
                    for line in f:
                        line = line.rstrip('\n')
                        if line:
                            item_type = line[0]
                            parts = line[1:].split('\t')
                            label = parts[0]
                            item_path = parts[1] if len(parts) > 1 else ''
                            # Map Gopher item types to HTML format
                            if item_type == '1':  # Directory
                                item_path = item_path.strip('/')
                                response += f'<div><a href="/pub/{item_path}">{label}/</a></div>'
                            elif item_type == '0':  # Text file
                                item_path = item_path.rstrip('/')
                                response += f'<div><a href="/pub/{item_path}">{label}</a></div>'
                            elif item_type == 'i':  # Informational text
                                response += f'<pre>{label}<br/></pre>'  # Line break for 'i' items
                            else:  # Fallback for unknown types
                                item_path = item_path.rstrip('/')
                                response += f'<div><a href="/pub/{item_path}">{label}</a></div>'
                response += "</div>"
                return response, "text/html"
            else:
                # No gophermap, fallback to directory listing
                entries = os.listdir(file_path)
                response = f"<h2>Directory listing for /pub/{path}</h2><div>"
                for entry in entries:
                    entry_path = os.path.join(path, entry)
                    if os.path.isdir(os.path.join(PUB_DIR, entry_path)):
                        response += f'<div><a href="/pub/{entry_path}/">{entry}/</a></div>'
                    else:
                        response += f'<div><a href="/pub/{entry_path}">{entry}</a></div>'
                response += "</div>"
                return response, "text/html"

        elif os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as f:
                return f.read(), mime_type or 'application/octet-stream'

        return "<h2>Error: Resource not found</h2>", "text/html"


async def start_gopher_server():
    """Start the Gopher server with asyncio."""
    loop = asyncio.get_running_loop()
    ssl_context = None
    if TLS:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(TLS_CERT_CHAIN, TLS_PRIVATE_KEY)

    server = await loop.create_server(GopherProtocol, GOPHER_HOST, GOPHER_PORT, ssl=ssl_context)
    print(f"Gopher server running on {GOPHER_HOST}:{GOPHER_PORT} with TLS={TLS}")
    await server.serve_forever()


def start_http_server():
    """Start the HTTP server on a separate thread."""
    httpd = http.server.HTTPServer(('localhost', HTTP_PORT), HTTPHandler)
    print(f"HTTP wrapper running on http://localhost:{HTTP_PORT}")
    httpd.serve_forever()


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(start_gopher_server())
    loop.run_in_executor(None, start_http_server)
    loop.run_forever()


if __name__ == "__main__":
    main()
