import http.server
import socketserver
import threading
import os
import requests
import subprocess
from handlers.handler import Handler
from value_manager import ValueManager

PORT = 8000  # Port number for the HTTP server
WEB_FOLDER = '/home/pi/google_hps_dap_controller/src/gallery/'  # Directory containing the static files

class GalleryHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = False
        self.task_queue = task_queue
        self.server_thread = None
        self.server_thread = threading.Thread(self.start_server())
        self.server_thread.start()

    def start_server(self):
        os.system("python app.py")
        # Start the server in a new thread
        self.server_thread = threading.Thread()
        self.server_thread.start()

