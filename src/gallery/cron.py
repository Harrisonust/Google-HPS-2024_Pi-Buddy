import os
from handlers.gallery_handler import GalleryHandler  # Ensure server_manager.py is in the same directory
import gallery
def update_html_and_restart_server():
    # Update the HTML
    os.system('python3 /home/pi/google_hps_dap_controller/src/gallery/gallery.py')  # This runs your script that updates the HTML file

    # Restart the server
    task_queue = None  # Replace with actual task queue if needed
    handler = GalleryHandler(task_queue)
    handler.restart_server()

if __name__ == "__main__":
    update_html_and_restart_server()
