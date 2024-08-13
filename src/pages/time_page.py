from datetime import datetime
import multiprocessing
import time


from value_manager import ValueManager
from pages.pages_utils import theme_colors
from pages.page import Page


class TimePageStates():
    IDLE = 0
    EXITING = 1


class TimePageConfig:
    BACKGROUND_COLOR = theme_colors.Primary
    
    DAY_X = 20
    DAY_Y = 30
    DAY_TEXT_SIZE = 11
    DAY_COLOR = theme_colors.Info
    
    TIME_X = 17
    TIME_Y = 50
    TIME_TEXT_SIZE = 25
    TIME_COLOR = theme_colors.Highlight
    
    DATE_X = 30
    DATE_Y = 90
    DATE_TEXT_SIZE = 14
    DATE_COLOR = theme_colors.Muted
    

class DateTime():
    def __init__(self, screen):
        self.screen = screen
        
    def draw(self):
        current_datetime = datetime.now()
        
        formatted_day_str = f'Happy {current_datetime.strftime("%A")}, it\'s'
        formatted_time_str = current_datetime.strftime("%H : %M : %S")
        formatted_date_str = current_datetime.strftime('%B %d, %Y')
        
        # draw_text(self, x, y, text, size, color=None)
        self.screen.draw_text(TimePageConfig.DAY_X, TimePageConfig.DAY_Y, formatted_day_str,
                              TimePageConfig.DAY_TEXT_SIZE, TimePageConfig.DAY_COLOR)
        self.screen.draw_text(TimePageConfig.TIME_X, TimePageConfig.TIME_Y, formatted_time_str,
                              TimePageConfig.TIME_TEXT_SIZE, TimePageConfig.TIME_COLOR)
        self.screen.draw_text(TimePageConfig.DATE_X, TimePageConfig.DATE_Y, formatted_date_str,
                              TimePageConfig.DATE_TEXT_SIZE, TimePageConfig.DATE_COLOR)


class TimePage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.date_time_components = DateTime(self.screen)
        
        self.state = ValueManager(TimePageStates.IDLE)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        
        
    def reset_states(self, args):
        self.state.overwrite(TimePageStates.IDLE)
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
    
    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
    
    
    def handle_task(self, task_info):
        if not self.busy.reveal():
            
            self.busy.overwrite(int(True))
            
            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                pass
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                pass
            elif task_info['task'] == 'ENTER_SELECT':
                pass
            elif task_info['task'] == 'OUT_RESUME':
                self.state.overwrite(TimePageStates.EXITING)
                while True:
                    if self.display_completed.reveal():
                        return 'MenuPage', None

            self.busy.overwrite(int(False))
        
        
    def _display(self):
        print('in display')
        while True:
            
            state = self.state.reveal()
            if state == TimePageStates.EXITING:
                break
            
            self.screen.fill_screen(TimePageConfig.BACKGROUND_COLOR)
            
            # self.screen.draw_vertical_line(80, 0, 128)
            # self.screen.draw_horizontal_line(0, 64, 160)
            
            self.date_time_components.draw()
            self.screen.update()
            time.sleep(0.5)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))