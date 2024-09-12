from flask import Flask, render_template, send_from_directory, jsonify
import os
from handlers.handler import Handler
from value_manager import ValueManager
from handlers.handler import Handler
from value_manager import ValueManager
from pages.pages_utils import PageConfig

from handlers.robot_movement_handler import RobotMovementHandler
from handlers.audio_handler import AudioHandler

app = Flask(__name__)

ABSOLUTE_PATH = 'D:/HPS/web/web/templates'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu/index.html')
@app.route('/joystick')
def joystick():
    return render_template('joystick/index.html')

@app.route('/move', methods=['POST'])
def move():
    name = request.form.get('direction')  # Get 'name' from form data
    RobotmovementHandler.handle_task(name)
    return jsonify({"moved"})

audio_handler = AudioHandler()  # Initialize the class instance

# Route for page switching
@app.route('/page_switching', methods=['POST'])
def page_switching():
    data = request.get_json()
    page = data.get('page')
    args = data.get('args')
    audio_handler.page_switching(page, args)  # Call the function
    return jsonify({"message": f"Switched to {page} with args {args}."})

# Route for set_emotion
@app.route('/set_emotion', methods=['POST'])
def set_emotion():
    data = request.get_json()
    emotion = data.get('emotion')
    audio_handler.set_emotion(emotion)
    return jsonify({"message": f"Emotion set to {emotion}."})

# Route for take_a_photo
@app.route('/take_a_photo', methods=['POST'])
def take_a_photo():
    audio_handler.take_a_photo()
    return jsonify({"message": "Taking a photo."})

# Route for start_recording
@app.route('/start_recording', methods=['POST'])
def start_recording():
    audio_handler.start_recording()
    return jsonify({"message": "Recording started."})

# Route for end_recording
@app.route('/end_recording', methods=['POST'])
def end_recording():
    audio_handler.end_recording()
    return jsonify({"message": "Recording ended."})

# Route for set_count_down_timer
@app.route('/set_count_down_timer', methods=['POST'])
def set_count_down_timer():
    data = request.get_json()
    hours = data.get('hours', 0)
    minutes = data.get('minutes', 0)
    seconds = data.get('seconds', 0)
    audio_handler.set_count_down_timer(seconds, minutes, hours)
    return jsonify({"message": f"Timer set for {hours} hours, {minutes} minutes, and {seconds} seconds."})

# Route for add_todo
@app.route('/add_todo', methods=['POST'])
def add_todo():
    data = request.get_json()
    task_name = data.get('task_name')
    audio_handler.add_todo(task_name)
    return jsonify({"message": f"Task '{task_name}' added to the TODO list."})


@app.route('/files/<path:filename>')
def serve_files(filename):
    return send_from_directory(ABSOLUTE_PATH, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
