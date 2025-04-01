from langflow.custom.custom_component.component import Component
from langflow.inputs.inputs import MessageInput
from langflow.schema.message import Message
from langflow.io import MessageTextInput, Output
import subprocess
import time
import threading
from flask import Flask, send_from_directory, jsonify, request, send_file
import os
import zipfile
import io

# Flask app initialization
app = Flask(__name__)

# Flask routes
@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        directory = request.args.get('directory')
        file_type = request.args.get('file_type', '').lower()

        if not directory or not file_type:
            return jsonify({"error": "Both 'directory' and 'file_type' query parameters are required"}), 400

        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return jsonify({"error": f"Directory '{directory}' does not exist"}), 404

        files = [f for f in os.listdir(directory) if f.lower().endswith(file_type)]
        if not files:
            return jsonify({"message": f"No files with type '{file_type}' found in the directory"}), 200

        file_urls = {f: f'http://{request.host}/download/{f}?directory={directory}' for f in files}
        return jsonify(file_urls)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        directory = request.args.get('directory')

        if not directory:
            return jsonify({"error": "'directory' query parameter is required"}), 400

        directory = os.path.abspath(directory)
        file_path = os.path.join(directory, filename)

        if not os.path.exists(directory):
            return jsonify({"error": f"Directory '{directory}' does not exist"}), 404
        if not os.path.isfile(file_path):
            return jsonify({"error": f"File '{filename}' not found in the directory"}), 404

        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_all', methods=['GET'])
def download_all():
    try:
        directory = request.args.get('directory')
        file_type = request.args.get('file_type', '').lower()

        if not directory or not file_type:
            return jsonify({"error": "Both 'directory' and 'file_type' query parameters are required"}), 400

        directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            return jsonify({"error": f"Directory '{directory}' does not exist"}), 404

        files = [f for f in os.listdir(directory) if f.lower().endswith(file_type)]
        if not files:
            return jsonify({"message": f"No files with type '{file_type}' found in the directory"}), 200

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                file_path = os.path.join(directory, file)
                zip_file.write(file_path, arcname=file)

        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f"{file_type}_files.zip")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

class FileDownloader(Component):
    name = "filesDownload"
    display_name = "Files Downloader"
    description = "A custom component to make a url to download files."
    inputs = [
        MessageTextInput(
            name="files_dir",
            display_name="Directory Path",
            info="Directory containing files to download.",
            tool_mode=True
        ),
        MessageTextInput(
            name="file_type",
            display_name="Files Type",
            info="File type to download.",
            tool_mode=True
        ),
    ]

    outputs = [
        Output(display_name="Result", name="result", method="generate_url"),
    ]

    def start_flask_app(self):
        """Start the Flask app"""
        app.run(host='0.0.0.0', port=5000)

    def run_flask_app_in_thread(self):
        """Starts Flask App in a separate thread"""
        thread = threading.Thread(target=self.start_flask_app, daemon=True)
        thread.start()
        time.sleep(2)  # Give the server some time to start

    def generate_url(self) -> Message:
        """Generate link to download files"""
        self.run_flask_app_in_thread()
        return Message(text=f"http://localhost:5000/download_all?directory={self.files_dir}&file_type={self.file_type}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)