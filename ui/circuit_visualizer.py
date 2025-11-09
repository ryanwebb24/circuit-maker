import pygame
from typing import Dict
from components.base_component import Component
from ui.config import Colors

class CircuitVisualizer:
    def __init__(self, screen, grid_renderer):
        """
        Initialize the circuit visualizer.
        
        Args:
            screen: Pygame surface to draw on
            grid_renderer: GridRenderer instance for coordinate conversion
        """
        self.screen = screen
        self.grid_renderer = grid_renderer
        self.font = pygame.font.Font(None, 24)  # Default font for labels
        self.small_font = pygame.font.Font(None, 20)  # Smaller font for values
        self.voltage_values: Dict[int, float] = {}  # Node number -> voltage
        self.current_values: Dict[str, float] = {}  # Component name -> current
        self.hovered_component = None  # Component currently being hovered over
        
    def set_values(self, voltages: Dict[int, float], currents: Dict[str, float]):
        """Set the voltage and current values to display."""
        self.voltage_values = voltages
        self.current_values = currents
        
    def update_hover(self, mouse_pos, components):
        """Update which component is being hovered over."""
        self.hovered_component = None
        if not mouse_pos:
            return
            
        # Convert mouse position to grid coordinates
        grid_x, grid_y = self.grid_renderer.pixel_to_grid(*mouse_pos)
        
        # Check if any component is at these coordinates
        for component in components:
            if component.x == grid_x and component.y == grid_y:
                self.hovered_component = component
                break
        
    def draw_voltage_labels(self, components: list[Component]):
        """Draw voltage values near the hovered component's nodes."""
        if not self.voltage_values or not self.hovered_component:
            return
            
        # Only draw voltage labels for the hovered component
        component = self.hovered_component
        
        # Get grid position of component
        px, py = self.grid_renderer.grid_to_pixel(component.x, component.y)
        
        # Draw voltage label for each node of the hovered component
        offset_y = -20  # Start above the component
        for node in component.nodes:
            if node not in self.voltage_values:
                continue
                
            voltage = self.voltage_values[node]
            label = f"Node {node}: {voltage:.2f}V"
            
            # Render voltage text
            text = self.font.render(label, True, Colors.BLACK)
            text_rect = text.get_rect()
            
            # Position the text above the component, stacked if multiple nodes
            text_rect.centerx = px
            text_rect.bottom = py + offset_y
            offset_y -= 20  # Move up for next label
            
            # Draw a white background for better visibility
            padding = 2
            background_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(self.screen, Colors.WHITE, background_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, background_rect, 1)
            
            # Draw the text
            self.screen.blit(text, text_rect)
                
    def draw_current_arrows(self, components: list[Component]):
        """Draw current arrows and values near components."""
        if not self.current_values:
            return
            
        for component in components:
            if component.name not in self.current_values:
                continue
                
            current = self.current_values[component.name]
            if abs(current) < 1e-9:  # Skip negligible currents
                continue
                
            # Get component position
            px, py = self.grid_renderer.grid_to_pixel(component.x, component.y)
            
            # Draw current value
            label = f"{current*1000:.1f}mA"  # Convert to mA for display
            text = self.small_font.render(label, True, Colors.BLACK)
            text_rect = text.get_rect()
            
            # Position based on component orientation
            if component.orientation in [0, 2]:  # Vertical
                text_rect.midleft = (px + 15, py)
                arrow_start = (px + 5, py - 10)
                arrow_end = (px + 5, py + 10)
            else:  # Horizontal
                text_rect.midtop = (px, py + 15)
                arrow_start = (px - 10, py + 5)
                arrow_end = (px + 10, py + 5)
            
            # Draw arrow background
            padding = 2
            background_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(self.screen, Colors.WHITE, background_rect)
            pygame.draw.rect(self.screen, Colors.BLACK, background_rect, 1)
            
            # Draw the text
            self.screen.blit(text, text_rect)
            
            # Draw current direction arrow
            if current > 0:
                start, end = arrow_start, arrow_end
            else:
                start, end = arrow_end, arrow_start
            
            # Draw arrow line
            pygame.draw.line(self.screen, Colors.BLACK, start, end, 2)
            
            # Draw arrow head
            if component.orientation in [0, 2]:  # Vertical
                head_left = (end[0] - 3, end[1] - 3)
                head_right = (end[0] + 3, end[1] - 3)
            else:  # Horizontal
                head_left = (end[0] - 3, end[1] - 3)
                head_right = (end[0] - 3, end[1] + 3)
            
            pygame.draw.line(self.screen, Colors.BLACK, end, head_left, 2)
            pygame.draw.line(self.screen, Colors.BLACK, end, head_right, 2)
            
    def draw(self, components: list[Component]):
        """Draw all circuit analysis visualizations."""
        self.draw_voltage_labels(components)
        self.draw_current_arrows(components)