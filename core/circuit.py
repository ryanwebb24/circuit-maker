from components.base_component import Component

class Circuit:
    def __init__(self, height:int = 64, width:int = 64):
        self.height = height
        self.width = width
        self.components = {}

    def add_component(self, component:Component):
        self.components[(component.x, component.y)] = component

    def remove_component(self, x:int, y:int):
        del self.components[(x,y)]

    def get_adjacent_components(self, x: int, y: int) -> tuple[bool, bool, bool, bool]:
        """Check for components in adjacent positions (up, right, down, left).
        
        Args:
            x: The x coordinate to check around
            y: The y coordinate to check around
            
        Returns:
            Tuple of (up, right, down, left) booleans indicating component presence
        """
        return (
            isinstance(self.components.get((x, y - 1)), Component),  # up
            isinstance(self.components.get((x + 1, y)), Component),  # right
            isinstance(self.components.get((x, y + 1)), Component),  # down
            isinstance(self.components.get((x - 1, y)), Component)   # left
        )