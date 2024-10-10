from http.server import BaseHTTPRequestHandler, HTTPServer

# HTML template for the page
PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Simple OTEL endpoint</title>
<script>
function updateContent() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == XMLHttpRequest.DONE) {
            document.body.innerText = xhr.responseText;
        }
    };
    xhr.open("GET", "/content", true);
    xhr.send();
}
setInterval(updateContent, 1000);
</script>
</head>
<body>
</body>
</html>
"""

# Global variable to store incoming messages
incoming_messages = []

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/content":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("\n".join(incoming_messages).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(PAGE_HTML.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        incoming_messages.clear() # Comment this line to keep appending data 
        incoming_messages.append(post_data.decode())        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'POST request received')

def run(server_class=HTTPServer, handler_class=RequestHandler, port=3317):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting HTTP server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
