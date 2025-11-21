from components.base_component import Component
import pygame
from components.enums import Orientation, ComponentColors


class Resistor(Component):
    def __init__(self, name: str = "", n1: int = 0, n2: int = 0, x: int = 0, y: int = 0, orientation: Orientation = Orientation.E, color:ComponentColors = ComponentColors.RED, resistance: float = 0):
        super().__init__(name, [n1, n2], x, y)
        self.resistance = resistance
        self.color = color
        # Require Orientation enum (or int that maps to it)
        if isinstance(orientation, Orientation):
            self.orientation = orientation
        else:
            try:
                # allow integer values that match the enum
                self.orientation = Orientation(orientation)
            except Exception:
                raise TypeError("orientation must be a components.enums.Orientation")

    def stamp(self, G, I):
        if self.resistance == 0:  # Handle short circuit case
            return
            
        # Get the nodes this resistor connects
        n1, n2 = self.nodes
        
        # Calculate conductance (1/R)
        g = 1.0 / self.resistance
        
        # Add conductance to diagonal elements
        if n1 >= 0:  # If node 1 is not ground
            G[n1][n1] += g
        if n2 >= 0:  # If node 2 is not ground
            G[n2][n2] += g
            
        # Add negative conductance to off-diagonal elements
        if n1 >= 0 and n2 >= 0:  # If neither node is ground
            G[n1][n2] -= g
            G[n2][n1] -= g  # Matrix must be symmetric
            
    def calculate_current(self, v1: float, v2: float) -> float:
        if self.resistance == 0:
            return 0.0  # Avoid division by zero
        return (v1 - v2) / self.resistance

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        if screen is None:
            return

        # Resistor visual size: fit inside one cell but leave some padding
        body_w = min(cell_w, cell_h) * 0.7
        half = body_w / 2.0

        term_len = max(4, int(min(cell_w, cell_h) * 0.15))

        # Determine axis (vertical vs horizontal) and phase for zig-zag
        ori = self.orientation
        is_vertical = ori in (Orientation.N, Orientation.S)
        # phase controls zig-zag direction so we can visually flip for N/S or E/W
        phase = 1
        if ori in (Orientation.S, Orientation.W):
            phase = -1

        if is_vertical:
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

            # Zig-zag along vertical axis: alternate x offsets, apply phase
            segments = 6
            pts = []
            amp = min(cell_w, cell_h) * 0.12
            for i in range(segments + 1):
                t = i / segments
                y = top_y + t * (bottom_y - top_y)
                sign = amp if (i % 2 == 0) else -amp
                x = px + phase * sign
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

            # Draw zig-zag resistor body (apply phase to vertical offsets)
            segments = 6
            pts = []
            amp = min(cell_w, cell_h) * 0.12
            for i in range(segments + 1):
                t = i / segments
                x = left_x + t * (right_x - left_x)
                sign = amp if (i % 2 == 0) else -amp
                y = py + phase * sign
                pts.append((int(round(x)), int(round(y))))

            if len(pts) >= 2:
                pygame.draw.lines(screen, (0, 0, 0), False, pts, 2)