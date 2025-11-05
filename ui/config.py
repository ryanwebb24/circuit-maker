from enum import Enum

class Colors:
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (220, 220, 220)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

class WindowConfig:
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    BORDER = 100
    FPS = 60
    CAPTION = "Circuit Maker"

class ButtonConfig:
    # Dimensions
    WIDTH = 120
    HEIGHT = 32
    PADDING = 10
    SPACING = 5  # Space between buttons
    
    # Border
    BORDER_COLOR = (0, 0, 0)
    BORDER_WIDTH = 2
    
    # Font
    FONT_SIZE = 18
    
    # Colors
    COLORS = {
        'normal': (200, 200, 200),
        'hover': (220, 220, 220),
        'pressed': (160, 160, 160),
        'text': (0, 0, 0),
        'disabled': (150, 150, 150),
        'disabled_text': (100, 100, 100),
        'selected': (180, 200, 255),
        'selected_hover': (190, 210, 255),
        'selected_pressed': (160, 180, 255),
    }

class Tool(Enum):
    WIRE = "WIRE"
    RESISTOR = "RESISTOR"