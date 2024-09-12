import time
import os
import time
import speech_recognition as sr
import numpy as np
import google.generativeai as genai
import threading
from gtts import gTTS
import re
import sqlite3

# from handlers.audio_control_handler import process_response
from handlers.handler import Handler
from value_manager import ValueManager
from handlers.handler import Handler
from value_manager import ValueManager
from pages.pages_utils import PageConfig

class AudioHandler(Handler):

    def __init__(self, task_queue):
        self.run_input_process = False
        # self.run_input_process = True
        self.task_queue = task_queue

        self.r = sr.Recognizer()  # Set up the speech recognition engine
        self.r.pause_threshold = 0.5
        self.r.energy_threshold = 300
        self.greetings = [
            "Hello! What can I do for you today?",
            "yeah?",
            "Hello there",
            "Hi, how can I assist you?"
        ]
        self.chat_history = []  # Initialize chat history
        self.audio_gain = 1500

        task = threading.Thread(target=self.listen_for_wake_word)
        task.start()


    # Listen for the wake word "hey"
    def listen_for_wake_word(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            self.r.adjust_for_ambient_noise(source)  # Adjust for ambient noise

            while True:
                try:
                    print("Listening audio")
                    audio = self.r.listen(source, phrase_time_limit=5)
                    print("Recognizing audio")
                    text = self.r.recognize_google(audio)
                    print(f"You said: {text}")
                    if "hey" in text.lower():
                        print("Wake word detected.")
                        response_text = np.random.choice(self.greetings)
                        print(response_text)
                        #os.system(f"espeak -v en+f3 '{response_text}'")  # Use espeak to say the greeting
                        tts = gTTS(text=response_text, lang='en', slow = False)
                        tts.save("audio/output.wav")
                        os.system(f"mpg321 -g {self.audio_gain} audio/output.wav")
                        self.listen_and_respond(source)
                except sr.UnknownValueError:
                    print('input not recognized')
                time.sleep(0.5)


    # Listen for input and respond with OpenAI API
    def listen_and_respond(self, source):
        while True:
            print("Listening...")
            os.system("aplay audio/beep.wav")
            try:
                print("Listening audio")
                audio = self.r.listen(source, timeout=5, phrase_time_limit=8)
                print("Recognizing audio")
                text = self.r.recognize_google(audio)
                print(f"You said: {text}")
                os.system("aplay audio/boop.wav")
                if not text:
                    print("No speech detected, returning to wake word listening.")
                    #continue
                    break
                    #return
                elif "bye" in text.lower():
                    tts = gTTS(text='Goodbye', lang='en', slow = False)
                    tts.save("audio/output.wav")
                    os.system(f"mpg321 -g {self.audio_gain} audio/output.wav")
                    break
                else:
                    self.page_switching('QA',args={'who':'user','what':text})


                # Send input to Gemini API
                api_key = "AIzaSyC5olADq7MxujG6hbSBGBIDQXVKwWge97I"
                prompt = "\n".join(self.chat_history) + f"\nUser: {text}\nPi-buddy:"
                system_instructions = 'You are Pi-buddy, a friendly AI desktop pet. ' + \
                      'You are mostly optimistic, but also easily moody. ' + \
                      'Please always return your mood at the start of your response (#depressed, #joyful, #hungry, #energetic, #sleepy, #scared) ' + \
                      'based on user prompt and your own response. ' + \
                      'If the new user prompt or your response does not show a new emotion, please maintain the previous emotion.' + \
                      'You have the ability to empathize, e.g. if user is having a bad mood, then you should either be depressed as well, or you can also choose to cheer him up.' +\
                      'Please don\'t include any kind of emojis. ' + \
                      'Please consider the dictionary below. ' + \
                      'If any !command is called, then there is no need to set #emotion. ' + \
                      'Always try to match the user\'s input to the closest command in the dictionary, ' + \
                      'even if the phrasing doesn\'t match exactly. ' + \
                      'If you catch any of the commands in the dictionary or anything insinuating these commands, ' + \
                      'please include the corresponding text in the dictionary below at the start of your response. ' + \
                      'For example, if I ask "how is the weather today," you should switch to the weather page. ' + \
                      'If I ask "what time is it now," you should switch to the time page. ' + \
                      'If I ask "remind me to do something," you should trigger the "add task to todo" command. ' + \
                      'It should look like !command(number) along with any arguments stated for that command number using &(arg_variable). ' + \
                      'Please note that you are capable of all these commands and ' + \
                      'should give an affirmative response in the present continuous tense for any of these commands, ' + \
                      'e.g., "switching to weather page," "I am coming," or "ok, I will take a photo for you." ' + \
                      'Dictionary: ' + \
                      '"If I ask a question related to weather, switch to the weather page": "!Command1 &Weather", ' + \
                      '"If I ask about the time, switch to the time page": "!Command1 &Time", ' + \
                      '"Switch to the timer page": "!Command1 &Timer", ' + \
                      '"Switch to the photograph page": "!Command1 &Photograph", ' + \
                      '"Switch to the film page": "!Command1 &Film", ' + \
                      '"If I ask how much battery you have, switch to the battery page": "!Command1 &Battery", ' + \
                      '"If I ask questions like what do I need to do, switch to the todo page": "!Command1 &Todo", ' + \
                      '"Come to me": "!Command2", ' + \
                      '"Set emotion to depressed": "!Command3 &depressed", ' + \
                      '"Set emotion to joyful": "!Command3 &joyful", ' + \
                      '"Set emotion to hungry": "!Command3 &hungry", ' + \
                      '"Set emotion to energetic": "!Command3 &energetic", ' + \
                      '"Set emotion to sleepy": "!Command3 &sleepy", ' + \
                      '"Set emotion to scared": "!Command3 &scared", ' + \
                      '"Set a timer for x seconds": "!Command4 &(x)&0&0", ' + \
                      '"Set a timer for x minutes": "!Command4 &0&(x)&0", ' + \
                      '"Set a timer for x hours": "!Command4 &0&0&(x)", ' + \
                      '"Set a timer for x minutes and y seconds": "!Command4 &(y)&(x)&0", ' + \
                      '"Set a timer for x hours and y minutes": "!Command4 &0&(y)&(x)", ' + \
                      '"Set a timer for x hours, y minutes, and z seconds": "!Command4 &(z)&(y)&(x)", ' + \
                      '"Add task to todo": "!Command5 &(task_to_be_done)" (please connect each word in the todo phrase with "_"), ' + \
                      '"Take a photo": "!Command6", ' + \
                      '"Start recording video": "!Command7", ' + \
                      '"Start recording video for x seconds": "!Command7 &(x)", ' + \
                      '"End recording": "!Command8"'

                model = 'gemini-1.5-flash'
                temperature = 0.5
                stop_sequence = ''

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model, system_instruction=system_instructions)
                config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
                response = model.generate_content(contents=[prompt], generation_config=config)
                print("prompt", prompt)
                print("response.text", response.text)
                response_text = self.process_response(response.text)

                # Append the user input and AI response to chat history
                self.chat_history.append(f"User: {text}")
                self.chat_history.append(f"Pi-buddy: {response_text}")
                
                time.sleep(0.5)

                if not audio:
                    self.listen_for_wake_word()

            except sr.UnknownValueError:
                print("unknown value error, keep listening...")
                time.sleep(2)
                continue
            except sr.WaitTimeoutError:
                print("wait timeout error, keep listening...")
                time.sleep(2)
                continue
            except sr.RequestError as e:
                print(f"Could not request results; {e}, keep listening")
                time.sleep(2)
                continue

    def page_switching(self, page, args=None):
        # 1
        print(f'page = {page}, args = {args}')
        # If no arguments are given, and the page is 'Timer', go to the 'SetTimer' page
        if page == 'Timer':
            if args == None:
                page = 'SetTimer'
            else:
                args = self._get_time_val(
                    seconds_to_count_down = args[0]
                )

        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'SWITCH_PAGE',
            'page_key': page + 'Page',
            'args': args
        })
        
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'encoders',
            'task': 'RESET_TIMER'
        })


    def call_and_come(self):
        # -1
        pass


    def set_emotion(self, emotion):
        # 3
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'emotion',
            'task': 'SET_EMOTION',
            'args': emotion,
        })


    def set_count_down_timer(self, seconds_to_count_down=0, minutes_to_count_down=0, hours_to_count_down=0):
        # 2
        if seconds_to_count_down == 0 and minutes_to_count_down == 0 and hours_to_count_down == 0:
            raise ValueError("Error: arguments cannnot all be 'None' for 'set_count_down_timer'")

        minutes_to_count_down += hours_to_count_down * 60
        seconds_to_count_down += minutes_to_count_down * 60
        self.page_switching('Timer', (seconds_to_count_down,))


    def add_todo(self, task_name):
        # 5
        self._write_todo_task(task_name)

        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'RELOAD_TODO_TASK',
        })


    def take_a_photo(self):
        # 4
        self.page_switching('Photograph', 'take_photo')


    def start_recording(self):
        # 4
        self.page_switching('Film', 'start_recording')


    def end_recording(self):
        # 4
        self.task_queue.append({
            'requester_name': 'audio_control',
            'handler_name': 'menu_screen',
            'task': 'END_RECORDING',
        })


    def _get_time_val(self, seconds_to_count_down=0, minutes_to_count_down=0, hours_to_count_down=0):
        minutes_to_count_down += seconds_to_count_down // 60
        seconds_to_count_down %= 60
        hours_to_count_down += minutes_to_count_down // 60
        minutes_to_count_down %= 60
        hours_to_count_down %= 100

        return {
            'hr_h':  hours_to_count_down // 10,
            'hr_l':  hours_to_count_down % 10,
            'min_h': minutes_to_count_down // 10,
            'min_l': minutes_to_count_down % 10,
            'sec_h': seconds_to_count_down // 10,
            'sec_l': seconds_to_count_down % 10
        }

    def _write_todo_task(self, task_name):
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(
                f'''
                INSERT INTO todo (task_name, is_active)
                VALUES           ('{task_name}', 1);
                '''
            )
            self.conn.commit()

        except Exception as e:
            print(f'An error occurred: {e}')


    def process_response(self, response_text: str):
        # Regular expressions to find !CommandX, &args, and #{emotion}
        command_pattern = r"!Command(\d+)"
        arg_pattern = r"&(\w+)"
        emotion_pattern = r"#(\w+)"

        # Find and process command
        command_match = re.search(command_pattern, response_text)
        args = re.findall(arg_pattern, response_text)
        emotions = re.findall(emotion_pattern, response_text)
        
        # Remove the processed parts from response_text
        response_text = re.sub(command_pattern, '', response_text)
        response_text = re.sub(arg_pattern, '', response_text)
        response_text = re.sub(emotion_pattern, '', response_text)

        # Clean up the remaining text
        leftover_text = response_text.strip()
        self.page_switching('QA', args={'who':'robot','what':response_text})
        if isinstance(response_text, str) and not response_text.strip():
            print("response_text is an empty string.")
        elif isinstance(response_text, list) and not any(response_text):
            print("response_text is an empty list.")
        else:
            tts = gTTS(text=response_text, lang='en', slow = False)
            tts.save("audio/output.wav")
            os.system(f"mpg321 -g {self.audio_gain} audio/output.wav")
                

        if command_match:
            command_number = int(command_match.group(1))
            # Call the appropriate command function based on command_number
            if command_number == 1:
                page = args[0] if args else None
                additional_args = args[1:] if len(args) > 1 else None
                self.page_switching(page, additional_args)
                print('Page switched to ' + page)
            elif command_number == 2:
                self.call_and_come()
                print('Call and come executed successfully')
            elif command_number == 3:
                emotion = args[0]
                self.set_emotion(emotion)
                self.page_switching('Emotion')
                print('Emotion set to ' + str(emotion))
            elif command_number == 4:
                seconds = int(args[0]) if len(args) > 0 else None
                minutes = int(args[1]) if len(args) > 1 else None
                hours = int(args[2]) if len(args) > 2 else None
                self.set_count_down_timer(seconds, minutes, hours)
                print(f'Countdown timer set to {hours} hours, {minutes} minutes, and {seconds} seconds')
            elif command_number == 5:
                task_name = args[0] if args else None
                self.add_todo(task_name)
                print('Task added: ' + str(task_name))
            elif command_number == 6:
                self.take_a_photo()
                print('Photo taken successfully')
            elif command_number == 7:
                seconds_of_video = int(args[0]) if args else None
                self.start_recording()
                print(f'Started recording for {seconds_of_video} seconds')
            elif command_number == 8:
                self.end_recording()
                print('Recording ended successfully')

        elif emotions:
            print('Setting emotion to ' + str(emotions[0]))
            self.set_emotion(emotions[0])
            self.page_switching('Emotion')

        return leftover_text
