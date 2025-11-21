from components.base_component import Component
import pygame
from components.enums import Orientation, ComponentColors

class PowerSupply(Component):
    def __init__(self, name: str = "", n1: int = 0, n2: int = 0, x: int = 0, y: int = 0, orientation: Orientation = Orientation.E, color: ComponentColors = ComponentColors.RED, voltage: float = 0):
        super().__init__(name, [n1, n2], x, y)
        self.voltage = voltage
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
        # Voltage sources are handled by the MNA solver directly
        # This method exists for interface compatibility
        pass
            
    def calculate_current(self, v1: float, v2: float) -> float:
        # The current through a voltage source is determined by the circuit
        # and would be calculated by the solver. For now, return 0.
        # In a complete implementation, this would access the current from
        # the solved system.
        return 0.0

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        if screen is None:
            return

        # Size the component to fit within a cell with padding
        diameter = min(cell_w, cell_h) * 0.7
        radius = diameter / 2.0
        
        # Draw the circle
        pygame.draw.circle(screen, self.color.value, (px, py), radius, width=2)
        
        # Draw polarity symbols
        font = pygame.font.Font(None, int(radius))
        
        # Position symbols based on orientation
        if self.orientation in [Orientation.E, Orientation.W]:
            # Horizontal orientation
            plus_pos = (px - radius/2, py - radius/4)
            minus_pos = (px + radius/2 - radius/4, py - radius/4)
        else:
            # Vertical orientation
            plus_pos = (px - radius/4, py - radius/2)
            minus_pos = (px - radius/4, py + radius/2 - radius/4)
            
        # Render the symbols
        plus_text = font.render("+", True, self.color.value)
        minus_text = font.render("-", True, self.color.value)
        screen.blit(plus_text, plus_pos)
        screen.blit(minus_text, minus_pos)