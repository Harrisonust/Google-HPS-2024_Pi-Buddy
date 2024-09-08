import os

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg']

GALLERY_FOLDER = 'gallery'  # '/home/pi/image_gallery'
HTML_FILE = os.path.join(GALLERY_FOLDER, 'index.html')

def create_gallery_html():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Media Gallery</title>
        <style>
            html, body {
                height: 100%;
                margin: 0;
            }
            body {
                display: grid;
                grid-template-rows: 1fr auto;
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #b9b5ba;
                color: #333;
            }
            header {
                background-color: #9209ed;
                color: white;
                padding: 15px 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }
            .container {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .gallery-section {
                flex: 1;
                min-width: 300px;
                margin: 10px;
            }
            .section-title {
                font-size: 22px;
                text-align: center;
                margin-bottom: 15px;
                color: #333;
            }
            .gallery {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                grid-gap: 15px;
                padding: 0;
            }
            .gallery img, .gallery video {
                width: 100%;
                height: auto;
                object-fit: cover;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .gallery img:hover, .gallery video:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            }
            .placeholder {
                font-size: 18px;
                color: #666;
                text-align: center;
                padding: 20px;
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            footer {
                text-align: center;
                padding: 10px 20px;
                background-color: #333;
                color: white;
                margin-top: 30px;
                font-size: 14px;
            }
            footer a {
                color: #3b303d;
                text-decoration: none;
            }
            footer a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <header>
            My Media Gallery
        </header>
        
        <div class="container">
            <div class="gallery-section">
                <div class="section-title">Images</div>
                <div class="gallery" id="images-gallery">
    '''

    image_count = 0
    video_count = 0

    # Loop through files in the directory and add images
    for file_name in os.listdir(GALLERY_FOLDER):
        file_path = os.path.join(GALLERY_FOLDER, file_name)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_name)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                html_content += f'<img src="{file_name}" alt="{file_name}">\n'
                image_count += 1

    # If no images found, display a placeholder
    if image_count == 0:
        html_content += '<div class="placeholder">No pictures available</div>\n'

    # Add the video section
    html_content += '''
                </div>
            </div>
            <div class="gallery-section">
                <div class="section-title">Videos</div>
                <div class="gallery" id="videos-gallery">
    '''

    # Loop through files in the directory and add videos
    for file_name in os.listdir(GALLERY_FOLDER):
        file_path = os.path.join(GALLERY_FOLDER, file_name)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_name)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                html_content += f'<video controls><source src="{file_name}" type="video/{ext[1:]}">Your browser does not support the video tag.</video>\n'
                video_count += 1

    # If no videos found, display a placeholder
    if video_count == 0:
        html_content += '<div class="placeholder">No videos available</div>\n'

    # Close the gallery divs and add the footer
    html_content += '''
                </div>
            </div>
        </div>
        <footer>
            © Your Pibuddy gallery. @ Google HPS team4.
        </footer>
    </body>
    </html>
    '''

    # Write the HTML to the file
    with open(HTML_FILE, 'w') as file:
        file.write(html_content)
    print(f"Gallery HTML has been generated and saved as '{HTML_FILE}'.")

if __name__ == "__main__":
    create_gallery_html()
