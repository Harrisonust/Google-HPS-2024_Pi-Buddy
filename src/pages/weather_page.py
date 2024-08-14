import time
import datetime
import multiprocessing
import requests

from pages.pages_utils import theme_colors, PageConfig, Text, IconTextBox
from value_manager import ValueManager

class WeatherPage():
    def __init__(self, screen):
        self.screen = screen
        self.weather_page_busy = ValueManager(int(False))
        
        self.title_box = None
        self.last_fetch_tick = 0
        self.temperature = None
        self.humidity = None
        self.last_observe_time = None 
        
        self._initiate_components()

        self.display_process = multiprocessing.Process(target=self._display)
        self.display_process.start()

    def _initiate_components(self):
        self.text_current_time = Text(
            screen=self.screen,
            text='',
            text_size=12,
            color=PageConfig.DEFAULT_COLOR,
            x_marking=38,
            y_marking=115
        )
        
        self.text_temperature = Text(
            screen=self.screen,
            text='',
            text_size=25,
            color=PageConfig.DEFAULT_COLOR,
            x_marking=40,
            y_marking=45
        )
        
        self.text_humidity = Text(
            screen=self.screen,
            text='',
            text_size=20,
            color=PageConfig.DEFAULT_COLOR,
            x_marking=80,
            y_marking=70
        )

        self.title_box_title = IconTextBox(
            screen=self.screen,
            x_marking=80,
            y_marking=20,
            box_width=PageConfig.ICON_TEXT_BOX_WIDTH,
            box_height=PageConfig.ICON_TEXT_BOX_HEIGHT,
            text='Weather',
            text_size=PageConfig.ICON_TEXT_BOX_TEXT_SIZE,
            color=PageConfig.TITLE_COLOR,
            icon_path='./icons/weather.png',
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
            if time.time() - self.last_fetch_tick > 60:
                print('get_weather')
                self.last_observe_time, _, _, _, _, self.temperature, self.humidity = self.get_weather()
                self.last_fetch_tick = time.time()

            self.screen.fill_screen(PageConfig.BACKGROUND_COLOR)
            
            current_time = datetime.datetime.now()
            
            self.title_box_title.draw()
            
            self.screen.draw_text(70, 103, 'Last updated at', 12)
            self.text_current_time.text = f'{self.last_observe_time}'
            self.text_current_time.draw()
            
            self.text_temperature.text = f'{self.temperature}°C'
            self.text_temperature.draw()

            self.text_humidity.text = f'{self.humidity}%'
            self.text_humidity.draw()

            self.screen.update()
            time.sleep(0.1)
            self.screen.clear()

    def get_weather(self):

        url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001'
        params = {
            'Authorization': 'CWA-223E922B-B77E-4E5D-BFF2-9DE9D5BB7A57',
            'WeatherElement': 'Weather,AirTemperature,RelativeHumidity',
            'StationId': 'C0D680',
        }

        response = requests.get(url, params=params)
        if response.status_code != 200: raise ValueError('unable to get weather data')
        data = response.json()
        location = data['records']['Station']
        
        for i in location:
            name = i['StationName']            
            city = i['GeoInfo']['CountyName']  
            area = i['GeoInfo']['TownName'] 
            weather = i['WeatherElement']['Weather']
            temperature = i['WeatherElement']['AirTemperature']
            humidity = i['WeatherElement']['RelativeHumidity']
            obs_time = i['ObsTime']['DateTime']
            #print(city, area, name, weather, temperature, humidity)
            return (obs_time[:19], city, area, name, weather, temperature, humidity)
