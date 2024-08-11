import time
import multiprocessing


from pages.pages_utils import theme_colors, PageConfig, Text, IconTextBox
from value_manager import ValueManager
       
 
class SetTimerPageConfig():
    ICON_TRUE_COLOR = PageConfig.ICON_TRUE_COLOR
    ICON_FALSE_COLOR = PageConfig.ICON_FALSE_COLOR
    TITLE_COLOR = PageConfig.TITLE_COLOR
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR
    BACKGROUND_COLOR = PageConfig.BACKGROUND_COLOR
    
    TIME_DIGIT_Y_RATIO = 0.5
    
    # Time digit coordinates
    TIME_DIGIT_TEXT_SIZE = 25
    TIME_DIGIT_HR_H_X = 25
    TIME_DIGIT_HR_L_X = 40
    TIME_DIGIT_MIN_H_X = 65
    TIME_DIGIT_MIN_L_X = 80
    TIME_DIGIT_SEC_H_X = 105
    TIME_DIGIT_SEC_L_X = 120
    
    # Time digit text
    TIME_DIGIT_TEXT_COL0_X = 55
    TIME_DIGIT_TEXT_COL1_X = 95
    
    # Title box
    TITLE_X = 80
    TITLE_Y = 20
    TITLE_BOX_WIDTH = PageConfig.ICON_TEXT_BOX_WIDTH             
    TITLE_BOX_HEIGHT = PageConfig.ICON_TEXT_BOX_HEIGHT            
    TITLE_TEXT_SIZE = PageConfig.ICON_TEXT_BOX_TEXT_SIZE 
    TITLE_ICON_Y_RATIO = PageConfig.ICON_TEXT_BOX_ICON_Y_RATIO            
    TITLE_ICON_X_MARGIN = PageConfig.ICON_TEXT_BOX_ICON_X_MARGIN   
    TITLE_ICON_COLOR_REPLACEMENTS = {
        ICON_TRUE_COLOR: TITLE_COLOR,
        ICON_FALSE_COLOR: BACKGROUND_COLOR
    }
    
    # Message to users
    MSG_X = 30
    MSG_Y = 90
    MSG_TEXT_SIZE = 15
    MSG_COLOR = theme_colors.Warning
    
    

class TimeDigitConfig():
    DEFAULT_NUM = 0
    TEXT_SIZE = SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR
    HOVERED_COLOR = PageConfig.HOVERED_COLOR
    ON_CHANGE_COLOR = theme_colors.Danger
    
    
class TimeDigit(Text):
    def __init__(self, screen, center_x, center_y, num_max_exclusive):
        self.num = TimeDigitConfig.DEFAULT_NUM
        self.text_size = TimeDigitConfig.TEXT_SIZE
        self.default_color = TimeDigitConfig.DEFAULT_COLOR
        self.hovered_color = TimeDigitConfig.HOVERED_COLOR
        self.on_change_color = TimeDigitConfig.ON_CHANGE_COLOR
        
        self.screen = screen
        self.num_max_exclusive = num_max_exclusive

        super().__init__(
             self.screen, str(self.num), self.text_size, self.default_color, 
             center_x, center_y, x_mark_edge='Left', y_mark_edge='Center'
        )
         
        '''
        class Text:
            instances:  self.display, self.screen, self.text, self.text_size, self.color, self.x, self.y
            attributes: self.draw()
        '''        
    
    def hover(self):
        self.color = self.hovered_color
    
    def unhover(self):
        self.color = self.default_color
        
    def select(self):
        self.color = self.on_change_color
        
    def unselect(self):
        self.color = self.hovered_color
    
    def change_value(self, change):
        self.num = (self.num + change) % self.num_max_exclusive
        self.text = str(self.num)


class SetTimerPageState():
    HOVER = 0
    SELECT = 1
    TO_DISCARD = 2
    TO_PROCEED = 3


