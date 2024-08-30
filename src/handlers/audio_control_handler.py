import re
class AudioControlHandler():

	def page_switching(page:str, args=None): 
		# 'page' is a parameter that tells what page is to be switched next
		# page: 'Weather', 'Time', 'Timer' (args=(seconds_to_count_down:int or None)), 'Photograph', 'Film' (args=(seconds_of_videos:int or None)), 'Battery', 'Todo'
		pass	
 
	def call_and_come(): 
		# this function has no parameters, and performs the call and come procedure when called
		pass

	def set_emotion(emotion:str):
		# emotion: 'depressed', 'joyful', 'hungry', 'energetic', 'sleepy', 'curious', 'scared'
		pass

	def set_count_down_timer(seconds_to_count_down:int=None, minutes_to_count_down:int=None, hours_to_count_down:int=None):
		# either one of the parameters cannot be None
		pass

	def add_todo(task_name:str):
		# add todo task to todo list
		pass

	def take_a_photo():
		# take a photo and show the photo afterwards
		pass

	def start_recording(seconds_of_video_to_record:int=None):
		# if no 'seconds_of_video_to_record' is specified, the recording will not stop until end_recording is called
		pass

	def end_recording():
		# ends recording
		pass
	
    def process_response(response_text: str):
    # Regular expressions to find !CommandX, &args, and #{emotion}
    command_pattern = r"!Command(\d+)"
    arg_pattern = r"&(\w+)"
    emotion_pattern = r"#(\w+)"
    
    # Find and process command
    command_match = re.search(command_pattern, response_text)
    if command_match:
        command_number = int(command_match.group(1))
        args = re.findall(arg_pattern, response_text)
        emotions = re.findall(emotion_pattern, response_text)
        
        # Call the appropriate command function based on command_number
        if command_number == 1:
            page = args[0] if args else None
            additional_args = args[1:] if len(args) > 1 else None
            page_switching(page, additional_args)
        elif command_number == 2:
            call_and_come()
        elif command_number == 3:
            emotion = args[0] if args else None
            set_emotion(emotion)
        elif command_number == 4:
            seconds = int(args[0]) if len(args) > 0 else None
            minutes = int(args[1]) if len(args) > 1 else None
            hours = int(args[2]) if len(args) > 2 else None
            set_count_down_timer(seconds, minutes, hours)
        elif command_number == 5:
            task_name = args[0] if args else None
            add_todo(task_name)
        elif command_number == 6:
            take_a_photo()
        elif command_number == 7:
            seconds_of_video = int(args[0]) if args else None
            start_recording(seconds_of_video)
        elif command_number == 8:
            end_recording()

        if emotions:
            set_emotion(emotions[0])
        
        # Remove the processed parts from response_text
        response_text = re.sub(command_pattern, '', response_text)
        response_text = re.sub(arg_pattern, '', response_text)
        response_text = re.sub(emotion_pattern, '', response_text)
    
    # Clean up the remaining text
    leftover_text = response_text.strip()
    
    return leftover_text
