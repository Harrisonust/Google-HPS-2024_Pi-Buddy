import multiprocessing
import threading
import time
import sqlite3

from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

from pages.pages_utils import theme_colors, PageConfig, IconPaths
from value_manager import ValueManager
from pages.page import Page
import cv2

'''
The drawing is done at lines 222 & 251 & 257 & 275
the x, y, height, width for draw_image functions may require some change
'''


class FilmPageConfig:
    TABLE_NAME = 'saved_videos'
    SAVE_PATH = f'./videos/'


class FilmPageStates:
    SHOW_CURRENT = 0
    RECORD_CURRENT = 1
    END_RECORD = 2
    SHOW_SAVED = 3
    PLAY_SAVED = 4
    LEAVE = 5


class FilmPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        # States
        self.state = ValueManager(FilmPageStates.SHOW_CURRENT)
        self.prev_state = ValueManager(FilmPageStates.SHOW_SAVED)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        self.saved_display_id = ValueManager(-1)
        self.prev_saved_display_id = ValueManager(-1)
        self.saved_len = ValueManager(-1)
        self.max_id = ValueManager(-1)
        
        

        # Camera
        self.saved_videos = None
        self._initiate()
   

    def _initiate(self):
        
        # Handlers for SQL database
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        # Get existing images
        self.cursor.execute(
            f'''
            SELECT video_name, video_path 
            FROM {FilmPageConfig.TABLE_NAME}
            WHERE is_active == 1
            ORDER BY created_at DESC;
            '''
        )
        self.saved_videos = self.cursor.fetchall()
        
        # Update parameters
        self.cursor.execute(
            f'''
            SELECT MAX(id)
            FROM {FilmPageConfig.TABLE_NAME};
            '''
        )
        max_id_data = self.cursor.fetchall()
        if len(self.saved_videos) != 0: 
            self.max_id.overwrite(max_id_data[0][0])
        self.saved_len.overwrite(len(self.saved_videos))
        self.saved_display_id.overwrite(len(self.saved_videos) - 1)
        
    
    
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
            
            # Get current states
            state = self.state.reveal()
            saved_display_id = self.saved_display_id.reveal()
            saved_len = self.saved_len.reveal()
            
            # Write states by current states
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
                    # Toggle states to record video and go to show_saved state
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.RECORD_CURRENT)
                    self.saved_display_id.overwrite(saved_len)
                    self.saved_len.overwrite(saved_len + 1)
                elif state == FilmPageStates.RECORD_CURRENT:
                    # Start recording video
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.END_RECORD)
                elif state == FilmPageStates.SHOW_SAVED:
                    # Start playing video
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.PLAY_SAVED)
                elif state == FilmPageStates.PLAY_SAVED:
                    # End playing video
                    self.prev_state.overwrite(state)
                    self.state.overwrite(FilmPageStates.SHOW_SAVED)
            
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
    
    
    def _record_video(self, file_path_tuple):
        # Record video; executed as a separate process
        encoder = H264Encoder(1000000)
        file_path = FfmpegOutput(file_path_tuple)
        self.camera.start_recording(encoder, output=file_path)
        print(f"start recording {file_path_tuple}")
        while self.state.reveal() == FilmPageStates.RECORD_CURRENT:
            time.sleep(0.1)
        self.camera.stop_recording()
        self.state.overwrite(FilmPageStates.SHOW_SAVED)
    
    def _capture_first_frame(self, filepath):
        # Returns the first frame of the video as a numpy array
        video_capture = cv2.VideoCapture(filepath)
        if not video_capture.isOpened():
            raise Exception(f"Error: could not open video file '{filepath}'")
        _, frame = video_capture.read()
        video_capture.release()
        return frame
    
    def _initiate_play_saved(self, filepath):
        # Gets fps and initiates the video_capture handle for playing saved videos
        video_capture = cv2.VideoCapture(filepath)
        if not video_capture.isOpened():
            raise Exception(f"Error: could not open video file '{filepath}'")
        
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        return video_capture, fps, total_frames

    
    def _terminate_play_saved(self, video_capture):
        video_capture.release()
    
    
    def _display(self):
        
        # Initiate camera
        self.camera = Picamera2()
        config = self.camera.create_video_configuration(main={'size': (160, 128), "format": "RGB888"})
        self.camera.configure(config)
        
        self.camera.start()
        
        # Handlers for SQL database
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        # For SHOW_SAVED
        first_frame = None
        
        # For PLAY_SAVED
        video_start_time, video_capture, fps, total_frames = None, None, None, None
        

        while True:
            self.screen.fill_screen(theme_colors.Primary)
            
            # Get current states
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            saved_display_id = self.saved_display_id.reveal()
            prev_saved_display_id = self.prev_saved_display_id.reveal()
            
            # Perform operations on components based on states
            if state == FilmPageStates.SHOW_CURRENT:
                print("show current")
                # Reset display_id to last last taken video
                if prev_state == FilmPageStates.SHOW_SAVED:
                    self.saved_display_id.overwrite(self.saved_len.reveal() - 1)
                
                # Display current camera captured footage
                frame = self.camera.capture_array()
                self.screen.draw_image_from_data(0, 0, 160, 128, frame)
                
            elif state == FilmPageStates.RECORD_CURRENT:
                print("record current")
                if prev_state == FilmPageStates.SHOW_CURRENT:
                    # Update parametres
                    max_id = self.max_id.reveal()
                    video_name = f'img{max_id + 1}.mp4'
                    video_path = FilmPageConfig.SAVE_PATH + video_name
                    self.saved_videos.append((video_name, video_path))
                    self.max_id.overwrite(max_id + 1)
                    print(f"243 {video_path}")
                    # Update the new path to sql table
                    try:
                        self.cursor.execute(
                            f'''
                            INSERT INTO {FilmPageConfig.TABLE_NAME} (video_name, video_path)
                            VALUES ('{video_name}', '{video_path}');
                            '''
                        )     
                        self.conn.commit()
                    except Exception as e:
                        print(f'An error ocurred: {e}')
                        
                    # Record the video
                    recording_process = threading.Thread(target=self._record_video, args=(video_path,))
                    recording_process.start()
                
                # Display the current captured footage
                frame = self.camera.capture_array()
                self.screen.draw_image_from_data(0, 0, 160, 128, frame)
                self.screen.draw_circle(150, 10, 6, color=theme_colors.Danger) 
            
            elif state == FilmPageStates.SHOW_SAVED:
                print("show saved")
                # Show the last-captured picture
                if first_frame is None or prev_saved_display_id != saved_display_id:
                    first_frame = self._capture_first_frame(self.saved_videos[saved_display_id][1])
                self.screen.draw_image_from_data(0, 0, 160, 128, first_frame)
            
            elif state == FilmPageStates.PLAY_SAVED:
                print("play saved")
                if prev_state == FilmPageStates.SHOW_SAVED:
                    video_capture, fps, total_frames = self._initiate_play_saved(self.saved_videos[saved_display_id][1])
                    video_start_time = time.time()
                
                video_played_time = time.time() - video_start_time
                frame_number = int(fps * video_played_time)
                print(frame_number, total_frames)
                
                if frame_number >= total_frames:
                    # End state PLAY_SAVED if the video is done
                    self._terminate_play_saved(video_capture)
                    self.state.overwrite(FilmPageStates.SHOW_SAVED)
                else:
                    # Get video frame
                    video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    _, frame = video_capture.read()
                    print(frame.shape)
                    self.screen.draw_image_from_data(0, 0, 160, 128, frame)
                
            
            elif state == FilmPageStates.LEAVE:
                break
            
            # Overwrite previous state with current state
            self.prev_state.overwrite(state)
            self.prev_saved_display_id.overwrite(saved_display_id)
            
            # Update screen
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
            
        self.display_completed.overwrite(int(True))        
        
        #self.camera.stop()
        self.camera.close()

