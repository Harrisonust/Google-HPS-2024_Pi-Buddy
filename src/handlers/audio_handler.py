import time
import os
import time
import speech_recognition as sr
import numpy as np
import google.generativeai as genai
import threading
from gtts import gTTS
import re

# from handlers.audio_control_handler import process_response
from handlers.handler import Handler
from value_manager import ValueManager
from handlers.handler import Handler
from value_manager import ValueManager


class AudioHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = False
        # self.run_input_process = True
        self.task_queue = task_queue
        
        self.r = sr.Recognizer()  # Set up the speech recognition engine
        self.greetings = [
            "Hello! What can I do for you today?",
            "yeah?",
            "Hello there",
            "Hi, how can I assist you?"
        ]

        task = threading.Thread(target=self.listen_for_wake_word)
        task.start()
    
    # Listen for the wake word "hey"
    def listen_for_wake_word(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise, please wait...")
            self.r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            while True:
                #try:
                    print("Listening audio")
                    audio = self.r.listen(source, timeout=2, phrase_time_limit=3)
                    text = self.r.recognize_google(audio)
                    print(text)
                    if "hey" in text.lower():
                        print("Wake word detected.")
                        response_text = np.random.choice(self.greetings)
                        print(response_text)
                        #os.system(f"espeak -v en+f3 '{response_text}'")  # Use espeak to say the greeting
                        tts = gTTS(text=response_text, lang='en', slow = False)
                        tts.save("output.wav")
                        os.system("mpg321 output.wav")
                        time.sleep(2)
                        self.listen_and_respond(source)
                #except sr.UnknownValueError:
                #    print('input not recognized')
                    time.sleep(0.5)
            

    # Listen for input and respond with OpenAI API
    def listen_and_respond(self, source):
         
        while True:
            os.system("sox -n -r 44100 -c 1 beep.wav synth 0.1 sine 1000")
            os.system("aplay beep.wav")
            print("Listening...")
            audio = self.r.listen(source, timeout=10, phrase_time_limit=3)
            try:
                text = self.r.recognize_google(audio)
                print(f"You said: {text}")
                os.system("sox -n -r 44100 -c 1 boop.wav synth 0.1 sine 500")
                os.system(" beep.wav boop.wav")
                if not text:
                    print("No speech detected, returning to wake word listening.")
                    #continue
                    break
                    #return
                else:
                    self.page_switching('QA','you',text)

                # Send input to Gemini API
                api_key = "AIzaSyC5olADq7MxujG6hbSBGBIDQXVKwWge97I"
                prompt = text
                system_instructions = 'You are Cody, a friendly AI desktop pet. ' + \
                                      'You are mostly optimistic, but also easily moody. ' + \
                                      'Please return your mood at the start of your response (#depressed, #joyful, #hungry, #energetic, #sleepy, #curious, #scared) ' + \
                                      'based on user prompt and your own response. ' + \
                                      'Pleas consider the dictionary below' + \
                                      'if !command3 is called, then there is no need to set #emotion' + \
                                      'If you catch any of the commands in the dictionary or anything insinuating these commands, ' + \
                                      'please include the corresponding text in the dictionary below at the start of your response. ' + \
                                      'It should look like !command(number) as well as any arguments that are stated for that command number with &(arg_variable)' +\
                                      'Please note that you are capable of all these commands and ' + \
                                      'should give an affirmative response in present continuous tense should any of these commands occur: e.g. "switching to weather page" or "I am coming"' + \
                                      'Dictionary:'+ \
                                      '  "switch to weather page": "!Command1 &Weather"'+ \
                                      '  "switch to time page": "!Command1 &Time"'+ \
                                      '  "switch to timer page": "!Command1 &Timer"'+ \
                                      '  "switch to photograph page": "!Command1 &Photograph"'+ \
                                      '  "switch to film page": "!Command1 &Film"'+ \
                                      '  "switch to battery page": "!Command1 &Battery"'+ \
                                      '  "switch to todo page": "!Command1 &Todo"'+ \
                                      '  "come to me": "!Command2"'+ \
                                      '  "set emotion to depressed": "!Command3 &depressed"'+ \
                                      '  "set emotion to joyful": "!Command3 &joyful"'+ \
                                      '  "set emotion to hungry": "!Command3 &hungry"'+ \
                                      '  "set emotion to energetic": "!Command3 &energetic"'+ \
                                      '  "set emotion to sleepy": "!Command3 &sleepy"'+ \
                                      '  "set emotion to curious": "!Command3 &curious"'+ \
                                      '  "set emotion to scared": "!Command3 &scared"'+ \
                                      '  "set a timer for x seconds": "!Command4 &(x)&0&0"'+ \
                                      '  "set a timer for x minutes": "!Command4 &0&(x)&0"'+ \
                                      '  "set a timer for x hours": "!Command4 &0&0&(x)"'+ \
                                      '  "set a timer for x minutes and y seconds": "!Command4 &(y)&(x)&0"'+ \
                                      '  "set a timer for x hours and y minutes": "!Command4 &0&(y)&(x)"'+ \
                                      '  "set a timer for x hours, y minutes, and z seconds": "!Command4 &(z)&(y)&(x)"'+ \
                                      '  "add task to todo": "!Command5 &(task)"'+ \
                                      '  "take a photo": "!Command6"'+ \
                                      '  "start recording video": "!Command7"'+ \
                                      '  "start recording video for x seconds": "!Command7 &(x)"'+ \
                                      '  "end recording": "!Command8"',
                
                model = 'gemini-1.5-flash'
                temperature = 0.5
                stop_sequence = ''

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model, system_instruction=system_instructions)
                config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
                response = model.generate_content(contents=[prompt], generation_config=config)
                print("response.text", response.text)
                response_text = self.process_response(response.text)
                print(response_text)
                self.page_switching('QA','Robot', text)

                print("Speaking...")
                #os.system(f"espeak -v en+f3 '{response_text}'")  # Use espeak to say the response
                tts = gTTS(text=response_text, lang='en', slow = False)
                tts.save("output.wav")
                os.system("mpg321 output.wav")
                time.sleep(4)

                if not audio:
                    self.listen_for_wake_word(source)
            except sr.UnknownValueError:
                time.sleep(2)
                print("Silence found, shutting up, listening...")
                self.listen_for_wake_word(source)
                #break
                return
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                os.system(f"espeak 'Could not request results; {e}'")  # Use espeak to say the error
                self.listen_for_wake_word(source)
                #break
                return

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
        emotions = re.findall(emotion_pattern, response_text)
        if command_match:
            command_number = int(command_match.group(1))
            args = re.findall(arg_pattern, response_text)
            if command_number!=3:
                emotions.clear()
            
            
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
                emotion = emotions[0]
                self.set_emotion(emotion)
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
                print('Task added: ' + task_name)
            elif command_number == 6:
                self.take_a_photo()
                print('Photo taken successfully')
            elif command_number == 7:
                seconds_of_video = int(args[0]) if args else None
                self.start_recording(seconds_of_video)
                print(f'Started recording for {seconds_of_video} seconds')
            elif command_number == 8:
                self.end_recording()
                print('Recording ended successfully')

            if emotions and command_number!=3:
                self.set_emotion(emotions[0])
                print('I am ' + str(emotions[0]))
            
            # Remove the processed parts from response_text
            response_text = re.sub(command_pattern, '', response_text)
            response_text = re.sub(arg_pattern, '', response_text)
            response_text = re.sub(emotion_pattern, '', response_text)
        
        # Clean up the remaining text
        leftover_text = response_text.strip()
        
        return leftover_text
