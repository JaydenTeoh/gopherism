from flask import Flask, send_file, abort, render_template_string
import os

app = Flask(__name__)

# Directory to serve files from
FILE_DIRECTORY = "pub"

# HTML template for displaying the file list
file_list_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File List</title>
</head>
<body>
    <h1>Available Files</h1>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def list_files():
    # List all files in the FILE_DIRECTORY
    try:
        files = os.listdir(FILE_DIRECTORY)
        files = [f for f in files if os.path.isfile(os.path.join(FILE_DIRECTORY, f))]
        return render_template_string(file_list_template, files=files)
    except FileNotFoundError:
        return "<p>File directory not found.</p>", 404

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Create the path to the requested file
    file_path = os.path.join(FILE_DIRECTORY, filename)
    # Check if the file exists and is a file, then send it for download
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404)  # File not found

if __name__ == '__main__':
    # Ensure the directory exists
    if not os.path.exists(FILE_DIRECTORY):
        os.makedirs(FILE_DIRECTORY)
    
    # Paths to your certificate and private key files
    cert_file = 'tls/cacert.pem'  # Replace with your certificate file path
    key_file = 'tls/privkey.pem'    # Replace with your private key file path

    # Start the HTTPS server with TLS enabled
    app.run(host='0.0.0.0', port=8443, ssl_context=(cert_file, key_file))
