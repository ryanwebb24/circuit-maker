from components.base_component import Component
import pygame
from components.enums import Orientation, ComponentColors

class Ground(Component):
    def __init__(self, name: str = "GND", n1: int = 0, x: int = 0, y: int = 0, orientation: Orientation = Orientation.S, color: ComponentColors = ComponentColors.BLUE):
        # Ground only needs one node (the one being grounded)
        super().__init__(name, [n1], x, y)
        self.color = color
        
        # Require Orientation enum (or int that maps to it)
        if isinstance(orientation, Orientation):
            self.orientation = orientation
        else:
            try:
                self.orientation = Orientation(orientation)
            except Exception:
                raise TypeError("orientation must be a components.enums.Orientation")

    def stamp(self, G, I):
        # Ground connections are handled by the MNA solver directly
        # This method exists for interface compatibility
        pass

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        if screen is None:
            return

        # Size the component to fit within a cell with padding
        size = min(cell_w, cell_h) * 0.7
        half_size = size / 2.0
        line_spacing = size / 8.0
        
        # Calculate rotation based on orientation
        rotation = {
            Orientation.N: 180,
            Orientation.E: 270,
            Orientation.S: 0,
            Orientation.W: 90
        }[self.orientation]
        
        # Define the ground symbol points relative to center
        if rotation in [0, 180]:  # Vertical orientation
            # Main vertical line
            start_main = (px, py - half_size)
            end_main = (px, py)
            
            # Three horizontal lines of decreasing width
            lines = [
                ((px - half_size, py), (px + half_size, py)),
                ((px - half_size * 0.7, py + line_spacing), 
                 (px + half_size * 0.7, py + line_spacing)),
                ((px - half_size * 0.4, py + line_spacing * 2), 
                 (px + half_size * 0.4, py + line_spacing * 2))
            ]
        else:  # Horizontal orientation
            # Main horizontal line
            start_main = (px - half_size, py)
            end_main = (px, py)
            
            # Three vertical lines of decreasing height
            lines = [
                ((px, py - half_size), (px, py + half_size)),
                ((px + line_spacing, py - half_size * 0.7),
                 (px + line_spacing, py + half_size * 0.7)),
                ((px + line_spacing * 2, py - half_size * 0.4),
                 (px + line_spacing * 2, py + half_size * 0.4))
            ]

        # Draw the lines
        pygame.draw.line(screen, self.color.value, start_main, end_main, width=2)
        for start, end in lines:
            pygame.draw.line(screen, self.color.value, start, end, width=2)