import threading
import time
import random
import math
import os


from value_manager import ValueManager
from pages.pages_utils import theme_colors
from pages.page import Page

# MUST MATCH EmotionHandlerConfig AT EMOTION_HANDLER.PY
class EmotionPageConfig:
    task_2_id = {
        'SHOW_JOYFUL': 1,
        'SHOW_DEPRESSED' : 2,
        'SHOW_HUNGRY': 3,
        'SHOW_ENERGETIC': 4,
        'SHOW_SLEEPY': 5,
        'SHOW_SCARED': 6,
    }
    
    id_2_dir = {
        1: './emotions/joyful',     
        2: './emotions/depressed',  
        3: './emotions/hungry',     
        4: './emotions/energetic',
        5: './emotions/sleepy',     
        6: './emotions/scared'      
    }
    

    id_2_motion = {
        # joyful
        1: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(0),
            'x_angle_displacement': math.radians(15),
            'y_angle_displacement': math.radians(5),
            'x_radius': 12,
            'y_radius': 3,
            'img1_freq': 0.02
            },
        
        # depressed
        2: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(0),
            'x_angle_displacement': math.radians(7),
            'y_angle_displacement': math.radians(5),
            'x_radius': 12,
            'y_radius': 1.5,
            'img1_freq': 0.02
            },
        
        # hungry
        3: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(90),
            'x_angle_displacement': math.radians(7),
            'y_angle_displacement': math.radians(180),
            'x_radius': 12,
            'y_radius': 1.5,
            'img1_freq': 0
            },
        
        # energetic
        4: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(0),
            'x_angle_displacement': math.radians(30),
            'y_angle_displacement': math.radians(30),
            'x_radius': 20,
            'y_radius': 7,
            'img1_freq': 0
            },
        
        # sleepy
        5: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(0),
            'x_angle_displacement': math.radians(7),
            'y_angle_displacement': math.radians(5),
            'x_radius': 12,
            'y_radius': 1.5,
            'img1_freq': 0
            },

        # scared
        6: {
            'x_angle_start': math.radians(0),
            'y_angle_start': math.radians(90),
            'x_angle_displacement': math.radians(60),
            'y_angle_displacement': math.radians(180),
            'x_radius': 20,
            'y_radius': 10,
            'img1_freq': 0
            },
    }
    

class EmotionPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.busy = ValueManager(int(False))
        self.end_display = ValueManager(int(False))
        self.displaying_emotion_id = ValueManager(1)   # Shows 'joyful' as default
        self.display_completed = ValueManager(int(False))


    def reset_states(self, args):
        self.busy.overwrite(int(False))
        self.end_display.overwrite(int(False))
        self.displaying_emotion_id.overwrite(1)
        self.display_completed.overwrite(int(False))

        
    def start_display(self):
        display_thread = threading.Thread(target=self._display)
        display_thread.start()


    def handle_task(self, task_info):       
        if not self.busy.reveal():
            self.busy.overwrite(int(True))
            
            if task_info['task'] == 'SWITCH_PAGE':
                self.end_display.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': task_info['page_key'],
                            'args': task_info['args']
                        }
            
            elif task_info['requester_name'] == 'encoders' and task_info['task'] != 'PAGE_EXPIRED':
                # Go to menu page if encoder is touched
                self.end_display.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'MenuPage',
                            'args': None
                        }
                
            
            # Available to start displaying of a new sequence of frames
            elif task_info['task'] in EmotionPageConfig.task_2_id and not self.displaying_emotion_id.reveal():
                self.displaying_emotion_id.overwrite(EmotionPageConfig.task_2_id[task_info['task']])
                self.busy.overwrite(int(False))
                
                # Send confirmation back to task_queue
                return {
                    'type': 'NEW_TASK',
                    'task': {
                                'requester_name': 'menu_screen',
                                'handler_name': 'emotion',
                                'task': 'EMOTION_RECIEVED',
                                'recieved': task_info['task']
                            }
                }
            else:
                self.busy.overwrite(int(False))


    def _load_frame_paths(self, frame_dir):
        frame_paths = []
        
        for root, dirs, files in os.walk(frame_dir):
            for file in files:
                frame_paths.append(os.path.join(root, file))
        
        frame_paths.sort()        
        return frame_paths
    
    
    def _display(self):
        
        frame_paths, frame_count = None, None
        x_angle, y_angle = 0, 0
        while True:
            
            self.screen.fill_screen(0x0000)
            
            end_display = self.end_display.reveal()
            displaying_emotion_id = self.displaying_emotion_id.reveal()
            
            # Leave display loop if command is so
            if end_display:
                break
            
            # Draw emotion if available
            elif displaying_emotion_id:
                
                # Paths had not been load
                if frame_paths == None or frame_count == None:
                    frame_paths = self._load_frame_paths(EmotionPageConfig.id_2_dir[displaying_emotion_id])
                    frame_count = 0
                    x_angle = EmotionPageConfig.id_2_motion[displaying_emotion_id]['x_angle_start']
                    y_angle = EmotionPageConfig.id_2_motion[displaying_emotion_id]['y_angle_start']
                
                # All frames iterated, reset and change state
                elif frame_count == 30:
                # elif frame_count == len(frame_paths):
                    frame_paths, frame_count = None, None
                    self.displaying_emotion_id.overwrite(0)
                    continue

                # Draw frame and move on to next
                self.screen.draw_image(
                    x=int(math.cos(x_angle) * EmotionPageConfig.id_2_motion[displaying_emotion_id]['x_radius']), 
                    y=int(math.sin(y_angle) * EmotionPageConfig.id_2_motion[displaying_emotion_id]['y_radius']), 
                    width=160, 
                    height=128, 
                    path=frame_paths[1] if (random.random() < EmotionPageConfig.id_2_motion[displaying_emotion_id]['img1_freq']) else frame_paths[0])
                frame_count += 1
                x_angle += EmotionPageConfig.id_2_motion[displaying_emotion_id]['x_angle_displacement']
                y_angle += EmotionPageConfig.id_2_motion[displaying_emotion_id]['y_angle_displacement']
                
                
            self.screen.update()
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))
