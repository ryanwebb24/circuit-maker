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
        """Initialize the event handler.
        
        Args:
            circuit: The circuit being edited
        """
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
        """Change the current tool."""
        self.current_tool = tool
    
    def handle_event(self, event: pygame.event.Event, grid_coords: Optional[tuple] = None) -> bool:
        """Handle a pygame event.
        
        Args:
            event: The pygame event to handle
            grid_coords: Optional tuple of (x, y) grid coordinates for the event
            
        Returns:
            True if the event was handled, False otherwise
        """
        handler = self.handlers.get(event.type)
        if handler:
            return handler(event, grid_coords)
        return False
    
    def _handle_mouse_down(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        """Handle mouse button down events."""
        if event.button != pygame.BUTTON_LEFT or not grid_coords:
            return False
            
        x, y = grid_coords
        self.dragging = True
        self.drag_start = (x, y)
        
        return self._handle_component_placement(x, y, self.current_tool)
    
    def _handle_mouse_up(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        """Handle mouse button up events."""
        if event.button != pygame.BUTTON_LEFT:
            return False
            
        self.dragging = False
        self.drag_start = None
        return True
    
    def _handle_mouse_motion(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        """Handle mouse motion events."""
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
        """Handle quit events."""
        if self.on_quit:
            self.on_quit()
        return True
    
    # def _handle_resistor_placement(self, x: int, y: int) -> bool:
    #     """Handle placing or removing a resistor."""
    #     if isinstance(self.circuit.components.get((x,y)), Resistor):
    #         self.circuit.remove_component(x, y)
    #     else:
    #         self.circuit.add_component(
    #             Resistor(
    #                 name="R1",  # TODO: Generate unique names
    #                 n1=0,
    #                 n2=1,
    #                 x=x,
    #                 y=y,
    #                 orientation=Orientation.E,
    #                 color=ComponentColors.RED,
    #                 resistance=100.0
    #             )
    #         )
    #     return True

    def _update_adjacent_wires(self, x: int, y: int):
        """Update the adjacent components property of all neighboring wires."""
        # Check all adjacent positions (N, E, S, W)
        positions = [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]
        
        # Update each neighboring wire's adjacent_components
        for nx, ny in positions:
            neighbor = self.circuit.components.get((nx, ny))
            if isinstance(neighbor, Wire):
                neighbor.adjacent_components = self.circuit.get_adjacent_components(nx, ny)

    # def _handle_wire_placement(self, x: int, y: int) -> bool:
    #     """Handle placing or removing a wire."""
    #     if isinstance(self.circuit.components.get((x,y)), Wire):
    #         self.circuit.remove_component(x, y)
    #         self._update_adjacent_wires(x, y)
    #     else:
    #         # Create and place the new wire
    #         wire = Wire(
    #                 name="W1",  # TODO: Generate unique names
    #                 n1=0,
    #                 n2=1,
    #                 x=x,
    #                 y=y,
    #                 orientation=Orientation.E,
    #                 color=ComponentColors.RED
    #             )
    #         # Set its adjacent components
    #         wire.adjacent_components = self.circuit.get_adjacent_components(x, y)
    #         self.circuit.add_component(wire)
            
    #         # Update all neighboring wires
    #         self._update_adjacent_wires(x, y)
    #     return True
    
    # def _handle_power_supply_placement(self, x: int, y:int) -> bool:
    #     """Handle placing or removing a power supply."""
    #     if isinstance(self.circuit.components.get((x,y)), PowerSupply):
    #         self.circuit.remove_component(x, y)
    #         self._update_adjacent_wires(x, y)
    #     else:
    #         # Create and place the new wire
    #         power_supply = PowerSupply(
    #                 name="P1",  # TODO: Generate unique names
    #                 n1=0,
    #                 n2=1,
    #                 x=x,
    #                 y=y,
    #                 orientation=Orientation.E,
    #                 color=ComponentColors.RED,
    #                 voltage=15
    #             )
    #         self.circuit.add_component(power_supply)
    #         self._update_adjacent_wires(x, y)
    #     return True
    
    def _get_node_number(self, x: int, y: int) -> int:
        """Get a node number for a position, creating a new one if needed."""
        pos = (x, y)
        if pos not in self.node_map:
            self.node_map[pos] = self.next_node
            print(f"Assigning new node {self.next_node} at position {pos}")
            self.next_node += 1
        return self.node_map[pos]

    def _handle_component_placement(self, x: int, y: int, tool: Tool = Tool.WIRE) -> bool:
        """Handle placing or removing a component.
        
        Args:
            x: Grid x coordinate
            y: Grid y coordinate
            tool: The tool type being used (corresponds to component type)
            
        Returns:
            True if the component was placed/removed, False otherwise
        """
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
            
            # Assign node numbers based on position
            n1 = self._get_node_number(x, y)
            n2 = self._get_node_number(x + 1, y)  # Next node to the right
            
            # Handle special cases for different components
            if tool == Tool.POWER_SUPPLY:
                # PowerSupply: positive terminal to the right, negative to the left (adjacent position)
                n_pos = self._get_node_number(x + 1, y)  # positive terminal (right)
                n_neg = self._get_node_number(x - 1, y)  # negative terminal (left, to connect with Ground)
                params.update({"n1": n_pos, "n2": n_neg})
            elif tool == Tool.GROUND:
                # Ground connects to its own position 
                params.update({"n1": n1})
            else:
                # Other components use left and right positions
                params.update({"n1": n1, "n2": n2})
            
            # Create and configure the component
            component = component_class(**params)
            
            if isinstance(component, Wire):
                component.adjacent_components = self.circuit.get_adjacent_components(x, y)
                
            self.circuit.add_component(component)
            self._update_adjacent_wires(x, y)
            
        return True