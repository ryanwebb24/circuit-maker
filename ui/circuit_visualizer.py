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
        """Draw comprehensive component information for the hovered component."""
        if not self.hovered_component:
            return
            
        component = self.hovered_component
        
        # Get grid position of component
        px, py = self.grid_renderer.grid_to_pixel(component.x, component.y)
        
        # Collect all information to display
        info_lines = []
        
        # Component name and type
        info_lines.append(f"{component.name} ({type(component).__name__})")
        
        # Node voltages
        for i, node in enumerate(component.nodes):
            if node in self.voltage_values:
                voltage = self.voltage_values[node]
                terminal_name = self._get_terminal_name(component, i)
                info_lines.append(f"{terminal_name}: {voltage:.3f}V")
        
        # Current through component
        if component.name in self.current_values:
            current = self.current_values[component.name]
            current_ma = current * 1000  # Convert to mA
            if abs(current_ma) >= 1:
                info_lines.append(f"Current: {current_ma:.2f}mA")
            else:
                info_lines.append(f"Current: {current*1000000:.2f}µA")
        
        # Component-specific information
        component_info = self._get_component_specific_info(component)
        info_lines.extend(component_info)
        
        # Calculate power if we have voltage and current
        if hasattr(component, 'nodes') and len(component.nodes) >= 2 and component.name in self.current_values:
            power = self._calculate_power(component)
            if power is not None:
                if abs(power) >= 0.001:  # >= 1mW
                    info_lines.append(f"Power: {power*1000:.2f}mW")
                else:
                    info_lines.append(f"Power: {power*1000000:.2f}µW")
        
        # Draw the information box
        self._draw_info_box(info_lines, px, py)
    
    def _get_terminal_name(self, component, terminal_index: int) -> str:
        """Get a descriptive name for the component terminal."""
        from components.power_supply import PowerSupply
        from components.ground import Ground
        from components.resistor import Resistor
        from components.wire import Wire
        
        if isinstance(component, PowerSupply):
            return "Positive" if terminal_index == 0 else "Negative"
        elif isinstance(component, Ground):
            return "Ground"
        elif isinstance(component, Resistor):
            return "Left" if terminal_index == 0 else "Right"
        elif isinstance(component, Wire):
            return "Terminal A" if terminal_index == 0 else "Terminal B"
        else:
            return f"Terminal {terminal_index + 1}"
    
    def _get_component_specific_info(self, component) -> list[str]:
        """Get component-specific information to display."""
        from components.power_supply import PowerSupply
        from components.resistor import Resistor
        
        info = []
        
        if isinstance(component, PowerSupply):
            info.append(f"Voltage Source: {component.voltage}V")
            
        elif isinstance(component, Resistor):
            info.append(f"Resistance: {component.resistance}Ω")
            
            # Calculate voltage drop across resistor
            if len(component.nodes) >= 2:
                v1 = self.voltage_values.get(component.nodes[0], 0)
                v2 = self.voltage_values.get(component.nodes[1], 0)
                voltage_drop = abs(v1 - v2)
                info.append(f"Voltage Drop: {voltage_drop:.3f}V")
        
        return info
    
    def _calculate_power(self, component) -> float | None:
        """Calculate power dissipated/supplied by the component."""
        if component.name not in self.current_values:
            return None
            
        current = self.current_values[component.name]
        
        from components.power_supply import PowerSupply
        from components.resistor import Resistor
        
        if isinstance(component, PowerSupply):
            # Power supplied by voltage source: P = V * I
            return component.voltage * current
            
        elif isinstance(component, Resistor):
            # Power dissipated by resistor: P = I^2 * R
            return current * current * component.resistance
            
        elif len(component.nodes) >= 2:
            # General case: P = V * I (voltage difference times current)
            v1 = self.voltage_values.get(component.nodes[0], 0)
            v2 = self.voltage_values.get(component.nodes[1], 0)
            voltage_diff = v1 - v2
            return voltage_diff * current
            
        return None
    
    def _draw_info_box(self, info_lines: list[str], px: float, py: float):
        """Draw an information box with the given lines of text."""
        if not info_lines:
            return
            
        # Calculate box dimensions
        line_height = 18
        padding = 6
        max_width = 0
        
        # Render all text to find maximum width
        rendered_lines = []
        for line in info_lines:
            text_surface = self.font.render(line, True, Colors.BLACK)
            rendered_lines.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
        
        # Box dimensions
        box_width = max_width + 2 * padding
        box_height = len(info_lines) * line_height + 2 * padding
        
        # Position box above component, but keep it on screen
        box_x = px - box_width // 2
        box_y = py - box_height - 20  # 20 pixels above component
        
        # Keep box within screen bounds
        screen_rect = self.screen.get_rect()
        if box_x < 0:
            box_x = 0
        elif box_x + box_width > screen_rect.width:
            box_x = screen_rect.width - box_width
            
        if box_y < 0:
            box_y = py + 20  # Move below component if no room above
        
        # Draw background box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, Colors.WHITE, box_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, box_rect, 2)
        
        # Draw text lines
        text_y = box_y + padding
        for text_surface in rendered_lines:
            text_x = box_x + padding
            self.screen.blit(text_surface, (text_x, text_y))
            text_y += line_height
                
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