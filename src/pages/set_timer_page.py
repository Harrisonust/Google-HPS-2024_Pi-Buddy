import time
import multiprocessing


from pages.pages_utils import theme_colors, PageConfig, Text, IconTextBox, OptionBox, IconPaths
from pages.page import Page
from value_manager import ValueManager
       
 
class SetTimerPageConfig():
    ICON_TRUE_COLOR = PageConfig.ICON_TRUE_COLOR
    ICON_FALSE_COLOR = PageConfig.ICON_FALSE_COLOR
    TITLE_COLOR = PageConfig.TITLE_COLOR
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR
    BACKGROUND_COLOR = PageConfig.BACKGROUND_COLOR
    TITLE_TEXT_SIZE = 14
    
    # Time digit coordinates
    TIME_DIGIT_Y = 60
    TIME_DIGIT_TEXT_SIZE = 25
    TIME_DIGIT_HR_H_X = 25
    TIME_DIGIT_HR_L_X = 40
    TIME_DIGIT_MIN_H_X = 65
    TIME_DIGIT_MIN_L_X = 80
    TIME_DIGIT_SEC_H_X = 105
    TIME_DIGIT_SEC_L_X = 120
    
    # Button coordinates
    BTN_Y = 90
    PROCEED_BTN_X = 112
    RESET_BTN_X = 60
    MENU_BTN_X = 8
    
    # Text coordinates
    TIME_DIGIT_TEXT_COL_0_X = 55
    TIME_DIGIT_TEXT_COL_1_X = 95
    TITLE_TEXT_X = 35
    TITLE_TEXT_Y = 15
    
    TITLE_TEXT_SIZE = 14
    
    

class TimeDigitConfig():
    DEFAULT_NUM = 0
    TEXT_SIZE = SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR
    HOVERED_COLOR = theme_colors.Highlight
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
        # Set to hovered color
        self.color = self.hovered_color
    
    def unhover(self):
        # Set to default color
        self.color = self.default_color

    def select(self):
        # Set to on-change color
        self.color = self.on_change_color
        
    def unselect(self):
        # Set to hovered color
        self.color = self.hovered_color
    
    def change_value(self, change):
        # Change value by 'change'
        self.num = (self.num + change) % self.num_max_exclusive
        self.text = str(self.num)
    
    def reset_value(self):
        # Reset value to 0
        self.num = 0
        self.text = str(self.num)
        

class SetTimerPageBtnConfig:
    BOX_HOVER_SCALE = 1                                             # The ratio the box is scaled at in hover mode 
    BORDER_HOVER_SCALE = 1                                          # The ratio the box border is scaled at in hover mode
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR                        # Default color for border box, icon, and text
    HOVERED_COLOR = PageConfig.HOVERED_COLOR                        # Hovered color for border box, icon, and text
    BACKGROUND_COLOR = PageConfig.BACKGROUND_COLOR                  # Background color of the screen
    DEFAULT_BOX_WIDTH = PageConfig.BTN_WIDTH                        # Box width in default mode, border width included
    DEFAULT_BOX_HEIGHT = PageConfig.BTN_HEIGHT                      # Box height in default mode, border width included
    DEFAULT_BORDER = PageConfig.BTN_BORDER                          # Default border width 
    ICON_Y_RATIO = PageConfig.BTN_ICON_Y_RATIO                      # The amount of horizontal space the icon takes, border width exclusive
    DEFAULT_ICON_X_MARGIN = PageConfig.BTN_ICON_X_MARGIN            # The x margin between border-icon and icon-text 
    DEFAULT_TEXT_SIZE = PageConfig.BTN_TEXT_SIZE                    # Default text size


