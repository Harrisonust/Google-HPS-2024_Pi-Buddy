class ThemeColors:
    _themes = {
        'EvaDark': {
            'Primary':      0x2966,     # blue-grey
            'Secondary':    0x322c,     # blue-grey 
            'Teritary':     0x1acd,     # dark-teal
            'Muted':        0x5b73,     # blue-grey
            'Font':         0xb5f8,     # ice-blue
            'Highlight':    0xd35c,     # lavendar
            'Success':      0x5df8,     # teal
            'Danger':       0xf16f,     # pink
            'Warning':      0x64bd,     # blue
            'Info':         0x9dcb,     # olive-green
            'Contrast':     0xfc8e,     # rose
        },
        'UprightCrimson': {
            'Primary':      0xffff,     # white
            'Secondary':    0xf67d,     # lavendar
            'Teritary':     0xef5d,     # light-grey
            'Muted':        0xa514,     # grey
            'Font':         0x28c3,     # brown 
            'Highlight':    0x74c9,     # green
            'Success':      0x0473,     # dark-teal
            'Danger':       0xe8a7,     # red
            'Warning':      0xdd29,     # orange
            'Info':         0x042d,     # dark-green
            'Contrast':     0x92e7,     # brown
        }
    }

    def __init__(self, theme='EvaDark'):
        self.theme = None
        self.change_theme(theme)
        
    
    def change_theme(self, theme):
        if theme not in self._themes:
            raise ValueError(f'Unknown color theme {theme}')
        
        self.theme = theme
        for key, value in self._themes[self.theme].items():
            setattr(self, key, value)


theme_colors = ThemeColors()


class IconPaths:
    # Menu icons
    Weather = './icons/cloud_sun.png'
    Battery = './icons/battery.png'
    Photograph = './icons/photograph.png'
    Film = './icons/film.png'
    Timer = './icons/timer.png'
    Time = './icons/time.png'
    Surprise = './icons/surprise.png'
    Todo = './icons/checked_bordered.png'
    
    # Timer icons
    Menu = './icons/menu.png'
    Reset = './icons/reset.png'
    Proceed = './icons/proceed.png'
    
    # Weather icons
    Sun = './icons/sun.png'
    Moon = './icons/moon.png'
    CloudSun = './icons/cloud_sun.png'
    CloudMoon = './icons/cloud_moon.png'
    Cloud = './icons/cloud.png'
    Rain = './icons/rain.png'
    Lightning = './icons/lightning.png'
    Fog = './icons/fog.png'
    Snow = './icons/snow.png'
    Ice = './icons/ice.png'
    RainLightning = './icons/rain_lightning.png'
    RainSnow = './icons/rain_snow.png'
    IceLightning = './icons/ice_lightning.png'
    SnowLightning = './icons/snow_lightning.png'

    # Todo icons
    Unchecked = './icons/unchecked.png'
    Checked_Bordered = './icons/checked_bordered.png'
    Checked_Filled = './icons/checked_filled.png'

class PageConfig():
    
    DB_PATH = 'database/database.db'
    
    SCREEN_HEIGHT = 128
    SCREEN_WIDTH = 160
    
    ICON_TRUE_COLOR = (255, 255, 255)
    ICON_FALSE_COLOR = (0, 0, 0)
    DEFAULT_COLOR = theme_colors.Font
    HOVERED_COLOR = theme_colors.Highlight
    TITLE_COLOR = theme_colors.Contrast
    BACKGROUND_COLOR = theme_colors.Primary
    
    PAGE_TITLE_BOX_WIDTH = 110
    PAGE_TITLE_BOX_HEIGHT = 35
    PAGE_TITLE_BOX_BORDER = 2
    PAGE_TITLE_BOX_ICON_Y_RATIO = 0.8
    PAGE_TITLE_BOX_ICON_X_MARGIN = 5
    PAGE_TITLE_BOX_TEXT_SIZE = 14
    
    BTN_WIDTH = 45
    BTN_HEIGHT = 18
    BTN_BORDER = 1
    BTN_ICON_Y_RATIO = 0.8
    BTN_ICON_X_MARGIN = 2
    BTN_TEXT_SIZE = 10



