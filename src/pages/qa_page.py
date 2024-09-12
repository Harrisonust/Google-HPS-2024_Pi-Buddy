import multiprocessing
import time

from pages.pages_utils import theme_colors, PageConfig, Text
from value_manager import ValueManager
from pages.page import Page


class QAPageConfig():
    USER_COLOR = theme_colors.Contrast
    ROBOT_COLOR = theme_colors.Info
    
    TEXT_X = 5
    TEXT_Y = 5
    TEXT_SIZE = 15 
    TEXT_LINE_CHR_COUNT = 20
    TEXT_LINE_HEIGHT = 21


class QAText():
    def __init__(self, screen):
        self.screen = screen
        self.who = None
        self.what = None
        self.text_components = None
        
    
    def reset(self, who, what):
        self.who = who
        self.what = what
        self._build_text_components()
    
        
    def _build_text_components(self):
        self.text_components = []
        current_y = QAPageConfig.TEXT_Y
        if self.what != None:
            current_line = ''
            for c in self.what:
                if len(current_line) == QAPageConfig.TEXT_LINE_CHR_COUNT:
                    self.text_components.append(
                        Text(
                            screen=self.screen,
                            text=current_line,
                            text_size=QAPageConfig.TEXT_SIZE,
                            color=QAPageConfig.USER_COLOR if (self.who == 'user') else QAPageConfig.ROBOT_COLOR,
                            x_marking=QAPageConfig.TEXT_X,
                            y_marking=current_y
                        )
                    )
                    current_y += QAPageConfig.TEXT_LINE_HEIGHT
                    current_line = ''
                    if c != ' ':
                        current_line += '-'
                        current_line += c
                else:
                    current_line += c
            self.text_components.append(
                Text(
                    screen=self.screen,
                    text=current_line,
                    text_size=QAPageConfig.TEXT_SIZE,
                    color=QAPageConfig.USER_COLOR if (self.who == 'user') else QAPageConfig.ROBOT_COLOR,
                    x_marking=QAPageConfig.TEXT_X,
                    y_marking=current_y
                )
            )
        
    def draw(self):
        for text_component in self.text_components:
            text_component.draw()
            
            

class QAPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.qa_text = QAText(self.screen)
        
        self.busy = ValueManager(int(False))
        self.leave = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
    
    
    def reset_states(self, args):
        self.qa_text.reset(args['who'], args['what'])
        self.display_completed.overwrite(int(False))
        self.leave.overwrite(int(False))
        self.busy.overwrite(int(False))
    
    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
 
    
    def handle_task(self, task_info):
        if not self.busy.reveal():
            self.busy.overwrite(int(True))
            print(task_info)
            '''
            if task_info['task'] == 'PAGE_EXPIRED':
                self.leave.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'EmotionPage',
                            'args': None,
                        }
            '''
            if task_info['task'] == 'SWITCH_PAGE':
                self.leave.overwrite(int(True))
                print("helloworld")
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': task_info['page_key'],
                            'args': task_info['args'],
                        }
            
            elif task_info['requester_name'] == 'encoders' and task_info['task'] != 'PAGE_EXPIRED':
                self.leave.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'MenuPage',
                            'args': None, 
                        }
            
            self.busy.overwrite(int(False))
 
    
    def _display(self):
        while True:
            self.screen.fill_screen(theme_colors.Primary)
            
            if self.leave.reveal():
                break
            
            self.qa_text.draw()
            
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
    
        self.display_completed.overwrite(int(True))
