import multiprocessing
import threading
import time
import os
import sqlite3
from picamera2 import Picamera2, Preview


from pages.pages_utils import theme_colors, PageConfig, IconPaths
from value_manager import ValueManager
from pages.page import Page


'''
The drawing is done at lines 175 and 185
the x, y, height, width for draw_image functions may require some change
'''


class PhotographPageConfig:
    TABLE_NAME = 'saved_imgs'
    SAVE_PATH = f'./images/'


class PhotographPageStates:
    SHOW_CURRENT = 0
    SHOW_SAVED = 1
    LEAVE = 2


class PhotographPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        # States
        self.state = ValueManager(PhotographPageStates.SHOW_CURRENT)
        self.prev_state = ValueManager(PhotographPageStates.SHOW_SAVED)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        self.saved_display_id = ValueManager(-1)
        self.saved_len = ValueManager(-1)
        self.max_id = ValueManager(-1)
        
        # Camera
        self.camera = Picamera2()
        config = self.camera.create_video_configuration(main={"size": (160, 128), "format": "RGB888"})
        self.camera.configure(config)
        self.camera.start()
        self.saved_images = None
        self._initiate()
    
    
    def _initiate(self):
        
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        # Get existing images
        self.cursor.execute(
            f'''
            SELECT img_name, img_path 
            FROM {PhotographPageConfig.TABLE_NAME}
            WHERE is_active == 1
            ORDER BY created_at DESC;
            '''
        )
        self.saved_images = self.cursor.fetchall()
        
        # Update parameters
        self.cursor.execute(
            f'''
            SELECT MAX(id)
            FROM {PhotographPageConfig.TABLE_NAME};
            '''
        )
        max_id_data = self.cursor.fetchall()
        if len(self.saved_images) != 0:
            self.max_id.overwrite(max_id_data[0][0])
        self.saved_len.overwrite(len(self.saved_images))
        self.saved_display_id.overwrite(len(self.saved_images) - 1)
        
    def reset_states(self, args):
        self.state.overwrite(PhotographPageStates.SHOW_CURRENT)
        self.prev_state.overwrite(PhotographPageStates.SHOW_SAVED)
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
        self.saved_display_id.overwrite(-1)
        self.saved_len.overwrite(-1)
        self.max_id.overwrite(-1)
        self._initiate()

    
    def start_display(self):
        display_process = threading.Thread(target=self._display)
        display_process.name = 'photo display'
        display_process.start()
    
    
    def handle_task(self, task_info):
        if not self.busy.reveal():

            self.busy.overwrite(int(True))
            
            state = self.state.reveal()
            saved_display_id = self.saved_display_id.reveal()
            saved_len = self.saved_len.reveal()
            
            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                if state == PhotographPageStates.SHOW_SAVED:
                    # Go to next image
                    saved_display_id += 1
                    saved_display_id %= saved_len
                    self.saved_display_id.overwrite(saved_display_id)
            
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                if state == PhotographPageStates.SHOW_SAVED:
                    # Go to previous image
                    saved_display_id -= 1
                    saved_display_id %= saved_len
                    self.saved_display_id.overwrite(saved_display_id)
            
            elif task_info['task'] == 'ENTER_SELECT':
                if state == PhotographPageStates.SHOW_CURRENT:
                    # Toggle states to take picutre and go to show_saved state
                    self.prev_state.overwrite(state)
                    self.state.overwrite(PhotographPageStates.SHOW_SAVED)
                    self.saved_display_id.overwrite(saved_len)
                    self.saved_len.overwrite(saved_len + 1)
            
            elif task_info['task'] == 'OUT_RESUME':
                if state == PhotographPageStates.SHOW_CURRENT:
                    self.state.overwrite(PhotographPageStates.LEAVE)
                    # Leave camera page
                    while True:
                        if self.display_completed.reveal():
                            return 'MenuPage', None
                elif state == PhotographPageStates.SHOW_SAVED:
                    # Resume to show current camera captured footage
                    self.prev_state.overwrite(state)
                    self.state.overwrite(PhotographPageStates.SHOW_CURRENT)

            self.busy.overwrite(int(False))
    
    
    def _display(self):

        #self.conn = sqlite3.connect(PageConfig.DB_PATH)
        #self.cursor = self.conn.cursor()
        
        while True:
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            saved_display_id = self.saved_display_id.reveal()
                
            if state == PhotographPageStates.SHOW_SAVED:
                if prev_state == PhotographPageStates.SHOW_CURRENT:
                    # Take the picture
                    max_id = self.max_id.reveal()
                    img_name = f'img{max_id + 1}.png'
                    self.camera.capture_file(PhotographPageConfig.SAVE_PATH + img_name)

                    # Update the new path to sql table
                    try:
                        self.cursor.execute(
                            f'''
                            INSERT INTO {PhotographPageConfig.TABLE_NAME} (img_name, img_path)
                            VALUES ('{img_name}', '{PhotographPageConfig.SAVE_PATH + img_name}');
                            '''
                        )     
                        self.conn.commit()
                    except Exception as e:
                        print(f'An error ocurred: {e}')
                        
                    # Update parametres
                    self.saved_images.append((img_name, PhotographPageConfig.SAVE_PATH + img_name))
                    self.max_id.overwrite(max_id + 1)

                # Show the last-captured picture
                self.screen.draw_image(0, 0, 160, 128, self.saved_images[saved_display_id][1])
                    
                
            elif state == PhotographPageStates.SHOW_CURRENT:
                if prev_state == PhotographPageStates.SHOW_SAVED:
                    self.saved_display_id.overwrite(self.saved_len.reveal() - 1)
                frame = self.camera.capture_array()
                self.screen.draw_image_from_data(0, 0, 160, 128, frame)
                
            elif state == PhotographPageStates.LEAVE:
                break
            
            self.prev_state.overwrite(state)
            self.screen.update()
            self.screen.clear()
            
            print(f"fps: {self.screen.get_fps()}")
        self.display_completed.overwrite(int(True))        
        
        self.camera.stop()
