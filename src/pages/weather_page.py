import time
import math
from datetime import datetime
import multiprocessing
import requests
import sys


from pages.pages_utils import theme_colors, PageConfig, Text, IconPaths
from value_manager import ValueManager
from pages.page import Page



class WeatherPageConfig:
    URL = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001'
    STATION_ID = 'C0D680'
    AUTHORIZATION = 'CWA-223E922B-B77E-4E5D-BFF2-9DE9D5BB7A57'
    
    TEXT_X = 10
    TEXT_Y_1 = 25
    TEXT_Y_2 = 42
    TEXT_Y_3 = 95
    ICON_X = 105
    ICON_Y = 47
    
    TEXT_SIZE_S = 11
    TEXT_SIZE_L = 40
    ICON_SIZE = 40
    

class WeatherPageIcon:
    def __init__(self, screen, x, y, size, color, background_color):
        
        self.screen = screen
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.background_color = background_color
        
        self.icon_path = None
        
        self.weather_state_day_dict = {
            '晴': IconPaths.Sun,
            '多雲': IconPaths.CloudSun,
            '陰': IconPaths.Cloud
        }
        
        self.weather_state_night_dict = {
            '晴': IconPaths.Moon,
            '多雲': IconPaths.CloudMoon,
            '陰': IconPaths.Cloud
        }
        
        self.weather_phenomena_dict = {
        '有霾': IconPaths.Fog,                         
        '有靄': IconPaths.Fog,     
        '有閃電': IconPaths.Lightning,
        '有雷聲': IconPaths.Lightning,
        '有霧': IconPaths.Fog,
        '有雨': IconPaths.Rain,
        '有雨雪': IconPaths.RainSnow,
        '有大雪': IconPaths.Snow,
        '有雪珠': IconPaths.Snow,
        '有冰珠': IconPaths.Ice,
        '有陣雨': IconPaths.Rain,
        '陣雨雪': IconPaths.RainSnow,
        '有雹': IconPaths.Ice,
        '有雷雨': IconPaths.RainLightning,
        '有雷雪': IconPaths.SnowLightning,
        '有雷雹': IconPaths.IceLightning,
        '大雷雨': IconPaths.RainLightning,
        '大雷雹': IconPaths.IceLightning,
        '有雷': IconPaths.Lightning
        }
    
    def set_weather(self, weather_str):

        # Show weather phenomena if any
        for key in self.weather_phenomena_dict:
            if key in weather_str:
                self.icon_path = self.weather_phenomena_dict[key]
                return
        
        current_hour = int(datetime.now().strftime("%H"))
        is_daytime = current_hour > 6 and current_hour < 18
        
        if is_daytime:
            for key in self.weather_state_day_dict:
                if key in weather_str:
                    self.icon_path = self.weather_state_day_dict[key]
                    return
        
        for key in self.weather_state_night_dict:
                if key in weather_str:
                    self.icon_path = self.weather_state_day_dict[key]
                    return
        
        self.icon_path = None
        
        
    def draw(self):
        if self.icon_path != None:
            self.screen.draw_image(
                x=self.x,
                y=self.y, 
                width=self.size, 
                height=self.size, 
                path=self.icon_path, 
                replace_with={
                    PageConfig.ICON_TRUE_COLOR: self.color, 
                    PageConfig.ICON_FALSE_COLOR: self.background_color
                }
            )
        

class WeatherPageStates:
    IDLE = 0
    EXITING = 1


class WeatherPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        self.state = ValueManager(WeatherPageStates.IDLE)
        self.weather_page_busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))

        self.components = []
        self._initiate_components()


    def _initiate_components(self):        
        self.components = {
            'high_low_temp': Text(self.screen, '', WeatherPageConfig.TEXT_SIZE_S, theme_colors.Highlight, WeatherPageConfig.TEXT_X, WeatherPageConfig.TEXT_Y_1),
            'temp': Text(self.screen, '', WeatherPageConfig.TEXT_SIZE_L, theme_colors.Info, WeatherPageConfig.TEXT_X, WeatherPageConfig.TEXT_Y_2),
            'humidity_apparent_temp': Text(self.screen, '', WeatherPageConfig.TEXT_SIZE_S, theme_colors.Warning, WeatherPageConfig.TEXT_X, WeatherPageConfig.TEXT_Y_3),
            'weather_icon': WeatherPageIcon(self.screen, WeatherPageConfig.ICON_X, WeatherPageConfig.ICON_Y, WeatherPageConfig.ICON_SIZE, theme_colors.Font, theme_colors.Primary)
        }


    def reset_states(self, args):
        self.state.overwrite(WeatherPageStates.IDLE)
        self.weather_page_busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
    
    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
        

    def handle_task(self, task_info):
        if not self.weather_page_busy.reveal():
            self.weather_page_busy.overwrite(int(True))
            
            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                pass
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                pass
            elif task_info['task'] == 'ENTER_SELECT':
                pass
            elif task_info['task'] == 'OUT_RESUME':
                self.state.overwrite(WeatherPageStates.EXITING)
                while True:
                    if self.display_completed.reveal():
                        # return 'MenuPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'MenuPage',
                            'args': None,
                        }
            elif task_info['task'] == 'PAGE_EXPIRED':
                self.state.overwrite(WeatherPageStates.EXITING)
                while True:
                    if self.display_completed.reveal():
                        # return 'EmotionPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'EmotionPage',
                            'args': None,
                        }
            
            self.weather_page_busy.overwrite(int(False))
            

    def _display(self):
        last_fetch_tick = 0
        while True:
            
            if self.state.reveal() == WeatherPageStates.EXITING:
                break
            
            if time.time() - last_fetch_tick > 60:
                weather, temp, daily_high, daily_low, humidity, wind_speed = self._get_weather()
                last_fetch_tick = time.time()
                self._set_weather_components(weather, temp, daily_high, daily_low, humidity, wind_speed)

            self.screen.fill_screen(PageConfig.BACKGROUND_COLOR)
            
            for component_key in self.components:
                self.components[component_key].draw()

            self.screen.update()
            time.sleep(0.1)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))
            
    
    def _set_weather_components(self, weather, temp, daily_high, daily_low, humidity, wind_speed):
        # Set weather components according to given data
        apparent_temp = self._calculate_apparent_temp(temp, humidity, wind_speed)
        
        self.components['high_low_temp'].text = f'High: {daily_high}° ·  Low: {daily_low}°'
        self.components['temp'].text = f'{temp}°'
        self.components['humidity_apparent_temp'].text = f'Humidity {humidity}%; feels like {apparent_temp}°'
        self.components['weather_icon'].set_weather(weather)


    def _get_weather(self):
        # Gets weather information from API
        params = {
            'Authorization': WeatherPageConfig.AUTHORIZATION,
            'StationId': WeatherPageConfig.STATION_ID,
        }

        response = requests.get(WeatherPageConfig.URL, params=params)
        if response.status_code != 200: 
            raise ValueError('unable to get weather data')
        
        data = response.json()
        sys.stdout.reconfigure(encoding='utf-8')
        location_data = data['records']['Station'][0]
        
        weather = location_data['WeatherElement']['Weather']
        temp = location_data['WeatherElement']['AirTemperature']
        daily_high = location_data['WeatherElement']['DailyExtreme']['DailyHigh']['TemperatureInfo']['AirTemperature']
        daily_low = location_data['WeatherElement']['DailyExtreme']['DailyLow']['TemperatureInfo']['AirTemperature']
        humidity = location_data['WeatherElement']['RelativeHumidity']
        wind_speed = location_data['WeatherElement']['WindSpeed']
        

        return weather, temp, daily_high, daily_low, humidity, wind_speed
    
    
    def _calculate_apparent_temp(self, temp, humidity, wind_speed):
        # Calculate apparent tempature; formula by Robert G. Steadman
        e = humidity * 0.01 * 6.105 * math.exp(17.27 * temp / (237.7 + temp))
        apparent_temp = (1.07 * temp) + (0.2 * e) - (0.65 * wind_speed) - 2.7 
        
        return round(apparent_temp, 1)