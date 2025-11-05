import pygame

from components.base_component import Component
from components.enums import ComponentColors, Orientation

class Wire(Component):
    def __init__(self, name:str = "wire", n1:int = 0, n2:int = 0, x:int = 0, y:int = 0, orientation:Orientation = Orientation.E, color:ComponentColors = ComponentColors.RED):
        super().__init__(name, [n1, n2], x, y)
        self.orientation = orientation
        self.color = color

    def stamp(self, G, I):
        # Electrical stamping not implemented yet
        pass

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        """
        Draw the wire centered at pixel (px, py). The provided cell_w/cell_h
        describe the pixel size of a single grid cell so the resistor sizes itself
        appropriately without needing the renderer's grid math.
        """
        if screen is None:
            return

        # Wire visual size: fit inside one cell but leave some padding
        body_w = min(cell_w, cell_h) * 0.7
        half = body_w / 2.0

        ori = 'h'
        if (self.orientation == Orientation.E or self.orientation == Orientation.W):
            ori = 'h'
        else:
            ori = 'v'

        if ori in ('v', 'vertical'):
            top_y = py - half
            bottom_y = py + half

            cx_px = int(round(px))

            # Draw line
            pygame.draw.line(screen, self.color.rgb, (cx_px, top_y), (cx_px, bottom_y), 2)
        else:
            left_x = px - half
            right_x = px + half

            cy_px = int(round(py))

            # Draw line
            pygame.draw.line(screen, self.color.rgb, (left_x, cy_px), (right_x, cy_px), 2)