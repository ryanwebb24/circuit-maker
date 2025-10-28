
import pygame
import math
from ui.button import Button
from components.resistor import Resistor
from components.enums import Orientation

class Renderer:
    def __init__(self, circuit, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Circuit Maker")
        self.clock = pygame.time.Clock()
        self.fps = 60

        self.circuit = circuit
        self.running = True
        self.current_tool = "WIRE"

        # Colors
        self.WHITE = (255, 255, 255)
        self.LIGHT_GRAY = (220, 220, 220)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)

        self.border = 100
        # UI button in the top-right white border area
        # Button size and padding
        btn_w, btn_h = 120, 32
        padding = 10
        # place button inside the top-right corner (inside the white border area)
        btn_x = int(round(self.width - padding - btn_w))
        btn_y = int(round(padding))
        self.add_button = Button((btn_x, btn_y, btn_w, btn_h), "Add R", on_click=self._on_add_resistor)

    def grid_cell_size(self):
        """Return (cell_w, cell_h) in pixels for current renderer/circuit sizes.

        Raises ValueError if circuit dimensions are invalid.
        """
        inner_w = self.width - 2 * self.border
        inner_h = self.height - 2 * self.border
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
        """Map pixel coordinates (px,py) into integer grid cell indices (gx,gy).

        Returns None if the pixel is outside the inner grid area.
        """
        cell_w, cell_h = self.grid_cell_size()
        left = self.border
        top = self.border
        right = self.width - self.border
        bottom = self.height - self.border

        # Outside inner area?
        if px < left or px > right or py < top or py > bottom:
            return 0,0

        gx = int(math.floor((px - left) / cell_w))
        gy = int(math.floor((py - top) / cell_h))
        # clamp to valid indices
        gx = max(0, min(self.circuit.width - 1, gx))
        gy = max(0, min(self.circuit.height - 1, gy))
        return gx, gy


    def draw_grid(self):
        # Compute inner drawing area
        inner_w = self.width - 2 * self.border
        inner_h = self.height - 2 * self.border

        # Guard against invalid sizes
        try:
            divisions_x = float(self.circuit.width)
        except Exception:
            return
        try:
            divisions_y = float(self.circuit.height)
        except Exception:
            return

        if divisions_x <= 0 or divisions_y <= 0:
            return

        # Spacing can be fractional; compute as float so lines fit exactly into the inner area
        spacing_x = inner_w / divisions_x
        spacing_y = inner_h / divisions_y

        left = float(self.border)
        top = float(self.border)
        right = float(self.width - self.border)
        bottom = float(self.height - self.border)

        # Draw vertical lines from left to right using float steps
        i = 0
        epsilon = 1e-9
        while True:
            x = left + i * spacing_x
            if x > right + epsilon:
                break
            px = int(round(x))
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (px, int(top)), (px, int(bottom)))
            i += 1

        # Ensure the right border line is drawn exactly (avoid floating rounding gaps)
        if abs((left + (i - 1) * spacing_x) - right) > 0.5:
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (int(right), int(top)), (int(right), int(bottom)))

        # Draw horizontal lines from top to bottom using float steps
        i = 0
        while True:
            y = top + i * spacing_y
            if y > bottom + epsilon:
                break
            py = int(round(y))
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (int(left), py), (int(right), py))
            i += 1

        # Ensure the bottom border line is drawn exactly
        if abs((top + (i - 1) * spacing_y) - bottom) > 0.5:
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (int(left), int(bottom)), (int(right), int(bottom)))

    def draw_components(self):
        # Draw all component objects. components is a dict keyed by (x,y)
        # so iterate over values to get the component instances.
        cell_w = (self.width - 2 * self.border) / float(self.circuit.width)
        cell_h = (self.height - 2 * self.border) / float(self.circuit.height)

        for comp in self.circuit.components.values():
            # Use the component's own x,y as grid coordinates
            try:
                px, py = self.grid_to_pixel(comp.x, comp.y)
            except Exception:
                # If component doesn't have x/y, skip drawing
                continue
            comp.draw(self.screen, px, py, cell_w, cell_h)

    def handle_events(self):
        for event in pygame.event.get():
            # Let UI controls handle the event first
            try:
                self.add_button.handle_event(event)
            except Exception:
                pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] > self.border and event.pos[1] > self.border and self.current_tool:
                    x,y = self.pixel_to_grid(event.pos[0], event.pos[1])
                    if self.current_tool == "RESISTOR":
                        # need to add resistance slider
                        if isinstance(self.circuit.components.get((x,y)), Resistor):
                            self.circuit.remove_component(x, y)
                        else:
                            # default orientation EAST
                            self.circuit.add_component(Resistor("resistor", 0, 1, x, y, Orientation.E, 100))
                    

            if event.type == pygame.QUIT:
                self.running = False
            # TODO: Add component placement, dragging, wire drawing here

    def update(self):
        self.clock.tick(self.fps)
        self.screen.fill(self.WHITE)
        self.draw_grid()
        self.draw_components()
        # Update and draw UI buttons (mouse state / hover)
        try:
            self.add_button.update(pygame.mouse.get_pos())
            self.add_button.draw(self.screen)
        except Exception:
            pass
        pygame.display.flip()
        self.handle_events()

    def _on_add_resistor(self):
        self.current_tool = "RESISTOR"
