import os
import shutil

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg']

GALLERY_FOLDER = '/home/pi/google_hps_dap_controller/src/web/static/gallery/'  # '/home/pi/image_gallery'
VIDEO_FOLDER = '/home/pi/google_hps_dap_controller/src/images'
IMAGE_FOLDER = '/home/pi/google_hps_dap_controller/src/images'
HTML_FILE = '/home/pi/google_hps_dap_controller/src/web/templates/index.html'

def create_gallery_html():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="stylesheet" href="{{ url_for('static', filename='css/vars.css') }}" />
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}" />
        <style>
        a,
        button,
        input,
        select,
        h1,
        h2,
        h3,
        h4,
        h5,
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            border: none;
            text-decoration: none;
            background: none;

            -webkit-font-smoothing: antialiased;
        }

        menu,
        ol,
        ul {
            list-style-type: none;
            margin: 0;
            padding: 0;
        }
        </style>
        <script>
        function expandMedia(mediaElement) {
            const pop = document.getElementById('pop');
            const popImage = document.getElementById('pop-media');
            const popVideo = document.getElementById('pop-video');

            if (mediaElement.tagName === 'IMG') {
                popImage.src = mediaElement.src;
                popImage.style.display = 'block';
                popVideo.style.display = 'none';
            } else if (mediaElement.tagName === 'VIDEO') {
                popVideo.src = mediaElement.src;
                popVideo.style.display = 'block';
                popImage.style.display = 'none';
            }

            pop.style.display = 'flex';
        }
        function closeOverlay() {
            const pop = document.getElementById('pop');
            pop.style.display = 'none';
        }
        function showMenu() {
            const overlay = document.getElementById('overlay');
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/menu', true);
            xhr.onload = function () {
                if (xhr.status === 200) {
                    overlay.innerHTML = xhr.responseText;
                    overlay.classList.add('show');
                }
            };
            xhr.send();
        }

        function showJoystick() {
            const joystick = document.getElementById('overlay');
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/joystick', true);
            xhr.onload = function () {
                if (xhr.status === 200) {
                    joystick.innerHTML = xhr.responseText;
                    joystick.classList.add('show');
                }
            };
            xhr.send();
        }
        function hideOverlay() {
            const overlay = document.getElementById('overlay');
            overlay.classList.remove('show');
            overlay.innerHTML = ''; // Clear content to reload next time
        }

        window.onclick = function(event) {
            const overlay = document.getElementById('overlay');
            if (event.target == overlay) {
                hideOverlay();
            }
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                hideOverlay();
            }
        });
        </script>
    </head>
    <body>
        <div class="home">
            <img class="aura" src="{{ url_for('static', filename='icons/aura.png') }}" />
        </div>
        <div class="welcome-i-am-pibuddy">
            Welcome
            <br />
            I am Pi-Buddy~
        </div>
        <img class="pibuddy" src="{{ url_for('static', filename='icons/pibuddy.png') }}" />
        <a href="raspberrypi.local:8421">
            <img class="battery" src="{{ url_for('static', filename='icons/battery-5-10.png') }}" alt="Battery Button" />
        </a>
        <div class="group-2">
            <div class="gallery">Gallery</div>
            <div class="gallery-container">
            <div class="gallery-section images">
                <h2>Images</h2>
                <div class="media-container">
    '''

    image_count = 0
    video_count = 0

    # Loop through files in the directory and add images
    for file_name in os.listdir(IMAGE_FOLDER):
        file_path = os.path.join(IMAGE_FOLDER, file_name)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_name)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                shutil.copy(file_path, GALLERY_FOLDER)
                html_content += '<img src="{{ url_for(\'static\', filename=\'gallery/'
                html_content += f'{file_name}\')' 
                html_content += '}}'
                html_content +=f'" alt="{file_name}">\n'
                image_count += 1

    # If no images found, display a placeholder
    if image_count == 0:
        html_content += '<div class="placeholder">No pictures available</div>\n'

    # Add the video section
    html_content += '''
            </div>
        </div>
        <div class="gallery-section videos">
            <h2>Videos</h2>
            <div class="media-container">
    '''

    # Loop through files in the directory and add videos
    for file_name in os.listdir(VIDEO_FOLDER):
        file_path = os.path.join(VIDEO_FOLDER, file_name)
        if os.path.isfile(file_path):
            shutil.copy(file_path, GALLERY_FOLDER)
            ext = os.path.splitext(file_name)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                html_content += '<video controls><source src="{{ url_for(\'static\', filename=\'gallery/'
                html_content += f'{file_name}\')' 
                html_content += '}}'
                html_content +=f'" type="video/{ext[1:]}">Your browser does not support the video tag.</video>\n'
                image_count += 1
 
                video_count += 1

    # If no videos found, display a placeholder
    if video_count == 0:
        html_content += '<div class="placeholder">No videos available</div>\n'

    # Close the gallery divs and add the footer
    html_content += '''
    </div>
    </div>
        <div class="pop" id="pop" onclick="closeOverlay()">
            <img id="pop-media" src="" style="display: none;">
            <video id="pop-video" src="" style="display: none;" controls></video>
        </div>
            </div>
        </div>
        <div class="line-1"></div>
        <div class="line-2"></div>

        <button class="remote-button" onclick="showMenu()">
            <div class="rectangle-4">
            <div class="menu">Menu</div>
            </div>
        </button>

        <button class="remote-button" onclick="showJoystick()">
            <div class="rectangle-42">
            <div class="remote-control">
                Remote
                <br />
                Control
            </div>
            </div>
        </button>
        <div id="overlay" class="overlay"> </div>
        <footer class="footer">� Your Pibuddy gallery. @ Google HPS team4.</footer>
    </body>
    </html>
    '''

    # Write the HTML to the file
    with open(HTML_FILE, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"Gallery HTML has been generated and saved as '{HTML_FILE}'.")

if __name__ == "__main__":
    create_gallery_html()
