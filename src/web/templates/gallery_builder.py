import os

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg']

GALLERY_FOLDER = 'd:/HPS/web/web/templates/'  # '/home/pi/image_gallery'
HTML_FILE = os.path.join(GALLERY_FOLDER, 'index.html')

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
            <div class="rectangle-2"></div>
            <div class="gallery">Gallery</div>
            <div class="gallery-container">
            <div class="gallery-section images">
                <h2>Images</h2>
    '''

    image_count = 0
    video_count = 0

    # Loop through files in the directory and add images
    for file_name in os.listdir(GALLERY_FOLDER):
        file_path = os.path.join(GALLERY_FOLDER, file_name)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_name)[1].lower()
            if ext in IMAGE_EXTENSIONS:
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
            <div class="gallery-section videos">
                <h2>Videos</h2>
    '''

    # Loop through files in the directory and add videos
    for file_name in os.listdir(GALLERY_FOLDER):
        file_path = os.path.join(GALLERY_FOLDER, file_name)
        if os.path.isfile(file_path):
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
        </div>
        <div class="line-1"></div>
        <div class="line-2"></div>

        <button class="remote-button" onclick="openOverlay()">
            <div class="rectangle-4">
            <div class="menu">Menu</div>
            </div>
        </button>

        <button class="remote-button" onclick="openOverlay()">
            <div class="rectangle-42">
            <div class="remote-control">
                Remote
                <br />
                Control
            </div>
            </div>
        </button>
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
