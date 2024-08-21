import multiprocessing
import time
import RPi.GPIO as GPIO


from pages.pages_utils import theme_colors, PageConfig, OptionBox, IconPaths
from pages.page import Page
from components.st7735s.st7735s import Screen
from value_manager import ValueManager

class MenuPageCursorDirection():
    NONE = 0
    UP = 1
    DOWN = -1
    
    
class MenuPageSelectTransitionStage():
    NONE = 0
    REMOVE_OTHERS = 1
    REVERSE_SELECTED_COLOR = 2
    COLOR_BACKGROUND = 3
    END_DISPLAY = 4


class MenuPageOptionBoxConfig():
    BOX_HOVER_SCALE = 1.2                                           # The ratio the box is scaled at in hover mode 
    BORDER_HOVER_SCALE = 2                                          # The ratio the box border is scaled at in hover mode
    DEFAULT_COLOR = PageConfig.DEFAULT_COLOR                        # Default color for border box, icon, and text
    HOVERED_COLOR = PageConfig.HOVERED_COLOR                        # Hovered color for border box, icon, and text
    BACKGROUND_COLOR = PageConfig.BACKGROUND_COLOR                  # Background color of the screen
    DEFAULT_BOX_WIDTH = PageConfig.PAGE_TITLE_BOX_WIDTH             # Box width in default mode, border width included
    DEFAULT_BOX_HEIGHT = PageConfig.PAGE_TITLE_BOX_HEIGHT           # Box height in default mode, border width included
    DEFAULT_BORDER = PageConfig.PAGE_TITLE_BOX_BORDER               # Default border width 
    Y_MARGIN = 5                                                    # Box margin in vertical direction
    ICON_Y_RATIO = PageConfig.PAGE_TITLE_BOX_ICON_Y_RATIO           # The amount of horizontal space the icon takes, border width exclusive
    DEFAULT_ICON_X_MARGIN = PageConfig.PAGE_TITLE_BOX_ICON_X_MARGIN # The x margin between border-icon and icon-text 
    DEFAULT_TEXT_SIZE = PageConfig.PAGE_TITLE_BOX_TEXT_SIZE         # Default text size


class MenuPageOptionBox(OptionBox):
    def __init__(self, screen, default_x, default_y, text, icon_path):       
        super().__init__(
            screen=screen, 
            default_x=default_x,
            default_y=default_y,
            text=text,
            icon_path=icon_path,
            box_hover_scale=MenuPageOptionBoxConfig.BOX_HOVER_SCALE,
            border_hover_scale=MenuPageOptionBoxConfig.BORDER_HOVER_SCALE,
            default_color=MenuPageOptionBoxConfig.DEFAULT_COLOR,
            hovered_color=MenuPageOptionBoxConfig.HOVERED_COLOR,
            background_color=MenuPageOptionBoxConfig.BACKGROUND_COLOR,
            default_box_width=MenuPageOptionBoxConfig.DEFAULT_BOX_WIDTH,
            default_box_height=MenuPageOptionBoxConfig.DEFAULT_BOX_HEIGHT,
            default_border=MenuPageOptionBoxConfig.DEFAULT_BORDER,
            default_icon_x_margin=MenuPageOptionBoxConfig.DEFAULT_ICON_X_MARGIN,
            default_text_size=MenuPageOptionBoxConfig.DEFAULT_TEXT_SIZE,
            icon_y_ratio=MenuPageOptionBoxConfig.ICON_Y_RATIO,
            y_margin=MenuPageOptionBoxConfig.Y_MARGIN,
        )
    

    def scroll(self, y_incr, div):
        # Move y value, where y_incr is the amount to move and div keeps the value in range
        self.default_y += y_incr
        self.default_y %= div
        self.reset()
        

    def reverse_color(self):
        self.color, self.background_color = self.background_color, self.color
        self.icon_color_replacements = {
            PageConfig.ICON_TRUE_COLOR: self.color,
            PageConfig.ICON_FALSE_COLOR: self.background_color
        }


