import http.server
import socketserver
import threading
import os
import requests

from handlers.handler import Handler
from value_manager import ValueManager

PORT = 8000  # Port number for the HTTP server
WEB_FOLDER = 'src/gallery/'  # Directory containing the static files

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Modify the path to point to the WEB_FOLDER
        path = super().translate_path(path)
        return os.path.join(WEB_FOLDER, os.path.basename(path))
    
class GalleryHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = False
        self.task_queue = task_queue
        self.server_thread = None
        self.httpd = None
        self.run_server = False
        self.start_server()

    def get_public_ip(self):
        try:
            response = requests.get('https://api.ipify.org')
            response.raise_for_status()  # Check if the request was successful
            print("Public IP address:", response.text)
        except requests.RequestException as e:
            print("Error retrieving public IP address:", e)

        
    def start_server(self):
        if self.run_server:
            print("Server is already running.")
            return

        # Define the handler to serve files from the WEB_FOLDER
        Handler = CustomHTTPRequestHandler

        # Create a new server instance
        self.httpd = socketserver.TCPServer(("", PORT), Handler)
        self.run_server = True

        # Start the server in a new thread
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.start()
        IP = self.get_public_ip()
        print(f"Serving at port{IP}:{PORT}")
    
    def stop_server(self):
        if self.run_server:
            self.run_server = False
            self.httpd.shutdown()
            self.server_thread.join()
            print("Server stopped.")

    def restart_server(self):
        if self.run_server:
            print("Restarting the server...")
            self.stop_server()
        self.start_server()

    # Example usage: Restart the server
    # handler.restart_server()