class SetTimerPageBtn(OptionBox):
    def __init__(self, screen, default_x, default_y, text, icon_path):
        super().__init__(
            screen=screen, 
            default_x=default_x,
            default_y=default_y,
            text=text,
            icon_path=icon_path,
            box_hover_scale=SetTimerPageBtnConfig.BOX_HOVER_SCALE,
            border_hover_scale=SetTimerPageBtnConfig.BORDER_HOVER_SCALE,
            default_color=SetTimerPageBtnConfig.DEFAULT_COLOR,
            hovered_color=SetTimerPageBtnConfig.HOVERED_COLOR,
            background_color=SetTimerPageBtnConfig.BACKGROUND_COLOR,
            default_box_width=SetTimerPageBtnConfig.DEFAULT_BOX_WIDTH,
            default_box_height=SetTimerPageBtnConfig.DEFAULT_BOX_HEIGHT,
            default_border=SetTimerPageBtnConfig.DEFAULT_BORDER,
            default_icon_x_margin=SetTimerPageBtnConfig.DEFAULT_ICON_X_MARGIN,
            default_text_size=SetTimerPageBtnConfig.DEFAULT_TEXT_SIZE,
            icon_y_ratio=SetTimerPageBtnConfig.ICON_Y_RATIO
        )
        
    def unhover(self):
        self.reset()

class SetTimerPageState():
    HOVER_TIME_DIGIT = 0
    SELECT_TIME_DIGIT = 1
    HOVER_BTN = 2
    END_DISPLAY = 3


