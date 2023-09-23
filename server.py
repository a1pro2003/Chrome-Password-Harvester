import http.server
import socketserver
import os
import cgi
import shutil

# Define the directory where uploaded files will be saved
UPLOAD_DIR = 'uploads'

# Custom request handler to handle file uploads via POST requests
class FileUploadHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_type, _ = cgi.parse_header(self.headers.get('Content-Type'))
        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Check if a file was uploaded
            if 'file' in form:
                file_item = form['file']
                file_name = os.path.basename(file_item.filename)
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # Save the uploaded file
                with open(file_path, 'wb') as file:
                    shutil.copyfileobj(file_item.file, file)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'File uploaded successfully.')
                return

        # If no file was uploaded or content_type is not 'multipart/form-data'
        self.send_response(400)
        self.end_headers()
        self.wfile.write(b'Bad Request: No file uploaded or invalid content type.')

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Start the HTTP server on port 8000 with the custom request handler
with socketserver.TCPServer(('0.0.0.0', 8000), FileUploadHandler) as httpd:
    print('Server started on port 8000...')
    httpd.serve_forever()
