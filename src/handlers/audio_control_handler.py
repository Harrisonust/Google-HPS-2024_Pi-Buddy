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