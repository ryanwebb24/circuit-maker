from components.base_component import Component
import pygame
from components.enums import Orientation, ComponentColors

class PowerSupply(Component):
    def __init__(self, name: str = "", n1: int = 0, n2: int = 0, x: int = 0, y: int = 0, 
                 orientation: Orientation = Orientation.E, voltage: float = 0, 
                 color: ComponentColors = ComponentColors.RED):
        """Create a voltage source (power supply).
        
        Args:
            name: Name of the component
            n1: Positive terminal node number
            n2: Negative terminal node number
            x: X coordinate on grid
            y: Y coordinate on grid
            orientation: Direction component faces (N/E/S/W)
            voltage: Voltage value in volts
            color: Color of the component when drawn
        """
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
        """
        Stamp the voltage source contribution into the circuit matrices.
        For a voltage source:
        - Add 1/-1 to the conductance matrix for voltage relationship
        - Add the voltage value to the current vector
        
        Args:
            G: Conductance matrix to stamp into
            I: Current vector to stamp into
        """
        n1, n2 = self.nodes
        
        # Add voltage source contribution
        if n1 >= 0:
            G[n1][n1] += 1
        if n2 >= 0:
            G[n2][n2] += 1
        
        # Add voltage value to current vector
        if n1 >= 0:
            I[n1] += self.voltage
        if n2 >= 0:
            I[n2] -= self.voltage

    def draw(self, screen, px: int, py: int, cell_w: float, cell_h: float):
        """
        Draw the power supply centered at pixel coordinates.
        Draws a circle with + and - symbols to indicate polarity.
        
        Args:
            screen: Pygame surface to draw on
            px, py: Pixel coordinates of center
            cell_w, cell_h: Width and height of a grid cell
        """
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