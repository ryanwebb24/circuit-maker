from abc import ABC, abstractmethod

class Component(ABC):
    def __init__(self, name: str = "", nodes:list = [], x:int = 0, y:int = 0):
        self.name = name
        self.nodes = nodes
        self.x = x
        self.y = y

    @abstractmethod
    def stamp(self, G, I):
        """
        Add this component's contribution to the circuit matrices.

        Parameters:
        - G: Conductance matrix
        - I: Current vector
        """
        pass
    
    