import time
import multiprocessing


from pages.pages_utils import theme_colors, PageConfig, Text, IconPaths
from pages.page import Page
from value_manager import ValueManager
    
    
class TimerPageConfig():
    
    TIMER_Y = 60
    TIMER_HR_H_X = 25
    TIMER_HR_L_X = 40
    TIMER_COL_0_X = 55
    TIMER_MIN_H_X = 65
    TIMER_MIN_L_X = 80
    TIMER_COL_1_X = 95
    TIMER_SEC_H_X = 105
    TIMER_SEC_L_X = 120
    
    TEXT_SIZE = 25
    
    BACKGROUND_COLOR = theme_colors.Primary
    
    TIME_VAL_COUNTING_COLOR = theme_colors.Success
    TIME_VAL_PAUSED_COLOR = theme_colors.Muted
    TIME_VAL_TIMEUP_0_COLOR = theme_colors.Danger
    TIME_VAL_TIMEUP_1_COLOR = theme_colors.Warning
    
    COL_COUNTING_COLOR = theme_colors.Font
    COL_PAUSED_COLOR = theme_colors.Secondary
    COL_TIMEUP_0_COLOR = theme_colors.Info
    COL_TIMEUP_1_COLOR = theme_colors.Contrast
    
    RING_X = 80
    RING_Y = TIMER_Y
    RING_OUTER_RADIUS = 45
    RING_INNER_RADIUS = 40
    RING_COLOR = theme_colors.Teritary

    RING_RECT_X = 22
    RING_RECT_Y = 47
    RING_RECT_WIDTH = 114
    RING_RECT_HEIGHT = 26
    
    
class TimerPageStates():
    COUNTING = 0
    PAUSED = 1
    TIMEUP = 2
    DISCARD = 3
    

class TimerRing():
    def __init__(self, screen, total_ticks):
        self.screen = screen
        self.total_ticks = total_ticks
        self.color = TimerPageConfig.RING_COLOR
        self.background_color = TimerPageConfig.BACKGROUND_COLOR
        self.x = TimerPageConfig.RING_X
        self.y = TimerPageConfig.RING_Y
        self.outer_radius = TimerPageConfig.RING_OUTER_RADIUS
        self.inner_radius = TimerPageConfig.RING_INNER_RADIUS
        
        self.rect_x = TimerPageConfig.RING_RECT_X
        self.rect_y = TimerPageConfig.RING_RECT_Y
        self.rect_width = TimerPageConfig.RING_RECT_WIDTH
        self.rect_height = TimerPageConfig.RING_RECT_HEIGHT
        

    def update_total_ticks(total_ticks):
        self.total_ticks = total_ticks
    
    
    def draw(self, ticks_left):        
        # TIMEUP
        if ticks_left <= 0:
            self.screen.draw_circle(self.x, self.y, self.outer_radius, self.color)
            self.screen.draw_circle(self.x, self.y, self.outer_radius - 1, self.background_color)
            self.screen.draw_circle(self.x, self.y, self.inner_radius + 1, self.color)
            self.screen.draw_circle(self.x, self.y, self.inner_radius, self.background_color)
        
        # COUNTING/PAUSED
        else:
            end_angle = int(ticks_left / self.total_ticks * 360)
            self.screen.draw_sector(self.x, self.y, self.outer_radius, 91, end_angle + 90, self.color)
            self.screen.draw_sector(self.x, self.y, self.inner_radius, 91, end_angle + 90, self.background_color)

        self.screen.draw_rectangle(self.rect_x, self.rect_y, self.rect_width, self.rect_height, self.background_color)
        
    
