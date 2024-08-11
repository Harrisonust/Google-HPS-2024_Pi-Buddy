import multiprocessing
import time
from enum import Enum
import RPi.GPIO as GPIO


from pages.pages_utils import EvaDark
from components.st7735s.st7735s import Screen
from value_manager import ValueManager


class OptionBoxConfig(Enum):
    BOX_HOVER_SCALE = 1.2                           # The ratio the box is scaled at in hover mode 
    BORDER_HOVER_SCALE = 2                          # The ratio the box border is scaled at in hover mode
    DEFAULT_COLOR = EvaDark.DEFAULT_0               # Default color for border box, icon, and text
    HOVERED_COLOR = EvaDark.HIGHLIGHT_1             # Hovered color for border box, icon, and text
    BACKGROUND_COLOR = EvaDark.BACKGROUND_0         # Background color of the screen
    DEFAULT_BOX_WIDTH = 110                         # Box width in default mode, border width included
    DEFAULT_BOX_HEIGHT = 35                         # Box height in default mode, border width included
    DEFAULT_BORDER = 2                              # Default border width 
    Y_MARGIN = 5                                    # Box margin in vertical direction
    ICON_Y_RATIO = 0.8                              # The amount of horizontal space the icon takes, border width exclusive
    DEFAULT_ICON_X_MARGIN = 5                       # The x margin between border-icon and icon-text 
    DEFAULT_TEXT_SIZE = 14                          # Default text size


