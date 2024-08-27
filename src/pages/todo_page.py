import multiprocessing
import time
import sqlite3


from pages.pages_utils import theme_colors, PageConfig, IconPaths, Text
from value_manager import ValueManager
from pages.page import Page


class TodoPageConfig:
    TABLE_NAME = 'todo'
    
    NO_TASK_MESSAGE_COLOR = theme_colors.Danger
    NO_TASK_MESSAGE_SIZE = 15
    
    TODO_TASK_RECT_BORDER = 1
    TODO_TASK_RECT_X = 6
    TODO_TASK_RECT_W = 147
    TODO_TASK_RECT_DEFAULT_H = 30
    
    TODO_TASK_ICON_SIZE = 12
    TODO_TASK_ICON_X_LEFT_MARGIN = 5
    TODO_TASK_ICON_Y_TOP_MARGIN = 12
    
    TODO_TASK_DUE_DATE_Y_TOP_MARGIN = 2
    TODO_TASK_LINE_HEIGHT = 15
    TODO_TASK_Y_MARGIN = 10
    
    TODO_TASK_FONT_X = 27
    TODO_TASK_FONT_SIZE_L = 12
    TODO_TASK_FONT_SIZE_S = 10
    

class TodoTask():
    def __init__(self, screen, task_info):
        
        self.screen = screen
        self.y = None
        
        self.task_id = task_info[0] 
        self.task_name = task_info[1]
        self.task_due_date = task_info[2]
        self.task_priority = task_info[3]
        self.task_is_active = task_info[4]
        self.task_updated_at = task_info[5]
        
        self.border_color = theme_colors.Font
        self.icon_color = theme_colors.Font
        self.due_date_color = theme_colors.Info
        self.task_name_color = theme_colors.Font
        
        self.due_date_text = 'due: ' + self.task_due_date if self.task_due_date else 'no due date information'
        self.task_name_lines = []
        self.height = TodoPageConfig.TODO_TASK_RECT_DEFAULT_H - TodoPageConfig.TODO_TASK_LINE_HEIGHT + TodoPageConfig.TODO_TASK_DUE_DATE_Y_TOP_MARGIN

        current_line = ''
        for c in self.task_name:
            if len(current_line) == 20:
                self.task_name_lines.append(current_line)
                self.height += TodoPageConfig.TODO_TASK_LINE_HEIGHT
                if c == ' ':
                    current_line = ''
                    pass
                else:
                    current_line = '-' + c
            else:
                current_line += c
            
        if current_line != '':
            self.task_name_lines.append(current_line)      
            self.height += TodoPageConfig.TODO_TASK_LINE_HEIGHT
            
    
    def hover(self):
        self.border_color = theme_colors.Warning
        self.icon_color = theme_colors.Warning
        self.due_date_color = theme_colors.Muted
        self.task_name_color = theme_colors.Warning
    
    
    def unhover(self):
        self.border_color = theme_colors.Font
        self.icon_color = theme_colors.Font
        self.due_date_color = theme_colors.Info
        self.task_name_color = theme_colors.Font
    
    
    def draw(self):
        if self.y != None:
            self.screen.draw_rectangle(
                x=TodoPageConfig.TODO_TASK_RECT_X, 
                y=self.y, 
                xlen=TodoPageConfig.TODO_TASK_RECT_W, 
                ylen=self.height,
                color=self.border_color)
            self.screen.draw_rectangle(
                x=TodoPageConfig.TODO_TASK_RECT_X + TodoPageConfig.TODO_TASK_RECT_BORDER, 
                y=self.y + TodoPageConfig.TODO_TASK_RECT_BORDER, 
                xlen=TodoPageConfig.TODO_TASK_RECT_W - (2 * TodoPageConfig.TODO_TASK_RECT_BORDER), 
                ylen=self.height - (2 * TodoPageConfig.TODO_TASK_RECT_BORDER),
                color=PageConfig.BACKGROUND_COLOR)
            self.screen.draw_image(
                x=TodoPageConfig.TODO_TASK_RECT_X + TodoPageConfig.TODO_TASK_ICON_X_LEFT_MARGIN, 
                y=self.y + TodoPageConfig.TODO_TASK_ICON_Y_TOP_MARGIN, 
                width=TodoPageConfig.TODO_TASK_ICON_SIZE,
                height=TodoPageConfig.TODO_TASK_ICON_SIZE,
                path=IconPaths.Unchecked,
                replace_with={
                    PageConfig.ICON_TRUE_COLOR: self.icon_color,
                    PageConfig.ICON_FALSE_COLOR: theme_colors.Primary
                })
            self.screen.draw_text(
                x=TodoPageConfig.TODO_TASK_FONT_X,
                y=self.y + TodoPageConfig.TODO_TASK_DUE_DATE_Y_TOP_MARGIN,
                text=self.due_date_text,
                size=TodoPageConfig.TODO_TASK_FONT_SIZE_S,
                color=self.due_date_color
            )        
            current_y = self.y + TodoPageConfig.TODO_TASK_FONT_SIZE_L + TodoPageConfig.TODO_TASK_DUE_DATE_Y_TOP_MARGIN
            for line in self.task_name_lines:
                self.screen.draw_text(
                    x=TodoPageConfig.TODO_TASK_FONT_X,
                    y=current_y,
                    text=line,
                    size=TodoPageConfig.TODO_TASK_FONT_SIZE_L,
                    color=self.task_name_color
                )
                current_y += TodoPageConfig.TODO_TASK_LINE_HEIGHT
 

