import multiprocessing
import time


from pages.pages_utils import theme_colors, PageConfig, IconPaths, Text
from value_manager import ValueManager
from pages.page import Page


class BatteryPageConfig:
    BATTERY_SAFE_POWER_LEVEL = 20
    
    BACKGROUND_COLOR = theme_colors.Primary
    DEFAULT_COLOR = theme_colors.Warning
    
    BATTERY_POWER_SAFE_COLOR = theme_colors.Info
    BATTERY_POWER_DANGER_COLOR = theme_colors.Danger
    
    BATTERY_POWER_TEXT_X = 45
    BATTERY_POWER_TEXT_Y = 40
    BATTERY_POWER_TEXT_SIZE = 25
    
    BATTERY_POWER_BAR_X = 20
    BATTERY_POWER_BAR_Y = 80
    BATTERY_POWER_BAR_WIDTH = 120
    BATTERY_POWER_BAR_HEIGHT = 15
    BATTERY_POWER_BORDER_SIZE = 2
    
    CHARGING_ICON_X = 100
    CHARGING_ICON_Y = 38
    CHARGING_ICON_SIZE = 28


class BatteryPowerBar:
    def __init__(self, screen):
        self.screen = screen
        self.total_len = BatteryPageConfig.BATTERY_POWER_BAR_WIDTH - (2 * BatteryPageConfig.BATTERY_POWER_BORDER_SIZE)
        self.colored_len = 0
        self.color = BatteryPageConfig.BATTERY_POWER_SAFE_COLOR
        
    def update(self, power, is_charged):
        self.colored_len = int(self.total_len * (power / 100))
        self.color = (
            BatteryPageConfig.BATTERY_POWER_SAFE_COLOR
            if (is_charged or (power > BatteryPageConfig.BATTERY_SAFE_POWER_LEVEL)) else
            BatteryPageConfig.BATTERY_POWER_DANGER_COLOR
        )
        
        
    def draw(self):
        # Outer border
        if self.colored_len != None:
            self.screen.draw_rectangle(
                x=BatteryPageConfig.BATTERY_POWER_BAR_X,
                y=BatteryPageConfig.BATTERY_POWER_BAR_Y,
                xlen=BatteryPageConfig.BATTERY_POWER_BAR_WIDTH,
                ylen=BatteryPageConfig.BATTERY_POWER_BAR_HEIGHT,
                color=BatteryPageConfig.DEFAULT_COLOR
            )
            # Inner border
            self.screen.draw_rectangle(
                x=BatteryPageConfig.BATTERY_POWER_BAR_X + BatteryPageConfig.BATTERY_POWER_BORDER_SIZE,
                y=BatteryPageConfig.BATTERY_POWER_BAR_Y + BatteryPageConfig.BATTERY_POWER_BORDER_SIZE,
                xlen=BatteryPageConfig.BATTERY_POWER_BAR_WIDTH - (2 * BatteryPageConfig.BATTERY_POWER_BORDER_SIZE),
                ylen=BatteryPageConfig.BATTERY_POWER_BAR_HEIGHT - (2 * BatteryPageConfig.BATTERY_POWER_BORDER_SIZE),
                color=BatteryPageConfig.BACKGROUND_COLOR
            )
            # Filled part
            self.screen.draw_rectangle(
                x=BatteryPageConfig.BATTERY_POWER_BAR_X + BatteryPageConfig.BATTERY_POWER_BORDER_SIZE,
                y=BatteryPageConfig.BATTERY_POWER_BAR_Y + BatteryPageConfig.BATTERY_POWER_BORDER_SIZE,
                xlen=self.colored_len,
                ylen=BatteryPageConfig.BATTERY_POWER_BAR_HEIGHT - (2 * BatteryPageConfig.BATTERY_POWER_BORDER_SIZE),
                color=self.color
            )