class SetTimerPage(Page):
    def __init__(self, screen):
        self.screen = screen

        self.hoverable_components = None
        self.hoverable_tags = None
        self.text_components = None
        self._initiate_components()
        
        self.set_timer_page_busy = ValueManager(int(False))
        self.state = ValueManager(SetTimerPageState.HOVER_TIME_DIGIT)
        self.prev_state = ValueManager(SetTimerPageState.HOVER_TIME_DIGIT)
        self.hover_id = ValueManager(0)
        self.prev_hover_id = ValueManager(0)
        self.change_time_digit_val = ValueManager(0)
        self.display_completed = ValueManager(int(False))
        self.time_value_pipe = ValueManager(0)
        self.reset_values = ValueManager(int(False))
        
        self.hoverable_components[self.hover_id.reveal()].hover()
        
        
    def reset_states(self, args):
        self.set_timer_page_busy.overwrite(int(False))
        self.state.overwrite(SetTimerPageState.HOVER_TIME_DIGIT)
        self.prev_state.overwrite(SetTimerPageState.HOVER_TIME_DIGIT)
        self.hover_id.overwrite(0)
        self.prev_hover_id.overwrite(0)
        self.change_time_digit_val.overwrite(0)
        self.display_completed.overwrite(int(False))
        self.reset_values.overwrite(int(False))
    
    
    def start_display(self):
        # Start display process for set timer page
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
        
        
    def handle_task(self, task_info):
        if not self.set_timer_page_busy.reveal():
            
            self.set_timer_page_busy.overwrite(int(True))
            state = self.state.reveal()
            hover_id = self.hover_id.reveal()

            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                if (state == SetTimerPageState.HOVER_TIME_DIGIT or 
                    state == SetTimerPageState.HOVER_BTN):
                    # Move hover to next digit
                    hover_id = (hover_id - 1) % len(self.hoverable_components)
                    self.hover_id.overwrite(hover_id)
                elif state == SetTimerPageState.SELECT_TIME_DIGIT:
                    # Decrease digit value by 1
                    self.change_time_digit_val.overwrite(-1)
                
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                if (state == SetTimerPageState.HOVER_TIME_DIGIT or 
                    state == SetTimerPageState.HOVER_BTN):
                    # Move hover to previous digits
                    hover_id = (hover_id + 1) % len(self.hoverable_components)
                    self.hover_id.overwrite(hover_id)
                elif state == SetTimerPageState.SELECT_TIME_DIGIT:
                    # Increase digit value by 1      
                    self.change_time_digit_val.overwrite(1)  
            
            elif task_info['task'] == 'ENTER_SELECT':
                if state == SetTimerPageState.HOVER_TIME_DIGIT:
                    self.state.overwrite(SetTimerPageState.SELECT_TIME_DIGIT)
                elif state == SetTimerPageState.SELECT_TIME_DIGIT:
                    self.state.overwrite(SetTimerPageState.HOVER_TIME_DIGIT)
                elif state == SetTimerPageState.HOVER_BTN:
                    # Perform button task
                    if self.hoverable_tags[hover_id] == 'proceed':
                        self.state.overwrite(SetTimerPageState.END_DISPLAY)
                        while True:
                            if self.display_completed.reveal():
                                time_value_pipe = self.time_value_pipe.reveal()
                                # return 'TimerPage', self._decode_time_value_pipe(time_value_pipe)
                                return {
                                    'type': 'NEW_PAGE',
                                    'page': 'TimerPage',
                                    'args': self._decode_time_value_pipe(time_value_pipe),
                                }
                        
                    elif self.hoverable_tags[hover_id] == 'reset':
                        self.reset_values.overwrite(int(True))
                        
                    elif self.hoverable_tags[hover_id] == 'menu':
                        self.state.overwrite(SetTimerPageState.END_DISPLAY)
                        while True:
                            if self.display_completed.reveal():
                                # return 'MenuPage', None
                                return {
                                    'type': 'NEW_PAGE',
                                    'page': 'MenuPage',
                                    'args': None,
                                }
                
            elif task_info['task'] == 'OUT_RESUME':
                if state == SetTimerPageState.SELECT_TIME_DIGIT:
                    self.state.overwrite(SetTimerPageState.HOVER_TIME_DIGIT)
            
            elif task_info['task'] == 'PAGE_EXPIRED':
                self.state.overwrite(SetTimerPageState.END_DISPLAY)
                while True:
                    if self.display_completed.reveal():
                        # return 'EmotionPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'EmotionPage',
                            'args': None,
                        }
                        
            elif task_info['task'] == 'SWITCH_PAGE':
                self.state.overwrite(SetTimerPageState.END_DISPLAY)
                while True:
                    if self.display_completed.reveal():
                        # return 'EmotionPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': task_info['page_key'],
                            'args': task_info['args']
                        }
            
            
            self.set_timer_page_busy.overwrite(int(False))
    
    
    def _initiate_components(self):

        self.hoverable_components = [
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_HR_H_X, SetTimerPageConfig.TIME_DIGIT_Y, 10),                      
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_HR_L_X, SetTimerPageConfig.TIME_DIGIT_Y, 10),                      
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_MIN_H_X, SetTimerPageConfig.TIME_DIGIT_Y, 6),                      
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_MIN_L_X, SetTimerPageConfig.TIME_DIGIT_Y, 10),                     
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_SEC_H_X, SetTimerPageConfig.TIME_DIGIT_Y, 6),                      
            TimeDigit(self.screen, SetTimerPageConfig.TIME_DIGIT_SEC_L_X, SetTimerPageConfig.TIME_DIGIT_Y, 10),                     
            SetTimerPageBtn(self.screen, SetTimerPageConfig.MENU_BTN_X, SetTimerPageConfig.BTN_Y, 'Menu', IconPaths.Menu),         
            SetTimerPageBtn(self.screen, SetTimerPageConfig.RESET_BTN_X, SetTimerPageConfig.BTN_Y, 'Reset', IconPaths.Reset),  
            SetTimerPageBtn(self.screen, SetTimerPageConfig.PROCEED_BTN_X, SetTimerPageConfig.BTN_Y, 'Start', IconPaths.Proceed),          
        ]
        
        self.hoverable_tags = [
            'time_digit',
            'time_digit',
            'time_digit',
            'time_digit',
            'time_digit',
            'time_digit',
            'menu',
            'reset',
            'proceed',
        ]
        
        self.text_components = [
            Text(self.screen, ':', SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE, SetTimerPageConfig.DEFAULT_COLOR, 
                 SetTimerPageConfig.TIME_DIGIT_TEXT_COL_0_X, SetTimerPageConfig.TIME_DIGIT_Y, y_mark_edge='Center'),
            Text(self.screen, ':', SetTimerPageConfig.TIME_DIGIT_TEXT_SIZE, SetTimerPageConfig.DEFAULT_COLOR, 
                 SetTimerPageConfig.TIME_DIGIT_TEXT_COL_1_X, SetTimerPageConfig.TIME_DIGIT_Y, y_mark_edge='Center'),
            Text(self.screen, 'Set Your Timer:', SetTimerPageConfig.TITLE_TEXT_SIZE, SetTimerPageConfig.DEFAULT_COLOR,
                 SetTimerPageConfig.TITLE_TEXT_X, SetTimerPageConfig.TITLE_TEXT_Y)
        ]

  
    def _display(self):
        while True:
            self.screen.fill_screen(SetTimerPageConfig.BACKGROUND_COLOR)
            
            # Update components by states
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            hover_id = self.hover_id.reveal()
            prev_hover_id = self.prev_hover_id.reveal()
            change_time_digit_val = self.change_time_digit_val.reveal()
            reset_values = self.reset_values.reveal()
            
            if state == SetTimerPageState.END_DISPLAY:
                break
            
            elif state != prev_state:
                
                if prev_state == SetTimerPageState.SELECT_TIME_DIGIT and state == SetTimerPageState.HOVER_TIME_DIGIT:
                    # Time digit selected => Time digit hovered
                    self.hoverable_components[hover_id].unselect()
                
                elif prev_state == SetTimerPageState.HOVER_TIME_DIGIT and state == SetTimerPageState.SELECT_TIME_DIGIT:
                    # Time digit hovered => Time digit selected
                    self.hoverable_components[hover_id].select()
                    

                self.prev_state.overwrite(state)
                
            elif hover_id != prev_hover_id:
                # The digit hovered has changed
                self.hoverable_components[prev_hover_id].unhover()
                self.hoverable_components[hover_id].hover()
                self.prev_hover_id.overwrite(hover_id)
                
                # Update state according to the selected hoverable
                self.prev_state.overwrite(self.state.reveal())
                if self.hoverable_tags[hover_id] == 'time_digit':
                    self.state.overwrite(SetTimerPageState.HOVER_TIME_DIGIT)
                else:
                    self.state.overwrite(SetTimerPageState.HOVER_BTN)
                
            elif change_time_digit_val != 0:
                # The value of the digit should change
                self.hoverable_components[hover_id].change_value(change_time_digit_val)
                self.change_time_digit_val.overwrite(0)
            
            if reset_values:
                for i in range(len(self.hoverable_tags)):
                    if self.hoverable_tags[i] == 'time_digit':
                        self.hoverable_components[i].reset_value()
                self.reset_values.overwrite(int(False))
            
            
            # Draw components
            for hoverable in self.hoverable_components:
                hoverable.draw()
            for text in self.text_components:
                text.draw()    
            
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
            
        self._pass_time_val()
        self.display_completed.overwrite(int(True))
        
    
    def _decode_time_value_pipe(self, time_value_pipe):
        # time_val_keys = ['sec_l', 'sec_h', 'min_l', 'min_h', 'hr_l', 'hr_h']
        time_val_keys = ['hr_h', 'hr_l', 'min_h', 'min_l', 'sec_h', 'sec_l']
        time_val = dict()
        
        for i in range(len(time_val_keys)):
            time_val[time_val_keys[i]] = time_value_pipe % 10
            time_value_pipe //= 10
        
        return time_val
            

    def _pass_time_val(self):
        value_to_write = 0
        mul = 1
        for i, hoverable_component in enumerate(self.hoverable_components):
            if self.hoverable_tags[i] == 'time_digit':
                value_to_write += int(hoverable_component.text) * mul
                mul *= 10
        self.time_value_pipe.overwrite(value_to_write)
                