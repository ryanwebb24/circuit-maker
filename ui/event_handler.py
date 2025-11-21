import pygame
from typing import Callable, Dict, Optional
from ui.config import Tool
from components.resistor import Resistor
from components.wire import Wire
from components.power_supply import PowerSupply
from components.ground import Ground
from components.enums import Orientation, ComponentColors
from core.circuit import Circuit
from components.base_component import Component

class EventHandler:
    # Map each tool to its corresponding component class
    TOOL_TO_COMPONENT = {
        Tool.WIRE: Wire,
        Tool.RESISTOR: Resistor,
        Tool.POWER_SUPPLY: PowerSupply,
        Tool.GROUND: Ground
    }

    # Default parameters for each component type
    COMPONENT_DEFAULTS = {
        Tool.WIRE: {"name": "W1", "orientation": Orientation.E, "color": ComponentColors.RED},
        Tool.RESISTOR: {"name": "R1", "orientation": Orientation.E, "color": ComponentColors.RED, "resistance": 100.0},
        Tool.POWER_SUPPLY: {"name": "P1", "orientation": Orientation.E, "color": ComponentColors.RED, "voltage": 15},
        Tool.GROUND: {"name": "GND", "orientation": Orientation.S, "color": ComponentColors.BLUE}
    }

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.current_tool = Tool.WIRE
        self.next_node = 1  # Track the next available node number
        self.node_map = {}  # Map (x,y) coordinates to node numbers
        self.handlers: Dict[int, Callable] = {
            pygame.MOUSEBUTTONDOWN: self._handle_mouse_down,
            pygame.MOUSEBUTTONUP: self._handle_mouse_up,
            pygame.MOUSEMOTION: self._handle_mouse_motion,
            pygame.KEYDOWN: self._handle_key_down,
            pygame.QUIT: self._handle_quit
        }
        
        # Callback functions that can be set by the renderer
        self.on_quit: Optional[Callable] = None
        self.on_grid_click: Optional[Callable] = None
        self.on_component_drag: Optional[Callable] = None
        
        # State tracking
        self.dragging = False
        self.drag_start = None
        self.selected_component = None
    
    def set_current_tool(self, tool: Tool):
        self.current_tool = tool
    
    def handle_event(self, event: pygame.event.Event, grid_coords: Optional[tuple] = None) -> bool:
        handler = self.handlers.get(event.type)
        if handler:
            return handler(event, grid_coords)
        return False
    
    def _handle_mouse_down(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        if event.button != pygame.BUTTON_LEFT or not grid_coords:
            return False
            
        x, y = grid_coords
        self.dragging = True
        self.drag_start = (x, y)
        
        return self._handle_component_placement(x, y, self.current_tool)
    
    def _handle_mouse_up(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        if event.button != pygame.BUTTON_LEFT:
            return False
            
        self.dragging = False
        self.drag_start = None
        return True
    
    def _handle_mouse_motion(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        if self.dragging and self.on_component_drag and grid_coords:
            self.on_component_drag(self.drag_start, grid_coords)
            return True
        return False
    
    def _handle_key_down(self, event: pygame.event.Event, _: Optional[tuple]) -> bool:
        """Handle key press events."""
        if event.key == pygame.K_ESCAPE:
            self.current_tool = Tool.WIRE
            return True
        return False
    
    def _handle_quit(self, _: pygame.event.Event, __: Optional[tuple]) -> bool:
        if self.on_quit:
            self.on_quit()
        return True

    def _update_adjacent_wires(self, x: int, y: int):
        # Check all adjacent positions (N, E, S, W)
        positions = [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]
        
        # Update each neighboring wire's adjacent_components
        for nx, ny in positions:
            neighbor = self.circuit.components.get((nx, ny))
            if isinstance(neighbor, Wire):
                neighbor.adjacent_components = self.circuit.get_adjacent_components(nx, ny)
    
    def _get_node_number(self, x: int, y: int) -> int:
        # Don't create nodes at negative positions - return ground (0)
        if x < 0 or y < 0:
            return 0
            
        pos = (x, y)
        if pos not in self.node_map:
            self.node_map[pos] = self.next_node
            print(f"Assigning new node {self.next_node} at position {pos}")
            self.next_node += 1
        return self.node_map[pos]

    def _handle_component_placement(self, x: int, y: int, tool: Tool = Tool.WIRE) -> bool:
        # Get the component class for this tool
        component_class = self.TOOL_TO_COMPONENT.get(tool)
        if not component_class:
            return False
            
        # Check if there's already a component of this type at the location
        current_component = self.circuit.components.get((x, y))
        if isinstance(current_component, component_class):
            self.circuit.remove_component(x, y)
            self._update_adjacent_wires(x, y)
        else:
            # Get base parameters for this component type
            params = self.COMPONENT_DEFAULTS.get(tool, {}).copy()
            params.update({"x": x, "y": y})
            
            # Assign node numbers based on component terminals and adjacent positions
            if tool == Tool.POWER_SUPPLY:
                # PowerSupply: positive terminal at component position, negative at ground (node 0)
                n_pos = self._get_node_number(x, y)  # positive terminal at component position
                params.update({"n1": n_pos, "n2": 0})  # negative terminal to ground
            elif tool == Tool.GROUND:
                # Ground connects the component position to ground (node 0)
                n1 = self._get_node_number(x, y)
                params.update({"n1": n1})
            elif tool == Tool.RESISTOR:
                # Resistor connects left and right adjacent positions
                n1 = self._get_node_number(x - 1, y)  # left terminal
                n2 = self._get_node_number(x + 1, y)  # right terminal
                params.update({"n1": n1, "n2": n2})
            elif tool == Tool.WIRE:
                # Wire connects to all adjacent positions it should connect to
                # For now, connect left and right (horizontal wire)
                n1 = self._get_node_number(x - 1, y)  # left connection
                n2 = self._get_node_number(x + 1, y)  # right connection
                params.update({"n1": n1, "n2": n2})
            else:
                # Default: connect component position to right position
                n1 = self._get_node_number(x, y)
                n2 = self._get_node_number(x + 1, y)
                params.update({"n1": n1, "n2": n2})
            
            print(f"Placing {tool.name} at ({x},{y}) with nodes {params.get('n1', 'N/A')}, {params.get('n2', 'N/A')}")
            
            # Create and configure the component
            component = component_class(**params)
            
            if isinstance(component, Wire):
                component.adjacent_components = self.circuit.get_adjacent_components(x, y)
                
            self.circuit.add_component(component)
            self._update_adjacent_wires(x, y)
            
        return True