class OptionBox():
    def __init__(self, screen, default_x, default_y, text, icon_path):
        
        # The screen, for drawing
        self.screen = screen
        
        # States
        self.display = True
        self.show_border = True
        
        # Parameters that are static
        self.text = text
        self.icon_path = icon_path
        self.box_hover_scale = OptionBoxConfig.BOX_HOVER_SCALE.value
        self.border_hover_scale = OptionBoxConfig.BORDER_HOVER_SCALE.value
        self.default_color = OptionBoxConfig.DEFAULT_COLOR.value
        self.hovered_color = OptionBoxConfig.HOVERED_COLOR.value
        self.background_color = OptionBoxConfig.BACKGROUND_COLOR.value
        self.y_margin = OptionBoxConfig.Y_MARGIN.value
        self.icon_y_ratio = OptionBoxConfig.ICON_Y_RATIO.value
        
        # Parameters representing the default stage
        self.default_x = default_x
        self.default_y = default_y
        self.default_box_width = OptionBoxConfig.DEFAULT_BOX_WIDTH.value
        self.default_box_height = OptionBoxConfig.DEFAULT_BOX_HEIGHT.value
        self.default_border = OptionBoxConfig.DEFAULT_BORDER.value
        self.default_icon_x_margin = OptionBoxConfig.DEFAULT_ICON_X_MARGIN.value
        self.default_text_size = OptionBoxConfig.DEFAULT_TEXT_SIZE.value
        
        
        # Parameters to be set
        self.box_width = None
        self.box_height = None
        self.border = None
        self.color = None
        self.icon_size = None
        self.icon_x_margin = None
        self.text_size = None
        self.text_height = None
        self.x = None
        self.y = None
        
        # Set parameters to default
        self._reset_params()
    
    
    def _reset_params(self):
        # Set parameters to default value
        self.box_width = self.default_box_width
        self.box_height = self.default_box_height
        self.border = self.default_border
        self.color = self.default_color
        self.icon_size = int((self.box_height - (2 * self.border)) * self.icon_y_ratio)
        self.icon_x_margin = self.default_icon_x_margin
        self.text_size = self.default_text_size
        self.text_height = self.text_size + 4
        self.x = self.default_x
        self.y = self.default_y


    def move_y(self, y_incr, div):
        # Move y value, where y_incr is the amount to move and div keeps the value in range
        self.default_y += y_incr
        self.default_y %= div
        self._reset_params()
        
    
    def set_display_none(self):
        self.display = False


    def reverse_color(self):
        self.color, self.background_color = self.background_color, self.color
        
    
    def hide_border(self):
        self.show_border = False


    def hover(self):
        # Set parameters to hover mode
        self.box_width = int(self.default_box_width * self.box_hover_scale)
        self.box_height = int(self.default_box_height * self.box_hover_scale)
        self.border = int(self.default_border * self.border_hover_scale)
        self.color = int(self.hovered_color)
        self.icon_size = int((self.box_height - (2 * self.border)) * self.icon_y_ratio)
        self.icon_x_margin = int(self.default_icon_x_margin * self.box_hover_scale)
        self.text_size = int(self.default_text_size * self.box_hover_scale)
        self.text_height = int(self.text_size + 4)
        self.x = int(self.default_x - (self.box_width * (self.box_hover_scale - 1) / 2))
        self.y = int(self.default_y - (self.box_height * (self.box_hover_scale - 1) / 2)) 


    def draw(self):
        # Draw option box
        if self.display:
            if self.show_border:
                self.screen.draw_rectangle(self.x, self.y, self.box_width, self.box_height, self.color)
            self.screen.draw_rectangle(self.x + self.border, self.y + self.border, self.box_width - (self.border * 2),
                                    self.box_height - (self.border * 2), self.background_color)
            self.screen.draw_image(self.x + self.border + self.icon_x_margin, self.y + (self.box_height // 2) - (self.icon_size // 2), 
                                self.icon_size, self.icon_size, self.icon_path, 
                                replace_with={(255, 255, 255): self.color, (0, 0, 0): self.background_color})     
            self.screen.draw_text(self.x + self.border + self.icon_size + (2 * self.icon_x_margin), 
                                self.y + (self.box_height // 2) - (self.text_height // 2), 
                                self.text, self.text_size, self.color)


class MenuPageCursorDirection(Enum):
    NONE = 0
    UP = 1
    DOWN = -1
    
    
class MenuPageSelectTransitionStage(Enum):
    NONE = 0
    REMOVE_OTHERS = 1
    REVERSE_SELECTED_COLOR = 2
    COLOR_BACKGROUND = 3
    END_DISPLAY = 4


class MenuPage():
    def __init__(self, screen):        
        self.screen = screen
        
        # Screen states
        self.cursor_direction = ValueManager(MenuPageCursorDirection.NONE.value)    
        self.select_triggered = ValueManager(int(False))
        self.select_transition_state = ValueManager(MenuPageSelectTransitionStage.NONE.value)
        self.display_completed = ValueManager(int(False))
        
        # Setting the options in the menu
        self.option_box_information = [
            ['Weather', './icons/menu_weather.png'],
            ['Battery', './icons/menu_battery.png'],
            ['Time',    './icons/menu_timer.png'],
            ['???',     './icons/menu_surprise.png']
        ]
        self.background_color = EvaDark.BACKGROUND_0.value
        self.option_boxes = None 
        self.hovered_id = None
        self.option_box_height = None
        self.content_height = None
        self._initiate_option_boxes()
        
        
        # Start display process for menu page
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
    
    
    def handle_task(self, task_info):
        
        # Tasks will not be taken if a transition is ongoing
        if (self.cursor_direction.reveal() == MenuPageCursorDirection.NONE.value and
            self.select_triggered.reveal() == int(False)):

            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                self.cursor_direction.overwrite(MenuPageCursorDirection.DOWN.value)
                
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                self.cursor_direction.overwrite(MenuPageCursorDirection.UP.value)
                
            elif task_info['task'] == 'ENTER_SELECT':
                self.select_triggered.overwrite(int(True))
                
                # Return message to go to next page after display is done
                while True:
                    if self.display_completed.reveal():
                        return 'NEXT_PAGE', self.option_box_information[self.hovered_id]
                
            elif task_info['task'] == 'OUT_RESUME':
                pass
            
    
    
    def _initiate_option_boxes(self):
        
        # Hover over the option box in the middle as default
        num_boxes = len(self.option_box_information)
        self.hovered_id = num_boxes // 2
        
        # Calculate x value of the first box
        screen_width = self.screen.get_col_dim()
        box_width = OptionBoxConfig.DEFAULT_BOX_WIDTH.value
        current_box_x = (screen_width // 2) - (box_width // 2)
        
        # Calculate y vlaue of the first box
        screen_height = self.screen.get_row_dim()
        option_box_height = OptionBoxConfig.DEFAULT_BOX_HEIGHT.value + (2 * OptionBoxConfig.Y_MARGIN.value)
        current_box_y = (screen_height // 2) - ((self.hovered_id * 2 + 1) / 2.0 * option_box_height) + OptionBoxConfig.Y_MARGIN.value
        
        # Initiate option boxes with information from self.option_box_information
        self.option_boxes = []
        for box_info in self.option_box_information:
            option_box_name, option_box_icon_path = box_info
            self.option_boxes.append(
                OptionBox(
                    self.screen, 
                    current_box_x, 
                    current_box_y, 
                    option_box_name, 
                    option_box_icon_path)
            )
            current_box_y += option_box_height
        
        # Update height values
        self.option_box_height = option_box_height
        self.content_height = option_box_height * len(self.option_box_information)
        
        # Hover 
        self.option_boxes[self.hovered_id].hover()
                
        
    def _display(self):
        while True:
            
            cursor_direction = self.cursor_direction.reveal()
            select_triggered = self.select_triggered.reveal()
            
            # Check if the cursor had been moved
            if cursor_direction:
                if cursor_direction == MenuPageCursorDirection.UP.value:
                    direction = -1
                elif cursor_direction == MenuPageCursorDirection.DOWN.value:    
                    direction = 1
                else:
                    raise ValueError(f'Invaid cursor direction {cursor_direction} was assigned to menu page')

                # Move option_boxes 
                for option_box in self.option_boxes:
                    option_box.move_y(direction * self.option_box_height, self.content_height)
                
                self.hovered_id = (self.hovered_id - direction) % len(self.option_box_information)
                self.option_boxes[self.hovered_id].hover()
                self.cursor_direction.overwrite(MenuPageCursorDirection.NONE.value)
            
            # Check if select had been triggered
            elif select_triggered:
                select_transition_state = self.select_transition_state.reveal()
                
                if select_transition_state == MenuPageSelectTransitionStage.REMOVE_OTHERS.value:
                    for option_box_id, option_box in enumerate(self.option_boxes):
                        if option_box_id != self.hovered_id:
                            option_box.set_display_none()
                
                elif select_transition_state == MenuPageSelectTransitionStage.REVERSE_SELECTED_COLOR.value:
                    self.option_boxes[self.hovered_id].reverse_color()
                
                elif select_transition_state == MenuPageSelectTransitionStage.COLOR_BACKGROUND.value:
                    self.option_boxes[self.hovered_id].hide_border()
                    self.background_color = OptionBoxConfig.HOVERED_COLOR.value
                
                elif select_transition_state == MenuPageSelectTransitionStage.END_DISPLAY.value:
                    break
                
                self.select_transition_state.overwrite(select_transition_state + 1)
                
            # Draw and update screen
            self.screen.fill_screen(self.background_color)
            for option_box in self.option_boxes:
                option_box.draw()
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))