class TimerText(Text):
    def __init__(self, screen, x, y, val):
        if val == ':':
            color = TimerPageConfig.COL_COUNTING_COLOR
        else:
            color = TimerPageConfig.TIME_VAL_COUNTING_COLOR
        
        self.toggle_flag = False
        super().__init__(
            screen, str(val), TimerPageConfig.TEXT_SIZE, 
            color, x, y, x_mark_edge='Left', y_mark_edge='Center'
        )
    
    def decrease(self):
        self.text = str(int(self.text) - 1)
        
    def to_counting_mode(self):
        if self.text == ':':
            self.color = TimerPageConfig.COL_COUNTING_COLOR
        else:
            self.color = TimerPageConfig.TIME_VAL_COUNTING_COLOR
        
    def to_paused_mode(self):
        if self.text == ':':
            self.color = TimerPageConfig.COL_PAUSED_COLOR
        else:
            self.color = TimerPageConfig.TIME_VAL_PAUSED_COLOR
    
    def to_timeup_mode(self):
        if self.text == ':':
            self.color = TimerPageConfig.COL_TIMEUP_0_COLOR
        else:
            self.color = TimerPageConfig.TIME_VAL_TIMEUP_0_COLOR
            
    def toggle_timeup_color(self):        
        if self.toggle_flag:
            self.to_timeup_mode()
        else:    
            if self.text == ':':
                self.color = self.color = TimerPageConfig.COL_TIMEUP_1_COLOR
            else:
                self.color = TimerPageConfig.TIME_VAL_TIMEUP_1_COLOR

        self.toggle_flag = not self.toggle_flag


