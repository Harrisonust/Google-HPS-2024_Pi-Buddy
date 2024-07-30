class Screen:
	def __init__(self):
		pass

	def draw_pixel(self, x: int, y: int, color) -> None: 
		pass

	def draw_line(self, x1: int, y1: int, x2: int, y2: int, color) -> None: 
		pass

	def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color, fill=False) -> None: 
		pass

	def draw_circle(self, x: int, y: int, radius: int, color, fill=False) -> None: 
		pass

	def draw_text(self, x: int, y: int, text: str, font, color) -> None: 
		pass

	def draw_image(self, x: int, y: int, image) -> None: 
		pass

	def update(self) -> None: 
		pass

	def clear(self) -> None: 
		pass

if __name__ == '__main__':
	pass
