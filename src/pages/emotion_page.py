import threading
import time
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
        'SHOW_CURIOUS': 6,
        'SHOW_SCARED': 7,
    }
    
    id_2_dir = {
        1: './emotions/joyful',
        2: './emotions/depressed',
        3: './emotions/hungry',
        4: './emotions/energetic',
        5: './emotions/sleepy',
        6: './emotions/curious',
        7: './emotions/scared'
    }
    

class EmotionPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.busy = ValueManager(int(False))
        self.end_display = ValueManager(int(False))
        self.displaying_emotion_id = ValueManager(0)   # Shows 'joyful' as default
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
        
        frame_paths, current_frame_id = None, None
        while True:
            
            self.screen.fill_screen(theme_colors.Highlight)
            
            end_display = self.end_display.reveal()
            displaying_emotion_id = self.displaying_emotion_id.reveal()
            
            # Leave display loop if command is so
            if end_display:
                break
            
            # Draw emotion if available
            elif displaying_emotion_id:
                
                # Paths had not been load
                if frame_paths == None or current_frame_id == None:
                    frame_paths = self._load_frame_paths(EmotionPageConfig.id_2_dir[displaying_emotion_id])
                    current_frame_id = 0
                
                # All frames iterated, reset and change state
                elif current_frame_id == len(frame_paths):
                    frame_paths, current_frame_id = None, None
                    self.displaying_emotion_id.overwrite(0)
                    continue

                # Draw frame and move on to next
                self.screen.draw_image(
                    x=int(160/2 - 50), 
                    y=int(128/2 - 50) - 15, 
                    width=100, 
                    height=100, 
                    path=frame_paths[current_frame_id],
                    replace_with={
                        (0, 0, 0): theme_colors.Highlight,
                        (255, 255, 255): theme_colors.Primary
                    })
                current_frame_id += 1
                
                self.screen.draw_text(
                    x=50,
                    y=95,
                    text=EmotionPageConfig.id_2_dir[displaying_emotion_id].split('/')[-1],
                    size=15,
                    color=theme_colors.Primary
                )
                
            self.screen.update()
            time.sleep(1)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))