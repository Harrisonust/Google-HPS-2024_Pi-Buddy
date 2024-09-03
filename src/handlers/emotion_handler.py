import time
import sys
import requests
import random
import multiprocessing
from datetime import datetime


from handlers.handler import Handler
from value_manager import ValueManager


class EmotionHandlerConfig:
    URL = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001'
    STATION_ID = 'C0D680'
    AUTHORIZATION = 'CWA-223E922B-B77E-4E5D-BFF2-9DE9D5BB7A57'

    # MUST MATCH EmotionPageConfig AT EMOTION_PAGE.PY
    emotion_2_key = {
        'joyful': 1,
        'depressed': 2,
        'hungry': 3,
        'energetic': 4,
        'sleepy': 5,
        'curious': 6,
        'scared': 7
    }
    key_2_emotion = {
        1: 'joyful',
        2: 'depressed',
        3: 'hungry',
        4: 'energetic',
        5: 'sleepy',
        6: 'curious',
        7: 'scared'
    }
    

class EmotionHandler(Handler):
    def __init__(self, task_queue):
        
        self.run_input_process = True
        self.task_queue = task_queue
        
        self.depressed = ValueManager(int(False))
        self.joyful = ValueManager(int(True))       # The robot is joyful as default
        self.hungry = ValueManager(int(False))
        self.energetic = ValueManager(int(False))
        self.sleepy = ValueManager(int(False))
        self.curious = ValueManager(int(True))      # The robot is curious as default
        self.scared = ValueManager(int(False))      # NOTHING WRITTEN TO TRIGGER YET
        
        
        # The prioritized_emotion keeps id of a emtoin (as listed in emotion_2_key) to show;
        # the emotion will be shown regardless of the value of its corresponding state variable;
        # however, 'hungry' always overrides; prioritized_emotion will be shown AFTER 'hungry' if
        # 'hungry' is True 
        self.prioritized_emotion = ValueManager(-1)  
        self.busy = ValueManager(int(False))
        self.emotion_key = ValueManager(EmotionHandlerConfig.emotion_2_key['joyful'])   # The emotion sent to task_queue
        
        observe_process = multiprocessing.Process(target=self._observe_time_weather)
        observe_process.start()

    
    def _observe_time_weather(self):
        while True:
            
            # Get time
            current_datetime = datetime.now()
            day = current_datetime.strftime("A")
            hour = int(current_datetime.strftime("%H"))
            
            # Get weather
            params = {
                'Authorization': EmotionHandlerConfig.AUTHORIZATION,
                'StationId': EmotionHandlerConfig.STATION_ID,
            }
            
            response = requests.get(EmotionHandlerConfig.URL, params=params)
            if response.status_code != 200:
                raise ValueError('unable to get weather data')
            
            data = response.json()
            sys.stdout.reconfigure(encoding='utf-8')
            location_data = data['records']['Station'][0]
            weather = location_data['WeatherElement']['Weather']
            
            
            # 'depressed' is updated by wether it's monday or raining
            if day == 'Monday' or '陰' in weather:
                self.depressed.overwrite(int(True))
            else:
                self.depressed.overwrite(int(False))
            
            # 'joyful' is updated by wether it's sunny
            if '晴' in weather:
                self.joyful.overwrite(int(True))
            else:
                self.joyful.overwrite(int(False))
                
            # 'sleepy' is updated True at late night or early mornings
            if hour >= 22 or hour <= 7:
                self.sleepy.overwrite(int(True))
            else:
                self.sleepy.overwrite(int(False))
            
            # 'energetic' is updated True at Saturdays and Sundays
            if day == 'Saturday' or day == 'Sunday':
                self.energetic.overwrite(int(True))
            else:
                self.energetic.overwrite(int(False))
            
            # Updates every minutes
            time.sleep(60)
            
            
    def listen(self):
        # Sends the current emotion as task to task queue once per
        while True:
            self.task_queue.append({
                'requester_name': 'emotion',
                'handler_name': 'menu_screen',
                'task': f'SHOW_{EmotionHandlerConfig.key_2_emotion[self.emotion_key.reveal()].upper()}'
            })
            time.sleep(1)
    
    
    
    def _get_new_emotion_key(self):
        # Priority-wise: 'hungry' > 'prioritized_emotion' > 'scared' > 'curious' == 'depressed' == 'joyful' == 'energetic' == 'sleepy'
        
        new_emotion = 'joyful'
        
        # 'hungry' 
        if self.hungry.reveal():
            new_emotion = 'hungry'
            self.hungry.overwrite(int(False))   # Will be updated again by battery handler in 1 minute
        
        # 'prioritized_emotion'
        elif self.prioritized_emotion.reveal() != -1:
            new_emotion = EmotionHandlerConfig.key_2_emotion[self.prioritized_emotion.reveal()]
            self.prioritized_emotion.overwrite(-1)
            
        # 'scared'
        elif self.scared.reveal():
            new_emotion = 'scared'
            self.scared.overwrite(int(False))
        
        # 'curious', 'depressed', 'joyful', 'energetic', 'sleepy'
        else:
            lottery_box = []
            if self.curious.reveal():
                lottery_box.append('curious')
            if self.depressed.reveal():
                lottery_box.append('depressed')
            if self.joyful.reveal():
                lottery_box.append('joyful')
            if self.energetic.reveal():
                lottery_box.append('energetic')
            if self.sleepy.reveal():
                lottery_box.append('sleepy')
            
            if lottery_box:
                random.shuffle(lottery_box)
                new_emotion = lottery_box[0]
            # 'depressed', 'joyful', 'energetic', 'sleepy' are updated in observe_time_weather
            # therefore, no overwrite-s here

        return EmotionHandlerConfig.emotion_2_key[new_emotion]
    
    
    
    def handle_task(self, task_info):
        if not self.busy.reveal():
            # print('EmotionHandler Recieved: ', task_info)

            self.busy.overwrite(int(True))
            
            hungry = self.hungry.reveal()
            
            # 'hungry' is updated by the battery state sent as task from battery_handler
            if task_info['task'] == 'UPDATE_BATTERY_STATE':
                if (task_info['battery_level'] < 20 and 
                    task_info['battery_charging'] == False and
                    hungry == False):
                    self.hungry.overwrite(int(True))
                elif hungry == True:
                    self.hungry.overwrite(int(False))
            
            elif task_info['task'] == 'SET_EMOTION':
                self.prioritized_emotion.overwrite(EmotionHandlerConfig.emotion_2_key[task_info['args']])
            
            # Update emotion when the previous one had been received
            elif task_info['task'] == 'EMOTION_RECIEVED':
                new_emotion_key = self._get_new_emotion_key()
                self.emotion_key.overwrite(new_emotion_key)
            
               
            self.busy.overwrite(int(False))