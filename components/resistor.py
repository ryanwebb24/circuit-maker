from components.base_component import Component
import pygame
import math


class Resistor(Component):
    def __init__(self, name: str = "", n1: int = 0, n2: int = 0, resistance: float = 0, x: int = 0, y: int = 0, orientation: str = 'h'):
        super().__init__(name, [n1, n2], x, y)
        self.resistance = resistance
        # orientation: 'h' or 'v' (or 'horizontal' / 'vertical')
        self.orientation = orientation.lower() if isinstance(orientation, str) else 'h'

    def stamp(self, G, I):
        # Electrical stamping not implemented yet
        pass

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        """
        Draw the resistor centered at pixel (px, py). The provided cell_w/cell_h
        describe the pixel size of a single grid cell so the resistor sizes itself
        appropriately without needing the renderer's grid math.
        """
        if screen is None:
            return

        # Resistor visual size: fit inside one cell but leave some padding
        body_w = min(cell_w, cell_h) * 0.7
        half = body_w / 2.0

        term_len = max(4, int(min(cell_w, cell_h) * 0.15))

        if self.orientation in ('v', 'vertical'):
            # Vertical resistor: terminals on top/bottom, zig-zag along Y
            top_y = py - half
            bottom_y = py + half

            top_term_px = int(round(top_y - term_len))
            top_body_px = int(round(top_y))
            bottom_body_px = int(round(bottom_y))
            bottom_term_px = int(round(bottom_y + term_len))
            cx_px = int(round(px))

            # Draw terminals (vertical lines)
            pygame.draw.line(screen, (0, 0, 0), (cx_px, top_term_px), (cx_px, top_body_px), 2)
            pygame.draw.line(screen, (0, 0, 0), (cx_px, bottom_body_px), (cx_px, bottom_term_px), 2)

            # Zig-zag along vertical axis: alternate x offsets
            segments = 6
            pts = []
            amp = min(cell_w, cell_h) * 0.12
            for i in range(segments + 1):
                t = i / segments
                y = top_y + t * (bottom_y - top_y)
                x = px + (amp if (i % 2 == 0) else -amp)
                pts.append((int(round(x)), int(round(y))))

            if len(pts) >= 2:
                pygame.draw.lines(screen, (0, 0, 0), False, pts, 2)
        else:
            # Horizontal (default): terminals left/right, zig-zag along X
            left_x = px - half
            right_x = px + half

            left_term_px = int(round(left_x - term_len))
            left_body_px = int(round(left_x))
            right_body_px = int(round(right_x))
            right_term_px = int(round(right_x + term_len))
            cy_px = int(round(py))

            # Draw terminals (horizontal lines)
            pygame.draw.line(screen, (0, 0, 0), (left_term_px, cy_px), (left_body_px, cy_px), 2)
            pygame.draw.line(screen, (0, 0, 0), (right_body_px, cy_px), (right_term_px, cy_px), 2)

            # Draw zig-zag resistor body
            segments = 6
            pts = []
            amp = min(cell_w, cell_h) * 0.12
            for i in range(segments + 1):
                t = i / segments
                x = left_x + t * (right_x - left_x)
                y = py + (amp if (i % 2 == 0) else -amp)
                pts.append((int(round(x)), int(round(y))))

            if len(pts) >= 2:
                pygame.draw.lines(screen, (0, 0, 0), False, pts, 2)