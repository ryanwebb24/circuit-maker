from enum import Enum

class ComponentColors(Enum):
    # Store RGB tuples as the enum values so callers can directly get a color
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    @property
    def rgb(self):
        """Return the RGB tuple for this color."""
        return self.value

class Orientation(Enum):
    N = 1
    E = 2
    S = 3
    W = 4