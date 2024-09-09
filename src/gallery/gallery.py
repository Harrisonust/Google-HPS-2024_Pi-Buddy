import os
from handlers.battery_handler import BatteryHandler

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg']

GALLERY_FOLDER = 'src/gallery'  # Path to your gallery folder
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
                padding:15px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }
            .greeting-row {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 20px;
                background-color: #fff;
            }
            .greeting-left {
                display: flex;
                flex-direction: column;  /* Stacks the greeting texts vertically */
                align-items: flex-start;
            }
            .greeting-text {
                font-size: 42px;
                color: #333;
                font-weight: bold;
                margin-bottom: 5px;  /* Adds space between the texts */
            }
            .greeting-images img {
                height: 100px;
                align-items: left;
            }
            .greeting-battery img {
                height: 100px;
                object-fit: contain;
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
                background-color: #333;
                color: white;
                text-align: center;
                padding: 10px 0;
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 25px; /* Footer height */
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
        
        <!-- Greeting Row with Text and Images -->
        <div class="greeting-row">     
            <div class="greeting-left">
                <div class="greeting-text">Good Morning!</div>
                <div class="greeting-text">I am Pibuddy~</div>
            </div>
            <div class="greeting-images">  
                <img src="icons/pibuddy.png" alt="Pibuddy">   
                <img src="icons/battery1.png" alt="Battery">  
            </div>  
        </div>

        <div class="container">
            <div class="gallery-section">
                <div class="section-title">Images</div>
                <div class="gallery" id="images-gallery">
    '''
    
    if BatteryHandler.battery_charging.reveal():
        if BatteryHandler.battery_level.reveal()>80:
            html_content += '<img src="icons/battery1.png" alt="Battery5c">\n'
        elif BatteryHandler.battery_level.reveal()>60:
            html_content += '<img src="icons/battery1.png" alt="Battery4c">\n'
        elif BatteryHandler.battery_level.reveal()>40:
            html_content += '<img src="icons/battery1.png" alt="Battery3c">\n'
        elif BatteryHandler.battery_level.reveal()>20:
            html_content += '<img src="icons/battery1.png" alt="Battery2c">\n'
        elif BatteryHandler.battery_level.reveal()>0:
            html_content += '<img src="icons/battery1.png" alt="Battery1c">\n'
    
    else:
        if BatteryHandler.battery_level.reveal()>80:
            html_content += '<img src="icons/battery1.png" alt="Battery5">\n'
        elif BatteryHandler.battery_level.reveal()>60:
            html_content += '<img src="icons/battery1.png" alt="Battery4">\n'
        elif BatteryHandler.battery_level.reveal()>40:
            html_content += '<img src="icons/battery1.png" alt="Battery3">\n'
        elif BatteryHandler.battery_level.reveal()>20:
            html_content += '<img src="icons/battery1.png" alt="Battery2">\n'
        elif BatteryHandler.battery_level.reveal()>0:
            html_content += '<img src="icons/battery1.png" alt="Battery1">\n'
        
    
    image_count = 0
    video_count = 0

    # Loop through files in the directory and add images
    for file_name in os.listdir('src/images'):
        file_path = os.path.join('src/images', file_name)
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
    for file_name in os.listdir('src/videos'):
        file_path = os.path.join('src/videos', file_name)
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