class TimerPage(Page):
    def __init__(self, screen, time_val=None):
        self.screen = screen
        self.time_val = None
        # self.time_val = {
        #     'hr_h':  0,
        #     'hr_l':  0,
        #     'min_h': 0,
        #     'min_l': 0,
        #     'sec_h': 0,
        #     'sec_l': 0,
        # }
            
        self.state = ValueManager(TimerPageStates.COUNTING)
        self.prev_state = ValueManager(TimerPageStates.COUNTING)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(True))
        
        self.total_ticks = None
        self.ticks_left = None
        
        self.timer_ring = None   
        self.components = None
        
    
    def _get_total_ticks(self):
        total_ticks = 0
        total_ticks += self.time_val['hr_h'] * 10 * 60 * 60
        total_ticks += self.time_val['hr_l'] * 60 * 60
        total_ticks += self.time_val['min_h'] * 10 * 60
        total_ticks += self.time_val['min_l'] * 60
        total_ticks += self.time_val['sec_h'] * 10
        total_ticks += self.time_val['sec_l']
        return total_ticks
    
    
    def _initiate_components(self):
        self.timer_ring = TimerRing(self.screen, self.total_ticks)
        self.text_components = {
            'hr_h':  TimerText(self.screen, TimerPageConfig.TIMER_HR_H_X, TimerPageConfig.TIMER_Y, self.time_val['hr_h']),
            'hr_l':  TimerText(self.screen, TimerPageConfig.TIMER_HR_L_X, TimerPageConfig.TIMER_Y, self.time_val['hr_l']),
            'col_0': TimerText(self.screen, TimerPageConfig.TIMER_COL_0_X, TimerPageConfig.TIMER_Y, ':'),
            'min_h': TimerText(self.screen, TimerPageConfig.TIMER_MIN_H_X, TimerPageConfig.TIMER_Y, self.time_val['min_h']),
            'min_l': TimerText(self.screen, TimerPageConfig.TIMER_MIN_L_X, TimerPageConfig.TIMER_Y, self.time_val['min_l']),
            'col_1': TimerText(self.screen, TimerPageConfig.TIMER_COL_1_X, TimerPageConfig.TIMER_Y, ':'),
            'sec_h': TimerText(self.screen, TimerPageConfig.TIMER_SEC_H_X, TimerPageConfig.TIMER_Y, self.time_val['sec_h']),
            'sec_l': TimerText(self.screen, TimerPageConfig.TIMER_SEC_L_X, TimerPageConfig.TIMER_Y, self.time_val['sec_l']),
        }
    
    
    def reset_states(self, time_val):
        self.time_val = time_val
        self.total_ticks = self._get_total_ticks()
        self.ticks_left = self.total_ticks
        self._initiate_components()
        
        self.state.overwrite(TimerPageStates.COUNTING)
        self.prev_state.overwrite(TimerPageStates.COUNTING)
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(True))
    
    def start_display(self):
        # Start display process for set timer page
        self.display_completed.overwrite(int(False))
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
        
        
    def handle_task(self, task_info):
        if not self.busy.reveal():
            
            self.busy.overwrite(int(True))
            
            state = self.state.reveal()
            page_transition = None
            
            if task_info['task'] == 'ENTER_SELECT':
                if state == TimerPageStates.COUNTING:
                    self.state.overwrite(TimerPageStates.PAUSED)
                elif state == TimerPageStates.PAUSED:
                    self.state.overwrite(TimerPageStates.COUNTING)
                elif state == TimerPageStates.TIMEUP:
                    self.state.overwrite(TimerPageStates.DISCARD)
                    page_transition = 'MenuPage'
            
            elif task_info['task'] == 'OUT_RESUME':
                self.state.overwrite(TimerPageStates.DISCARD)
                page_transition = 'MenuPage'
                
            if page_transition:
                while True:
                    if self.display_completed.reveal():
                        return page_transition, None
            
            self.busy.overwrite(int(False))
        
        
    def _display(self):
        
        prev_tick_time = time.time()
        
        while True:
            self.screen.fill_screen(TimerPageConfig.BACKGROUND_COLOR)
            
            state = self.state.reveal()
            prev_state = self.prev_state.reveal()
            
            if state == TimerPageStates.COUNTING:
                # PAUSED -> COUNTING
                if prev_state == TimerPageStates.PAUSED:
                    for text_component_name in self.text_components:
                        self.text_components[text_component_name].to_counting_mode() 
                    prev_tick_time = time.time()
                    
                # COUNTING -> COUNTING
                elif time.time() - prev_tick_time > 1:
                    self.ticks_left -= 1
                    prev_tick_time = time.time()
                    tick_output = self._tick()
                    if tick_output == 'TIMEUP':
                        self.state.overwrite(TimerPageStates.TIMEUP)
                        prev_tick_time = time.time()
                        for text_component_name in self.text_components:
                            self.text_components[text_component_name].to_timeup_mode() 
                    
            elif state == TimerPageStates.PAUSED and prev_state == TimerPageStates.COUNTING:
                # COUNTING -> PAUSED 
                for text_component_name in self.text_components:
                    self.text_components[text_component_name].to_paused_mode() 
            
            elif state == TimerPageStates.TIMEUP:
                # TIMEUP -> TIMEUP
                if time.time() - prev_tick_time > 0.5:
                    prev_tick_time = time.time()
                    for text_component_name in self.text_components:
                        self.text_components[text_component_name].toggle_timeup_color() 
                    
                
            elif state == TimerPageStates.DISCARD:
                break
            
            self.prev_state.overwrite(self.state.reveal())

            # Draw components
            self.timer_ring.draw(self.ticks_left)
            for text_component_name in self.text_components:
                self.text_components[text_component_name].draw()
            
            self.screen.update()
            time.sleep(0.001)
            self.screen.clear()
    
            
        self.display_completed.overwrite(int(True))
    
    
    def _tick(self):
        # Works out the time values for each second passed
        if self.text_components['sec_l'].text != '0':
            self.text_components['sec_l'].decrease()
            return
    
        self.text_components['sec_l'].text = '9'
        if self.text_components['sec_h'].text != '0':
            self.text_components['sec_h'].decrease()
            return
        
        self.text_components['sec_h'].text = '5'
        if self.text_components['min_l'].text != '0':
            self.text_components['min_l'].decrease()
            return
        
        self.text_components['min_l'].text = '9'
        if self.text_components['min_h'].text != '0':
            self.text_components['min_h'].decrease()
            return
        
        self.text_components['min_h'].text = '5'
        if self.text_components['hr_l'].text != '0' :
            self.text_components['hr_l'].decrease()
            return
        
        self.text_components['hr_l'].text = '9'
        if self.text_components['hr_h'].text != '0' :
            self.text_components['hr_h'].decrease()
            return
        
        for text_component_name in self.text_components:
            if 'col' not in text_component_name:
                self.text_components[text_component_name].text = '0'
        
        return 'TIMEUP' 