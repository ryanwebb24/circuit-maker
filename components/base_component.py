from abc import ABC, abstractmethod
from components.enums import Orientation


class Component(ABC):
    def __init__(self, name: str = "", nodes:list = [], x:int = 0, y:int = 0, orientation:Orientation = Orientation.E):
        self.name = name
        self.nodes = nodes
        self.x = x
        self.y = y
        self.orientation = orientation
        
    def calculate_current(self, v1: float, v2: float) -> float:
        return 0.0  # Default implementation returns no current

    @abstractmethod
    def stamp(self, G, I):
        pass

    @abstractmethod
    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        pass
    
    