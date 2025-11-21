import pygame

from components.base_component import Component
from components.enums import ComponentColors, Orientation

class Wire(Component):
    def __init__(self, name:str = "wire", n1:int = 0, n2:int = 0, x:int = 0, y:int = 0, orientation:Orientation = Orientation.E, color:ComponentColors = ComponentColors.RED):
        super().__init__(name, [n1, n2], x, y)
        self.orientation = orientation
        self.color = color
        self._adjacent_components = (False, False, False, False)

    @property
    def adjacent_components(self):
        return self._adjacent_components
    
    @adjacent_components.setter
    def adjacent_components(self, adjacent_components:tuple[bool,bool,bool,bool] = (False, False, False, False)):
        '''
            Input is a tuple of 4 Booleans the layout being (N,E,S,W) true if there is a component in the polar coordinate
        '''
        if not isinstance(adjacent_components, tuple):
            raise ValueError("adjacent_component should be of type tuple")
        self._adjacent_components = adjacent_components

    def stamp(self, G, I):
        # Wire stamping is handled by the MNA solver's _stamp_passive_component method
        # This method exists for interface compatibility
        pass

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        if screen is None:
            return
        
        neighbors = self.adjacent_components

        # Wire visual size: fit inside one cell but leave some padding
        body_w = min(cell_w, cell_h) * 0.7
        half = body_w / 2.0
        
        # Initialize all endpoints at center
        top_y = py
        bottom_y = py
        left_x = px
        right_x = px
        
        # Round center points for pixel-perfect drawing
        center_x = int(round(px))
        center_y = int(round(py))

        # Extend lines based on neighbors (N,E,S,W)
        # Vertical connections
        if neighbors[0]:  # North neighbor
            top_y = py - half
        if neighbors[2]:  # South neighbor
            bottom_y = py + half
            
        # Horizontal connections
        if neighbors[1]:  # East neighbor
            right_x = px + half
        if neighbors[3]:  # West neighbor
            left_x = px - half

        pygame.draw.line(screen, self.color.rgb, (center_x - 1, top_y), (center_x - 1, bottom_y), 2)
        pygame.draw.line(screen, self.color.rgb, (left_x, center_y - 1), (right_x, center_y - 1), 2)