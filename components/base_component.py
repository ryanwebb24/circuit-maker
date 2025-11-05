from abc import ABC, abstractmethod
from components.enums import Orientation


class Component(ABC):
    def __init__(self, name: str = "", nodes:list = [], x:int = 0, y:int = 0, orientation:Orientation = Orientation.E):
        self.name = name
        self.nodes = nodes
        self.x = x
        self.y = y
        self.orientation = orientation

    @abstractmethod
    def stamp(self, G, I):
        """
        Add this component's contribution to the circuit matrices.

        Parameters:
        - G: Conductance matrix
        - I: Current vector
        """
        pass

    @abstractmethod
    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        """
        Draw the component at pixel coordinates on a pygame surface.

        Parameters:
        - screen: pygame Surface to draw on
        - px, py: pixel center coordinates where the component should be drawn
        - cell_w, cell_h: pixel size of a single grid cell (width, height)
        """
        pass
    
    