class SetTimerPage():
    def __init__(self, screen):
        self.screen = screen
        
        self.background_color = SetTimerPageConfig.BACKGROUND_COLOR

        self.time_digit_count = 6
        self.time_digit_components = None
        self.title_box = None
        self.text_components = None
        self.proceed_message = None
        self.discard_message = None
        self._initiate_components()
        
        
        self.set_timer_page_busy = ValueManager(int(False))
        self.state = ValueManager(SetTimerPageState.HOVER)
        self.prev_state = ValueManager(SetTimerPageState.HOVER)
        self.hover_id = ValueManager(0)
        self.prev_hover_id = ValueManager(0)
        self.change_time_digit_val = ValueManager(0)
        
        self.time_digit_components[self.hover_id.reveal()].hover()
        
        # Start display process for set timer page
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
        
    def handle_task(self, task_info):
        if not self.set_timer_page_busy.reveal():
            
            self.set_timer_page_busy.overwrite(int(True))
            state = self.state.reveal()
            hover_id = self.hover_id.reveal()

            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                if state == SetTimerPageState.HOVER:
                    # Move hover to next digit
                    hover_id = (hover_id - 1) % self.time_digit_count
                    self.hover_id.overwrite(hover_id)
                elif state == SetTimerPageState.SELECT:
                    # Decrease digit value by 1
                    self.change_time_digit_val.overwrite(-1)
                
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                if state == SetTimerPageState.HOVER:
                    # Move hover to previous digits
                    hover_id = (hover_id + 1) % self.time_digit_count
                    self.hover_id.overwrite(hover_id)
                elif state == SetTimerPageState.SELECT:
                    # Increase digit value by 1      
                    self.change_time_digit_val.overwrite(1)      
            
            elif task_info['task'] == 'ENTER_SELECT':
                if state == SetTimerPageState.HOVER:
                    self.state.overwrite(SetTimerPageState.SELECT)
                elif state == SetTimerPageState.TO_DISCARD:
                    self.state.overwrite(SetTimerPageState.HOVER)
                elif state == SetTimerPageState.TO_PROCEED:
                    return 'TimerStart'
                
            elif task_info['task'] == 'OUT_RESUME':
                if state == SetTimerPageState.HOVER:
                    self.state.overwrite(SetTimerPageState.TO_DISCARD)
                elif state == SetTimerPageState.SELECT:
                    self.state.overwrite(SetTimerPageState.HOVER)
                elif state == SetTimerPageState.TO_DISCARD:
                    return 'Menu'
            
            self.set_timer_page_busy.overwrite(int(False))
    
    
    def _initiate_components(self):
        time_digit_y = self.screen.get_row_dim() * SetTimerPageConfig.TIME_DIGIT_Y_RATIO

        self.time_digit_components = [
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_HR_H_X, time_digit_y, 10),     # Hour-higher-digit
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_HR_L_X, time_digit_y, 10),     # Hour-lower-digit
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_MIN_H_X, time_digit_y, 6),     # Minute-higher-digit
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_MIN_L_X, time_digit_y, 10),    # Minute-lower-digit
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_SEC_H_X, time_digit_y, 6),     # Second-higher-digit
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_SEC_L_X, time_digit_y, 10),    # Second-lower-digit
        ]
        
        self.text_components = [
            Text(self.screen, ':', SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE, SetTimerPageConfig.DEFAULT_COLOR, 
                 SetTimerPageConfig.TIME_DIGIT_TEXT_COL0_X, time_digit_y, y_mark_edge='Center'),
            Text(self.screen, ':', SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE, SetTimerPageConfig.DEFAULT_COLOR, 
                 SetTimerPageConfig.TIME_DIGIT_TEXT_COL1_X, time_digit_y, y_mark_edge='Center'),
        ]
        
        self.title_box = IconTextBox(
            screen=self.screen,
            x_marking=SetTimerPageConfig.TITLE_X,
            y_marking=SetTimerPageConfig.TITLE_Y,
            box_width=SetTimerPageConfig.TITLE_BOX_WIDTH,
            box_height=SetTimerPageConfig.TITLE_BOX_HEIGHT,
            text='Timer',
            text_size=SetTimerPageConfig.TITLE_TEXT_SIZE,
            color=SetTimerPageConfig.TITLE_COLOR,
            background_color=SetTimerPageConfig.BACKGROUND_COLOR,
            icon_path='./icons/menu_timer.png',
            icon_margin_x=SetTimerPageConfig.TITLE_ICON_X_MARGIN,
            icon_y_ratio=SetTimerPageConfig.TITLE_ICON_Y_RATIO,
            x_mark_edge='Center',
            y_mark_edge='Center',
            icon_alignment='Left',
            icon_color_replacements=SetTimerPageConfig.TITLE_ICON_COLOR_REPLACEMENTS
        )
        
        self.proceed_message = Text(self.screen, 'Start timing?', SetTimerPageConfig.MSG_TEXT_SIZE, SetTimerPageConfig.MSG_COLOR,
                                    SetTimerPageConfig.MSG_X, SetTimerPageConfig.MSG_Y)  
        self.discard_message = Text(self.screen, 'Discard timer?', SetTimerPageConfig.MSG_TEXT_SIZE, SetTimerPageConfig.MSG_COLOR,
                                    SetTimerPageConfig.MSG_X, SetTimerPageConfig.MSG_Y)  
    

    def _display(self):
        while True:
            self.screen.fill_screen(self.background_color)
            
            # Update components by states
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            hover_id = self.hover_id.reveal()
            prev_hover_id = self.prev_hover_id.reveal()
            change_time_digit_val = self.change_time_digit_val.reveal()
            
            if state != prev_state:
                
                if prev_state == SetTimerPageState.SELECT and state == SetTimerPageState.HOVER:
                    # Selected => Hovered
                    self.time_digit_components[hover_id].unselect()
                
                elif prev_state == SetTimerPageState.HOVER and state == SetTimerPageState.SELECT:
                    # Hovered => Selected
                    self.time_digit_components[hover_id].select()
                
                elif prev_state == SetTimerPageState.HOVER:
                    # Hovered => To Proceed
                    # Hovered => To Discard
                    self.time_digit_components[hover_id].unhover()
                    
                elif state == SetTimerPageState.TO_HOVER:
                    # To Proceed => Hovered
                    # To Discard => Hovered 
                    self.time_digit_components[hover_id].hover()

                self.prev_state.overwrite(state)
                
            elif hover_id != prev_hover_id:
                # The digit hovered has changed
                self.time_digit_components[prev_hover_id].unhover()
                self.time_digit_components[hover_id].hover()
                self.prev_hover_id.overwrite(hover_id)
                
            elif change_time_digit_val != 0:
                # The value of the digit should change
                self.time_digit_components[hover_id].change_value(change_time_digit_val)
                self.change_time_digit_val.overwrite(0)
            
            
            # Draw components
            for time_digit in self.time_digit_components:
                time_digit.draw()
            for text in self.text_components:
                text.draw()
            
            if state == SetTimerPageState.TO_PROCEED:
                self.proceed_message.draw()
            elif state == SetTimerPageState.TO_DISCARD:
                self.discard_message.draw()
            
            self.title_box.draw()
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()