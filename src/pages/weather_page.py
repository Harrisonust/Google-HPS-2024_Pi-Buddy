import time
import datetime
import multiprocessing

from pages.pages_utils import theme_colors, PageConfig, Text, IconTextBox
from value_manager import ValueManager

class WeatherPage():
    def __init__(self, screen):
        self.screen = screen
        self.weather_page_busy = ValueManager(int(False))
        
        self.title_box = None
        
        self._initiate_components()

        self.display_process = multiprocessing.Process(target=self._display)
        self.display_process.start()


    def _initiate_components(self):
        self.current_time = Text(
            screen=self.screen,
            text='',
            text_size=15,
            color=PageConfig.DEFAULT_COLOR,
            x_marking=20,
            y_marking=100
        )

        self.title_box = IconTextBox(
            screen=self.screen,
            x_marking=80,
            y_marking=20,
            box_width=PageConfig.ICON_TEXT_BOX_WIDTH,
            box_height=PageConfig.ICON_TEXT_BOX_HEIGHT,
            text='Weather',
            text_size=PageConfig.ICON_TEXT_BOX_TEXT_SIZE,
            color=PageConfig.TITLE_COLOR,
            icon_path='./icons/menu_timer.png',
            background_color=PageConfig.BACKGROUND_COLOR,
            icon_margin_x=PageConfig.ICON_TEXT_BOX_ICON_X_MARGIN,
            icon_y_ratio=PageConfig.ICON_TEXT_BOX_ICON_Y_RATIO,
            x_mark_edge='Center',
            y_mark_edge='Center',
            icon_alignment='Left',
            #icon_color_replacements=PageConfig.BACKGROUND_COLOR
        )

    def listen(self):
        raise TypeError(f'Invalid call to ScreenHandler "listen" function')

    def handle_task(self, task_info):
        if not self.weather_page_busy.reveal():
            self.weather_page_busy.overwrite(int(True))
            # do nothing lol
            self.weather_page_busy.overwrite(int(False))

    def _display(self):
        while True:
            self.screen.fill_screen(PageConfig.BACKGROUND_COLOR)
            
            current_time = datetime.datetime.now()
            self.title_box.draw()
            self.current_time.text=f"{datetime.date.today()} {current_time.hour}:{current_time.minute}:{current_time.second}"
            self.current_time.draw()
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
