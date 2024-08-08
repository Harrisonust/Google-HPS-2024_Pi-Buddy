class Page:
    def __init__(self, name, buttons, debug=False):
        self.name = name
        self.buttons = buttons
        self.current_button_index = 0
        self.debug = debug

    def render(self):
        # Render the page on the screen
        print(f"Rendering page: {self.name}")
        for i, button in enumerate(self.buttons):
            if i == self.current_button_index:
                print(f"> {button} <")
            else:
                print(button)

    def navigate(self, direction):
        if direction == 'up':
            self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
        elif direction == 'down':
            self.current_button_index = (self.current_button_index + 1) % len(self.buttons)

    def select(self):
        selected_button = self.buttons[self.current_button_index]
        print(f"Selected: {selected_button}")
        # Handle the selection logic
