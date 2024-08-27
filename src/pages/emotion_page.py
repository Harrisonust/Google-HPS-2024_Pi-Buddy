import multiprocessing
import time
import os


from value_manager import ValueManager
from pages.pages_utils import theme_colors
from pages.page import Page

# MUST MATCH EmotionHandlerConfig AT EMOTION_HANDLER.PY
class EmotionPageConfig:
    task_2_id = {
        'SHOW_JOYFUL': 7,
        'SHOW_DEPRESSED' : 1,
        'SHOW_HUNGRY': 2,
        'SHOW_ENERGETIC': 3,
        'SHOW_SLEEPY': 4,
        'SHOW_CURIOUS': 5,
        'SHOW_SCARED': 6,
    }
    
    id_2_dir = {
        7: './emotions/depressed',
        1: './emotions/joyful',
        2: './emotions/hungry',
        3: './emotions/energetic',
        4: './emotions/sleepy',
        5: './emotions/curious',
        6: './emotions/scared'
    }
    

class EmotionPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.busy = ValueManager(int(False))
        self.displaying_emotion_id = ValueManager(0)   # Shows 'joyful' as default
        self.display_completed = ValueManager(int(False))


    def reset_states(self, args):
        self.busy.overwrite(int(False))
        self.displaying_emotion_id.overwrite(1)
        self.display_completed.overwrite(int(False))
        
        self.handle_task()

        
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()


    def handle_task(self, task_info):       
        if not self.busy.reveal() and not self.displaying_emotion_id.reveal():
            
            self.busy.overwrite(int(True))
            print('EmotionPage Recieved: ', task_info)
            
            if task_info['requester_name'] == 'encoder':
                # Go to menu page if encoder is touched
                return {
                    'type': 'NEW_PAGE',
                    'page': 'MenuPage',
                    'args': None
                }
                
            if task_info['task'] == 'PAGE_EXPIRED':
                # Ignore page expiration tasks for emotion page
                return None
            
            if task_info['task'] not in EmotionPageConfig.task_2_id:
                # Invalid tasks for emotion page
                raise ValueError(f"Invalid task {task_info} passed to emotion_page")
            
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
            
            displaying_emotion_id = self.displaying_emotion_id.reveal()
            
            # Draw emotion if available
            if displaying_emotion_id:
                
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
                    y=int(128/2 - 50), 
                    width=100, 
                    height=100, 
                    path=frame_paths[current_frame_id],
                    replace_with={
                        (0, 0, 0): theme_colors.Highlight,
                        (255, 255, 255): theme_colors.Primary
                    })
                current_frame_id += 1
                    
                
            self.screen.update()
            time.sleep(1)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))