class MenuPage(Page):
    def __init__(self, screen):        
        self.screen = screen
        
        # Screen states
        self.cursor_direction = ValueManager(MenuPageCursorDirection.NONE)    
        self.select_triggered = ValueManager(int(False))
        self.select_transition_state = ValueManager(MenuPageSelectTransitionStage.NONE)
        self.display_completed = ValueManager(int(False))
        
        # Setting the options in the menu
        self.option_box_information = [
            ['Weather', IconPaths.Weather],
            ['Time', IconPaths.Time],
            ['Battery', IconPaths.Battery],
            ['Photograph', IconPaths.Photograph],
            ['Film', IconPaths.Film],
            ['Timer',   IconPaths.Timer],
            ['Todo List', IconPaths.Todo],
            ['???',     IconPaths.Surprise]
        ]
        self.background_color = theme_colors.Primary
        self.option_boxes = None 
        self.hovered_id = None
        self.option_box_height = None
        self.content_height = None
        self._initiate_option_boxes()
        
    
    def reset_states(self, args):
        self.cursor_direction.overwrite(MenuPageCursorDirection.NONE)
        self.select_triggered.overwrite(int(False))
        self.select_transition_state.overwrite(MenuPageSelectTransitionStage.NONE)
        self.display_completed.overwrite(int(False))
        self._initiate_option_boxes()
        
    
    def start_display(self):
        # Start display process for menu page
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
    
    
    def handle_task(self, task_info):
        
        # Tasks will not be taken if a transition is ongoing
        if (self.cursor_direction.reveal() == MenuPageCursorDirection.NONE and
            self.select_triggered.reveal() == int(False)):

            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                self.cursor_direction.overwrite(MenuPageCursorDirection.DOWN)
                
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                self.cursor_direction.overwrite(MenuPageCursorDirection.UP)
                
            elif task_info['task'] == 'ENTER_SELECT':
                self.select_triggered.overwrite(int(True))
                
                # Return message to go to next page after display is done
                while True:
                    if self.display_completed.reveal():
                        next_page_title = self.option_box_information[self.hovered_id.reveal()][0]
                        if next_page_title == 'Weather':
                            return 'WeatherPage', None
                        if next_page_title == 'Timer':
                            return 'SetTimerPage', None
                        if next_page_title == 'Time':
                            return 'TimePage', None
                        if next_page_title == 'Todo List':
                            return 'TodoPage', None
                        if next_page_title == 'Photograph':
                            return 'PhotographPage', None
                    
                        return None, None
                
            elif task_info['task'] == 'OUT_RESUME':
                pass
            
    
    
    def _initiate_option_boxes(self):
        
        # Hover over the option box in the middle as default
        num_boxes = len(self.option_box_information)
        if not self.hovered_id:
            self.hovered_id = ValueManager(num_boxes // 2)
        else:
            self.hovered_id.overwrite(num_boxes // 2)
        
        # Calculate x value of the first box
        screen_width = self.screen.get_col_dim()
        box_width = MenuPageOptionBoxConfig.DEFAULT_BOX_WIDTH
        current_box_x = (screen_width // 2) - (box_width // 2)
        
        # Calculate y vlaue of the first box
        screen_height = self.screen.get_row_dim()
        option_box_height = MenuPageOptionBoxConfig.DEFAULT_BOX_HEIGHT + (2 * MenuPageOptionBoxConfig.Y_MARGIN)
        current_box_y = (screen_height // 2) - ((self.hovered_id.reveal() * 2 + 1) / 2.0 * option_box_height) + MenuPageOptionBoxConfig.Y_MARGIN
        
        # Initiate option boxes with information from self.option_box_information
        self.option_boxes = []
        for box_info in self.option_box_information:
            option_box_name, option_box_icon_path = box_info
            self.option_boxes.append(
                MenuPageOptionBox(
                    self.screen, 
                    int(current_box_x), 
                    int(current_box_y), 
                    option_box_name, 
                    option_box_icon_path)
            )
            current_box_y += option_box_height
        
        # Update height values
        self.option_box_height = option_box_height
        self.content_height = option_box_height * len(self.option_box_information)
        
        # Hover 
        self.option_boxes[self.hovered_id.reveal()].hover()
                
        
    def _display(self):
        while True:
            
            cursor_direction = self.cursor_direction.reveal()
            select_triggered = self.select_triggered.reveal()
            hovered_id = self.hovered_id.reveal()
            
            # Check if the cursor had been moved
            if cursor_direction:
                if cursor_direction == MenuPageCursorDirection.UP:
                    direction = -1
                elif cursor_direction == MenuPageCursorDirection.DOWN:    
                    direction = 1
                else:
                    raise ValueError(f'Invaid cursor direction {cursor_direction} was assigned to menu page')

                # Move option_boxes 
                for option_box in self.option_boxes:
                    option_box.scroll(direction * self.option_box_height, self.content_height)
                
                hovered_id = (hovered_id - direction) % len(self.option_box_information)
                self.option_boxes[hovered_id].hover()
                self.hovered_id.overwrite(hovered_id)
                self.cursor_direction.overwrite(MenuPageCursorDirection.NONE)
                
            # Check if select had been triggered
            elif select_triggered:
                select_transition_state = self.select_transition_state.reveal()
                
                if select_transition_state == MenuPageSelectTransitionStage.REMOVE_OTHERS:
                    for option_box_id, option_box in enumerate(self.option_boxes):
                        if option_box_id != hovered_id:
                            option_box.display = False
                
                elif select_transition_state == MenuPageSelectTransitionStage.REVERSE_SELECTED_COLOR:
                    self.option_boxes[hovered_id].reverse_color()
                
                elif select_transition_state == MenuPageSelectTransitionStage.COLOR_BACKGROUND:
                    self.option_boxes[hovered_id].show_border = False
                    self.background_color = MenuPageOptionBoxConfig.HOVERED_COLOR
                
                elif select_transition_state == MenuPageSelectTransitionStage.END_DISPLAY:
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
    