class TodoPageScroll:
    NONE = 0
    DOWN = -1
    UP = 1


class TodoPage(Page):
    def __init__(self, screen):
        self.screen = screen
        
        # Handlers for SQL database
        self.conn = sqlite3.connect(PageConfig.DB_PATH)
        self.cursor = self.conn.cursor()
        
        # States
        self.busy = ValueManager(int(False))
        self.display_completed = ValueManager(int(False))
        self.hovered_id = ValueManager(0)
        self.scroll = ValueManager(TodoPageScroll.NONE) 
        self.select = ValueManager(int(False))
        self.leave = ValueManager(int(False))
        
        # Components to draw
        self.tasks = None     
        self.task_components = None
        self.no_task_message_components = None
        self._initiate_tasks()  
    
    
    def _initiate_tasks(self):
        
        # Get active tasks from SQL database
        self.cursor.execute(
            f'''
            SELECT * 
            FROM {TodoPageConfig.TABLE_NAME}
            WHERE is_active == 1
            '''
        )
        tasks = self.cursor.fetchall()
        
        # Initiate hovered_id
        if not self.hovered_id:
            self.hovered_id = ValueManager(0)
        else:
            self.hovered_id.overwrite(0)
        
        # Initiate task components
        self.task_components = []
        for task in tasks:
            self.task_components.append(
                TodoTask(
                    screen=self.screen,
                    task_info=task
                )
            )
        
        # Set y value of task components
        current_y = TodoPageConfig.TODO_TASK_Y_MARGIN
        hovered_id = self.hovered_id.reveal()
        current_id = hovered_id
        counts = 0
        
        while current_y < PageConfig.SCREEN_HEIGHT and counts < len(tasks):
            self.task_components[current_id].hovered = (current_id == hovered_id)
            self.task_components[current_id].y = current_y
            
            current_y += self.task_components[current_id].height
            current_y += TodoPageConfig.TODO_TASK_Y_MARGIN
            
            current_id += 1
            current_id %= len(self.task_components)
            
            counts += 1

        # Set the hovered task component to hover state
        if len(self.task_components) != 0:
            self.task_components[hovered_id].hover()
        
        # Initiate no_task_message_components
        self.no_task_message_components = [
            Text(
                screen=self.screen,
                text='Nothing to do',
                text_size=TodoPageConfig.NO_TASK_MESSAGE_SIZE,
                color=TodoPageConfig.NO_TASK_MESSAGE_COLOR,
                x_marking=TodoPageConfig.TODO_TASK_FONT_X,
                y_marking=TodoPageConfig.TODO_TASK_Y_MARGIN
            ),
            Text(
                screen=self.screen,
                text='you\'re all set  :D',
                text_size=TodoPageConfig.NO_TASK_MESSAGE_SIZE,
                color=TodoPageConfig.NO_TASK_MESSAGE_COLOR,
                x_marking=TodoPageConfig.TODO_TASK_FONT_X,
                y_marking=TodoPageConfig.TODO_TASK_Y_MARGIN + TodoPageConfig.TODO_TASK_LINE_HEIGHT
            )
        ]
        

    def reset_states(self, args):
        self.busy.overwrite(int(False))
        self.display_completed.overwrite(int(False))
        self.hovered_id.overwrite(0)
        self.scroll.overwrite(TodoPageScroll.NONE)
        self._initiate_tasks()
    
    
    def start_display(self):
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
 
    
    def handle_task(self, task_info):
        if not self.busy.reveal():
            self.busy.overwrite(int(True))
            
            if task_info['task'] == 'MOVE_CURSOR_LEFT_DOWN':
                self.scroll.overwrite(TodoPageScroll.DOWN)
            elif task_info['task'] == 'MOVE_CURSOR_RIGHT_UP':
                self.scroll.overwrite(TodoPageScroll.UP)
            elif task_info['task'] == 'ENTER_SELECT':
                self.select.overwrite(int(True))
            elif task_info['task'] == 'OUT_RESUME':
                self.leave.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        # return 'MenuPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'MenuPage',
                            'args': None,
                        }
            
            elif task_info['task'] == 'PAGE_EXPIRED':
                self.leave.overwrite(int(True))
                while True:
                    if self.display_completed.reveal():
                        # return 'EmotionPage', None
                        return {
                            'type': 'NEW_PAGE',
                            'page': 'EmotionPage',
                            'args': None,
                        }
                    
            
            self.busy.overwrite(int(False))


    def _display(self):
        while True:
            
            self.screen.fill_screen(theme_colors.Primary)
            
            if self.leave.reveal():
                self.leave.overwrite(int(False))
                break
            
            elif self.task_components != []:
                
                # Reveal states
                hovered_id = self.hovered_id.reveal()
                scroll = self.scroll.reveal()
                select = self.select.reveal()
                
                components_moved = True
                
                # Work with components according to states
                if scroll == TodoPageScroll.DOWN:
                    self.task_components[hovered_id].unhover()
                    hovered_id += 1
                    hovered_id %= len(self.task_components)
                    self.task_components[hovered_id].hover()
                    self.hovered_id.overwrite(hovered_id)
                    self.scroll.overwrite(TodoPageScroll.NONE)
                    
                elif scroll == TodoPageScroll.UP:
                    self.task_components[hovered_id].unhover()
                    hovered_id -= 1
                    hovered_id %= len(self.task_components)
                    self.task_components[hovered_id].hover()
                    self.hovered_id.overwrite(hovered_id)
                    self.scroll.overwrite(TodoPageScroll.NONE)
                    
                elif select:

                    try:
                        self.cursor.execute(
                            f'''
                            UPDATE {TodoPageConfig.TABLE_NAME}
                            SET is_active = 0
                            WHERE id = {self.task_components[hovered_id].task_id};
                            '''
                        )
                        self.conn.commit()
                        
                    except Exception as e:
                        print(f'An error ocurred: {e}')
                    
                    # Hovering on the last item
                    if hovered_id == len(self.task_components) - 1:
                        hovered_id -= 1
                        self.task_components.pop()
                        self.hovered_id.overwrite(hovered_id)
                    
                    else:
                        self.task_components.pop(hovered_id)
                        
                    if len(self.task_components) != 0:
                        self.task_components[hovered_id].hover()
                    self.select.overwrite(int(False))

                else:
                    components_moved = False
                
                
                # Move components
                if components_moved:
                    hovered_id = self.hovered_id.reveal()
                    current_y = TodoPageConfig.TODO_TASK_Y_MARGIN
                    current_id = hovered_id
                    counts = 0
                    
                    while current_y < PageConfig.SCREEN_HEIGHT and counts < len(self.task_components):
                        self.task_components[current_id].hovered = (current_id == hovered_id)
                        self.task_components[current_id].y = current_y
                        
                        current_y += self.task_components[current_id].height
                        current_y += TodoPageConfig.TODO_TASK_Y_MARGIN
                        
                        current_id += 1
                        current_id %= len(self.task_components)
                        
                        counts += 1
                    
                    while current_id != hovered_id and counts < len(self.task_components):
                        self.task_components[current_id].y = None
                        current_id += 1
                        current_id %= len(self.task_components)
                        
                        counts += 1
                
                # Draw components
                for task_component in self.task_components:
                    task_component.draw()
            
            # Draw no_task_message_compoments if there are no task components
            else:
                for no_task_message_component in self.no_task_message_components:
                    no_task_message_component.draw()
            
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))