class IconTextBox():
    def __init__(self, screen, x_marking, y_marking, box_width, box_height, text, text_size, color, background_color, 
                 icon_path, icon_margin_x, icon_y_ratio, border=0, x_margin=0, y_margin=0,
                 x_mark_edge='Left', y_mark_edge='Top', icon_alignment='Left', icon_color_replacements=None):

        self.screen = screen

        self.display = True
        self.show_border = True if (border != 0) else False
        
        self.x_marking = x_marking
        self.y_marking = y_marking
        self.box_width = box_width
        self.box_height = box_height
        self.text = text 
        self.text_size = text_size
        self.color = color
        self.background_color = background_color
        self.icon_path = icon_path
        self.icon_margin_x = icon_margin_x
        self.icon_y_ratio = icon_y_ratio
        self.border = border        
        self.x_margin = x_margin 
        self.y_margin = y_margin 
        self.x_mark_edge = x_mark_edge
        self.y_mark_edge = y_mark_edge
        self.icon_alignment = icon_alignment
        self.icon_color_replacements = icon_color_replacements
        
        self.outer_box_x, self.outer_box_y = None, None
        self.outer_box_width, self.outer_box_height = None, None
        self.inner_box_x, self.inner_box_y = None, None
        self.inner_box_width, self.inner_box_height = None, None
        self.text_x, self.text_y = None, None
        self.icon_x, self.icon_y = None, None
        self.icon_size = None
        self._reset_dim()
        
    
    def _reset_dim(self):
        
        # Boxes
        self.outer_box_width, self.outer_box_height = self.box_width, self.box_height
        self.inner_box_width, self.inner_box_height = self.box_width - (2 * self.border), self.box_height - (2 * self.border)
        
        self.outer_box_x = None
        if self.x_mark_edge =='Center':
            self.outer_box_x = self.x_marking  - (self.box_width // 2)
        elif self.x_mark_edge == 'Left':
            self.outer_box_x = self.x_marking
        elif self.x_mark_edge == 'Right':
            self.outer_box_x = self.x_marking - (self.box_width)
        self.inner_box_x = self.outer_box_x + self.border
        
        self.outer_box_y = None
        if self.y_mark_edge == 'Center':
            self.outer_box_y = self.y_marking - (self.box_height // 2)
        elif self.y_mark_edge == 'Top':
            self.outer_box_y = self.y_marking
        elif self.y_mark_edge == 'Bottom':
            self.outer_box_y = self.y_marking - (self.box_height)
        self.inner_box_y = self.outer_box_y + self.border
        
        # Icon
        self.icon_size = int((self.outer_box_height - (2 * self.border)) * self.icon_y_ratio)
        self.icon_x = None
        if self.icon_alignment == 'Left':
            self.icon_x = self.outer_box_x + self.border + self.icon_margin_x
        elif self.icon_alignment == 'Right':
            self.icon_x = self.outer_box_x + self.outer_box_width - self.border - self.icon_margin_x - self.icon_size
        self.icon_y = self.outer_box_y + (self.outer_box_height // 2) - (self.icon_size // 2)
        
        # Text
        self.text_x = None
        if self.icon_alignment == 'Left':
            self.text_x = self.outer_box_x + self.border + self.icon_size + (self.icon_margin_x * 2)
        elif self.icon_alignment == 'Right':
            self.text_x = self.outer_box_x + self.border + self.icon_margin_x
        self.text_y = self.outer_box_y + (self.outer_box_height // 2) - ((self.text_size + 4) // 2)
    
    
    def draw(self):
        if self.display:
            if self.show_border:
                self.screen.draw_rectangle(self.outer_box_x, self.outer_box_y, self.outer_box_width, self.outer_box_height, self.color)
                self.screen.draw_rectangle(self.inner_box_x, self.inner_box_y, self.inner_box_width, self.inner_box_height, self.background_color)
            
            self.screen.draw_image(self.icon_x, self.icon_y, self.icon_size, self.icon_size, self.icon_path, self.icon_color_replacements)
            self.screen.draw_text(self.text_x, self.text_y, self.text, self.text_size, self.color)
        
    

class OptionBox(IconTextBox):
    def __init__(self, screen, default_x, default_y, text, icon_path, box_hover_scale, border_hover_scale, default_color, 
                 hovered_color, background_color, default_box_width, default_box_height, default_border, default_icon_x_margin,
                 default_text_size, icon_y_ratio, y_margin=0):
        
        self.screen = screen
        self.default_x = default_x
        self.default_y = default_y
        self.text = text
        self.icon_path = icon_path
        self.box_hover_scale = box_hover_scale
        self.border_hover_scale = border_hover_scale
        self.default_color = default_color
        self.hovered_color = hovered_color
        self.background_color = background_color
        self.default_box_width = default_box_width
        self.default_box_height = default_box_height
        self.default_border = default_border
        self.default_icon_x_margin = default_icon_x_margin
        self.default_text_size = default_text_size
        self.y_margin = y_margin
        self.icon_y_ratio = icon_y_ratio
        
        
        self.default_icon_color_replacements={
            PageConfig.ICON_TRUE_COLOR: self.default_color,
            PageConfig.ICON_FALSE_COLOR: self.background_color
        }
        self.hovered_icon_color_replacements={
            PageConfig.ICON_TRUE_COLOR: self.hovered_color,
            PageConfig.ICON_FALSE_COLOR: self.background_color
        }

        super().__init__(
            screen=self.screen, 
            x_marking=self.default_x, 
            y_marking=self.default_y, 
            box_width=self.default_box_width, 
            box_height=self.default_box_height,
            text=self.text,
            text_size=self.default_text_size,
            color=self.default_color,
            background_color=self.background_color,
            icon_path=self.icon_path,
            icon_margin_x=self.default_icon_x_margin,
            icon_y_ratio=self.icon_y_ratio,
            border=self.default_border,
            y_margin=self.y_margin,
            icon_color_replacements=self.default_icon_color_replacements
        )
    
    
    def reset(self):
        # Set parameters to default value
        self.box_width = self.default_box_width
        self.box_height = self.default_box_height
        self.border = self.default_border
        self.color = self.default_color
        self.icon_x_margin = self.default_icon_x_margin
        self.text_size = self.default_text_size
        self.x_marking = self.default_x
        self.y_marking = self.default_y
        self.icon_color_replacements = self.default_icon_color_replacements
        self._reset_dim()
        
    
    def hover(self):
        # Set parameters to hover mode
        self.box_width = int(self.default_box_width * self.box_hover_scale)
        self.box_height = int(self.default_box_height * self.box_hover_scale)
        self.border = int(self.default_border * self.border_hover_scale)
        self.color = self.hovered_color
        self.icon_size = int((self.box_height - (2 * self.border)) * self.icon_y_ratio)
        self.icon_x_margin = int(self.default_icon_x_margin * self.box_hover_scale)
        self.text_size = int(self.default_text_size * self.box_hover_scale)
        self.x_marking = int(self.default_x - (self.box_width * (self.box_hover_scale - 1) / 2))
        self.y_marking = int(self.default_y - (self.box_height * (self.box_hover_scale - 1) / 2))
        self.icon_color_replacements = self.hovered_icon_color_replacements
        self._reset_dim()
    
    
class Text:
    def __init__(self, screen, text, text_size, color, 
                 x_marking, y_marking, x_mark_edge='Left', y_mark_edge='Top'):
        
        self.display = True
        self.screen = screen
        self.text = text
        self.text_size = text_size
        self.color = color
        
        self.x = None
        if x_mark_edge == 'Center':
            self.x = x_marking - ((self.text_size - 4) * len(self.text) // 2)
        elif x_mark_edge == 'Left':
            self.x = x_marking
        elif x_mark_edge == 'Right':
            self.x = x_marking - ((self.text_size - 4) * len(self.text))
        else:
            raise ValueError(f'Invalid x_mark_edge "{x_mark_edge}" for text "{self.text}"')

        
        self.y = None
        if y_mark_edge == 'Center':
            self.y = y_marking - ((self.text_size + 4) // 2)
        elif y_mark_edge == 'Top':
            self.y = y_marking
        elif y_mark_edge == 'Bottom':
            self.y = y_marking - (self.text_size + 4)
        else:
            raise ValueError(f'Invalid y_mark_edge "{y_mark_edge}" for text "{self.text}"')
    
    
    def draw(self):
        if self.display:
            self.screen.draw_text(self.x, self.y, self.text, self.text_size, self.color)
            


