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
        # Define the CRON job details
        cron_job = "*/5 * * * * /home/pi/google_hps_dap_controller/src/.venv/bin/python D:/GitHub/google_hps_dap_controller/src/gallery/cron.py"
        cron_file = "/tmp/mycron"
        setup_cron_job()
        print("CRON job has been set up.")

        self.run_server = False
        self.start_server()


    def setup_cron_job(self):
        # Create a backup of the current crontab
        os.system('crontab -l > {}'.format(self.cron_file))

        # Add the new cron job
        with open(self.cron_file, 'a') as f:
            f.write(f"\n{self.cron_job}\n")

        # Install the new cron job
        os.system('crontab {}'.format(self.cron_file))

        # Remove the temporary cron file
        os.system('rm {}'.format(self.cron_file))



    def get_public_ip(self):
        try:
            # Run the `hostname -I` command
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
        # Get the output of the command
            output = result.stdout.strip()
        # Split the output into lines (or space-separated values)
            ipv4_addresses = output.split()
        # return ipv4 address
            return ipv4_addresses[0]
        except:
            print("Error retrieving public IP address")
            return

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
        print(f"Serving at {IP}:{PORT}")
    
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
