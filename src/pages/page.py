
import time
import multiprocessing


from value_manager import ValueManager


class Page():
    def __init__(self, screen):
        # Initialize self.screen
        self.screen = screen
        
        # Initilaize page components
        pass
        
        # Initialize page states
        self.display_completed = ValueManager(int(False))
        # self.state = ValueManager()
    
    
    def reset_states(self):
        # Reset page states; this function is called in menu_screen_handler before the start_display function 
        pass
    
    
    def start_display(self):
        self.display_completed.overwrite(int(False))
        display_process = multiprocessing.Process(target=self._display)
        display_process.start()
        
    
    def handle_task(self, task_info):
        # Handle tasks and returns the next-page-key in certain states 
        # after the _display process ends, indicated by self.display_completed
        '''
        if transit_page:
            self.state.overwrite(END_DISPLAY)
            while True:
                if self.display_completed.reveal():
                    return next_page_key
        '''
    
    
    def _display(self):
        # Screen update loop
        while True:
            self.screen.fill_screen()
            
            # Update states
            pass
            '''
            if self.state.reveal() == END_DISPLAY:
                break
            '''

            # Draw page components
            
            self.screen.update()
            time.sleep(0.01)
            self.screen.clear()
        
        self.display_completed.overwrite(int(True))