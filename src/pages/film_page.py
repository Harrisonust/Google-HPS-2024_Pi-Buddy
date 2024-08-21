import multiprocessing
import time
import sqlite3
# from picamera2 import Picamera2, Preview


from pages.pages_utils import theme_colors, PageConfig, IconPaths
from value_manager import ValueManager
from pages.page import Page


class FilmPageConfig:
    TABLE_NAME = 'saved_imgs'
    SAVE_PATH = f'../images/'


class FilmPageStates:
    SHOW_CURRENT = 0
    SHOW_SAVED = 1
    LEAVE = 2


class FilmPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        # States
        self.state = ValueManager(FilmPageStates.SHOW_CURRENT)
        self.prev_state = ValueManager(FilmPageStates.SHOW_SAVED)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        self.saved_display_id = ValueManager(-1)
        self.saved_len = ValueManager(-1)
        self.max_id = ValueManager(-1)
        
        # Handlers for SQL database
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        # Camera
        self.camera = None
        self.saved_images = None
        self._initiate()
    
    
    def _initiate(self):
        
        # Get existing images
        self.cursor.execute(
            f'''
            SELECT img_name, img_path 
            FROM {FilmPageConfig.TABLE_NAME}
            WHERE is_active == 1
            ORDER BY created_at DESC;
            '''
        )
        self.saved_images = self.cursor.fetchall()
        
        # Update parameters
        self.cursor.execute(
            f'''
            SELECT MAX(id)
            FROM {FilmPageConfig.TABLE_NAME};
            '''
        )
        max_id_data = self.cursor.fetchall()
        self.max_id.overwrite(max_id_data[0][0])
        self.saved_len.overwrite(len(self.saved_images))
        self.saved_display_id.overwrite(len(self.saved_images) - 1)
        
        # Initiate camera
        # self.camera = Picamera2()
    
    
    def reset_states(self, args):
        self.state.overwrite(FilmPageStates.SHOW_CURRENT)
        self.prev_state.overwrite(FilmPageStates.SHOW_SAVED)
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
        self.saved_display_id.overwrite(-1)
        self.saved_len.overwrite(-1)
        self.max_id.overwrite(-1)
        self._initiate()

    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
    
    
    def handle_task(self, task_info):
        if not self.busy.reveal():

            self.busy.overwrite(int(True))
            
            state = self.state.reveal()
            saved_display_id = self.saved_display_id.reveal()
            saved_len = self.saved_len.reveal()
            
            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                if state == FilmPageStates.SHOW_SAVED:
                    saved_display_id += 1
                    saved_display_id %= saved_len
                    self.saved_display_id.overwrite(saved_display_id)
            
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                if state == FilmPageStates.SHOW_SAVED:
                    saved_display_id -= 1
                    saved_display_id %= saved_len
                    self.saved_display_id.overwrite(saved_display_id)
            
            elif task_info['task'] == 'ENTER_SELECT':
                if state == FilmPageStates.SHOW_CURRENT:
                    # Toggle states to take picutre and go to show_saved state
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.SHOW_SAVED)
                    self.saved_display_id.overwrite(saved_len)
                    self.saved_len.overwrite(saved_len + 1)
            
            elif task_info['task'] == 'OUT_RESUME':
                if state == FilmPageStates.SHOW_CURRENT:
                    self.state.overwrite(FilmPageStates.LEAVE)
                    # Leave camera page
                    while True:
                        if self.display_completed.reveal():
                            return 'MenuPage', None
                elif state == FilmPageStates.SHOW_SAVED:
                    # Resume to show current camera captured footage
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.SHOW_CURRENT)

            self.busy.overwrite(int(False))
    
    
    def _display(self):
        while True:
            self.screen.fill_screen(theme_colors.Primary)
            
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            saved_display_id = self.saved_display_id.reveal()
                
            if state == FilmPageStates.SHOW_SAVED:
                if prev_state == FilmPageStates.SHOW_CURRENT:
                    # Take the picture
                    max_id = self.max_id.reveal()
                    img_name = f'img{max_id + 1}.png'
                    # self.camera.start_preview(Preview.NULL)
                    # self.camera.start_and_capture_file(FilmPageConfig.SAVE_PATH + img_name)

                    # Update the new path to sql table
                    try:
                        self.cursor.execute(
                            f'''
                            INSERT INTO {FilmPageConfig.TABLE_NAME} (img_name, img_path)
                            VALUES ('{img_name}', '{FilmPageConfig.SAVE_PATH + img_name}');
                            '''
                        )     
                        self.conn.commit()
                    except Exception as e:
                        print(f'An error ocurred: {e}')
                        
                    # Update parametres
                    self.saved_images.append((img_name, FilmPageConfig.SAVE_PATH + img_name))
                    self.max_id.overwrite(max_id + 1)

                # Show the last-captured picture
                self.screen.draw_image(0, 0, 160, 128, self.saved_images[saved_display_id][1])
                    
                
            elif state == FilmPageStates.SHOW_CURRENT:
                if prev_state == FilmPageStates.SHOW_SAVED:
                    self.saved_display_id.overwrite(self.saved_len.reveal() - 1)
                
                # self.camera.start()
                # frame = self.camera.capture_array()
                # self.camera.stop()
                # self.screen.draw_image_from_data(0, 0, 160, 128, frame)
                
                ###
                self.screen.draw_image(0, 0, 160, 128, '../images/current_image.png')
                ###
            
            elif state == FilmPageStates.LEAVE:
                break
            
            self.prev_state.overwrite(state)
            
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
            
        self.display_completed.overwrite(int(True))        
        