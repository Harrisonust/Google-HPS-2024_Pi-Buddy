import time
import os
import time
import speech_recognition as sr
import numpy as np
import google.generativeai as genai
import command_handler

from handlers.handler import Handler
from value_manager import ValueManager
from handlers.handler import Handler
from value_manager import ValueManager




class AudioHandler(Handler):
    
    def __init__(self, task_queue):
        self.run_input_process = True
        self.task_queue = task_queue
        self.r = sr.Recognizer()  # Set up the speech recognition engine
        self.greetings = [
            "Hello! What can I do for you today?",
            "yeah?",
            "Hello there",
            "Hi, how can I assist you?"
        ]

    def listen(self):
        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            print("Listening for 'Hey'...")
            self.listen_for_wake_word(source)
    
    # Listen for the wake word "hey"
    def listen_for_wake_word(self, source):
        print("Listening for 'Hey'...")

        while True:
            print("Adjusting for ambient noise, please wait...")
            self.r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            audio = self.r.listen(source)
            try:
                text = self.r.recognize_google(audio)
                if "hey" in text.lower():
                    print("Wake word detected.")
                    response_text = np.random.choice(self.greetings)
                    print(response_text)
                    os.system(f"espeak -v en+f3 '{response_text}'")  # Use espeak to say the greeting
                    self.listen_and_respond(source)
            except sr.UnknownValueError:
                pass
            time.sleep(0.5)

    # Listen for input and respond with OpenAI API
    def listen_and_respond(self, source):
        print("Listening...")

        while True:
            audio = self.r.listen(source)
            try:
                text = self.r.recognize_google(audio)
                print(f"You said: {text}")
                if not text:
                    continue

                # Send input to Gemini API
                api_key = "AIzaSyC5olADq7MxujG6hbSBGBIDQXVKwWge97I"
                prompt = 'hi cody'
                system_instructions = 'You are Cody, a friendly AI desktop pet. ' + \
                                      'You are mostly optimistic, but also easily moody. ' + \
                                      'Please return your mood at the start of your response (#depressed, #joyful, #hungry, #energetic, #sleepy, #curious, #scared) ' + \
                                      'based on user prompt and your own response. ' + \
                                      'if !command3 is called, then there is no need to set #emotion' + \
                                      'If you catch any of the following commands or anything insinuating these commands, ' + \
                                      'please return "!Command" + command number at the start of your response. ' + \
                                      'as well as any arguments that are stated for that command number with &arg_variable}' +\
                                      'Please note that you are capable of all these commands and ' + \
                                      'should give an affirmative response should any of these commands occur: ' + \
                                      '  "switch to weather page": "!Command1 &weather"'+ \
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
                                      '  "set a timer for x seconds": "!Command4 &{x}&0&0"'+ \
                                      '  "set a timer for x minutes": "!Command4 &0&{x}&0"'+ \
                                      '  "set a timer for x hours": "!Command4 &0&0&{x}"'+ \
                                      '  "set a timer for x minutes and y seconds": "!Command4 &{y}&{x}&0"'+ \
                                      '  "set a timer for x hours and y minutes": "!Command4 &0&{y}&{x}"'+ \
                                      '  "set a timer for x hours, y minutes, and z seconds": "!Command4 &{z}&{y}&{x}"'+ \
                                      '  "add task to todo": "!Command5 &{task}"'+ \
                                      '  "take a photo": "!Command6"'+ \
                                      '  "start recording video": "!Command7"'+ \
                                      '  "start recording video for x seconds": "!Command7 &{x}"'+ \
                                      '  "end recording": "!Command8"',
                
                model = 'gemini-1.5-flash'
                temperature = 0.5
                stop_sequence = ''

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model, system_instruction=system_instructions)
                config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
                response = model.generate_content(contents=[prompt], generation_config=config)
                response_text = command_handler.process_response(response.text)
                print(response_text)

                print("Speaking...")
                os.system(f"espeak -v en+f3 '{response_text}'")  # Use espeak to say the response

                if not audio:
                    self.listen_for_wake_word(source)
            except sr.UnknownValueError:
                time.sleep(2)
                print("Silence found, shutting up, listening...")
                self.listen_for_wake_word(source)
                break
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                os.system(f"espeak 'Could not request results; {e}'")  # Use espeak to say the error
                self.listen_for_wake_word(source)
                break

    