class BatteryChargingIcon:
    def __init__(self, screen):
        self.screen = screen
        self.charging = False
    
    def update(self, is_charging):
        self.charging = is_charging
    
    def draw(self):
        if self.charging:
            self.screen.draw_image(
                x=BatteryPageConfig.CHARGING_ICON_X,
                y=BatteryPageConfig.CHARGING_ICON_Y,
                width=BatteryPageConfig.CHARGING_ICON_SIZE,
                height=BatteryPageConfig.CHARGING_ICON_SIZE,
                path=IconPaths.Lightning,
                replace_with={
                    PageConfig.ICON_TRUE_COLOR: BatteryPageConfig.DEFAULT_COLOR, 
                    PageConfig.ICON_FALSE_COLOR: BatteryPageConfig.BACKGROUND_COLOR
                },
            )
            
        else:
            self.screen.draw_image(
                x=BatteryPageConfig.CHARGING_ICON_X,
                y=BatteryPageConfig.CHARGING_ICON_Y,
                width=BatteryPageConfig.CHARGING_ICON_SIZE,
                height=BatteryPageConfig.CHARGING_ICON_SIZE,
                path=IconPaths.Unplugged,
                replace_with={
                    PageConfig.ICON_TRUE_COLOR: BatteryPageConfig.DEFAULT_COLOR,
                    PageConfig.ICON_FALSE_COLOR: BatteryPageConfig.BACKGROUND_COLOR
                },
            )


class BatteryPageStates:
    IDLE = 0
    LEAVE = 1


class BatteryPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.state = ValueManager(BatteryPageStates.IDLE)
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        self.battery_level = ValueManager(87)
        self.battery_charging = ValueManager(int(True))
        
        self.components = None
        self._initiate_components()
        
    
    def _initiate_components(self):
        self.components = {
            'percentage_text':  Text(
                                    screen=self.screen, 
                                    text='', 
                                    text_size=BatteryPageConfig.BATTERY_POWER_TEXT_SIZE, 
                                    color=BatteryPageConfig.DEFAULT_COLOR,
                                    x_marking=BatteryPageConfig.BATTERY_POWER_TEXT_X,
                                    y_marking=BatteryPageConfig.BATTERY_POWER_TEXT_Y
                                ),
            'percentage_bar':   BatteryPowerBar(screen=self.screen),
            'charging_icon':    BatteryChargingIcon(screen=self.screen)
        }
    
        
    def reset_states(self, args):
        self.state.overwrite(BatteryPageStates.IDLE)
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
        # battery_level and battery_charging should NOT be reset!!
    
    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
    
        
    def handle_task(self, task_info):
        if not self.busy.reveal():
            self.busy.overwrite(int(True))
        
            if task_info['task'] == 'UPDATE_BATTERY_STATE':
                print(task_info) 
                self.battery_level.overwrite(task_info['battery_level'])
                self.battery_charging.overwrite(task_info['battery_charging'])
            
            elif task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                pass
            
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                pass
            
            elif task_info['task'] == 'ENTER_SELECT':
                pass
            
            elif task_info['task'] == 'OUT_RESUME':
                self.state.overwrite(BatteryPageStates.LEAVE)
                # Return to menu when display is done
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'MenuPage',
                            'args': None,
                        }
                        # return 'MenuPage', None
            
            elif task_info['task'] == 'PAGE_EXPIRED':
                self.state.overwrite(BatteryPageStates.LEAVE)
                while True:
                    if self.display_completed.reveal():
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'EmotionPage',
                            'args': None,
                        }
                        # return 'EmotionPage', None
            
            self.busy.overwrite(int(False))

            
    
    def _display(self):
        while True:
            
            self.screen.fill_screen(theme_colors.Primary)
            
            state = self.state.reveal()
            battery_level = self.battery_level.reveal()
            battery_charging = self.battery_charging.reveal()
            
            if state == BatteryPageStates.LEAVE:
                break
            
            self.components['charging_icon'].update(battery_charging)
            self.components['percentage_text'].text = str(battery_level) + '%'
            self.components['percentage_bar'].update(battery_level, battery_charging)
            
            
            for component_key in self.components:
                self.components[component_key].draw()
            
            self.screen.update()
            time.sleep(0.1)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))
