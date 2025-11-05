import pygame
import math
from .config import Colors, WindowConfig

class GridRenderer:
    def __init__(self, screen, circuit):
        self.screen = screen
        self.circuit = circuit
        self.border = WindowConfig.BORDER

    def grid_cell_size(self):
        """Return (cell_w, cell_h) in pixels for current renderer/circuit sizes."""
        inner_w = self.screen.get_width() - 2 * self.border
        inner_h = self.screen.get_height() - 2 * self.border
        
        if not hasattr(self.circuit, 'width') or not hasattr(self.circuit, 'height'):
            raise ValueError("Circuit dimensions unavailable")
        if self.circuit.width <= 0 or self.circuit.height <= 0:
            raise ValueError("Circuit grid dimensions must be > 0")
            
        cell_w = inner_w / float(self.circuit.width)
        cell_h = inner_h / float(self.circuit.height)
        return cell_w, cell_h

    def grid_to_pixel(self, x, y):
        """Return pixel center for grid cell (x,y)"""
        cell_w, cell_h = self.grid_cell_size()
        px = self.border + (x + 0.5) * cell_w
        py = self.border + (y + 0.5) * cell_h
        return px, py

    def pixel_to_grid(self, px, py):
        """Map pixel coordinates (px,py) into integer grid cell indices (gx,gy)."""
        cell_w, cell_h = self.grid_cell_size()
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        
        # Check boundaries
        if (px < self.border or px > screen_w - self.border or 
            py < self.border or py > screen_h - self.border):
            return 0, 0

        gx = int(math.floor((px - self.border) / cell_w))
        gy = int(math.floor((py - self.border) / cell_h))
        
        # Clamp to valid indices
        gx = max(0, min(self.circuit.width - 1, gx))
        gy = max(0, min(self.circuit.height - 1, gy))
        return gx, gy

    def draw(self):
        """Draw the grid lines."""
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        inner_w = screen_w - 2 * self.border
        inner_h = screen_h - 2 * self.border

        try:
            divisions_x = float(self.circuit.width)
            divisions_y = float(self.circuit.height)
            if divisions_x <= 0 or divisions_y <= 0:
                return
        except (AttributeError, ValueError):
            return

        spacing_x = inner_w / divisions_x
        spacing_y = inner_h / divisions_y

        left = float(self.border)
        top = float(self.border)
        right = float(screen_w - self.border)
        bottom = float(screen_h - self.border)

        # Draw vertical lines
        for i in range(int(divisions_x) + 1):
            x = left + i * spacing_x
            if x > right:
                break
            px = int(round(x))
            pygame.draw.line(self.screen, Colors.LIGHT_GRAY, 
                           (px, int(top)), (px, int(bottom)))

        # Draw horizontal lines
        for i in range(int(divisions_y) + 1):
            y = top + i * spacing_y
            if y > bottom:
                break
            py = int(round(y))
            pygame.draw.line(self.screen, Colors.LIGHT_GRAY,
                           (int(left), py), (int(right), py))