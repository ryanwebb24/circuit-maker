import pygame
from typing import Callable, Dict, Optional
from ui.config import Tool
from components.resistor import Resistor
from components.wire import Wire
from components.enums import Orientation, ComponentColors
from core.circuit import Circuit

class EventHandler:
    def __init__(self, circuit: Circuit):
        """Initialize the event handler.
        
        Args:
            circuit: The circuit being edited
        """
        self.circuit = circuit
        self.current_tool = Tool.WIRE
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
        
        if self.current_tool == Tool.RESISTOR:
            return self._handle_resistor_placement(x, y)
        elif self.current_tool == Tool.WIRE:
            self.dragging = True
            self.drag_start = (x, y)
            return self._handle_wire_placement(x, y)
            return True
            
        return False
    
    def _handle_mouse_up(self, event: pygame.event.Event, grid_coords: Optional[tuple]) -> bool:
        """Handle mouse button up events."""
        if event.button != pygame.BUTTON_LEFT:
            return False
            
        if self.dragging and self.drag_start and grid_coords:
            end_x, end_y = grid_coords
            start_x, start_y = self.drag_start
            if self.current_tool == Tool.WIRE:
                # TODO: Add wire creation logic
                pass
            
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
    
    def _handle_resistor_placement(self, x: int, y: int) -> bool:
        """Handle placing or removing a resistor."""
        if isinstance(self.circuit.components.get((x,y)), Resistor):
            self.circuit.remove_component(x, y)
        else:
            self.circuit.add_component(
                Resistor(
                    name="R1",  # TODO: Generate unique names
                    n1=0,
                    n2=1,
                    x=x,
                    y=y,
                    orientation=Orientation.E,
                    color=ComponentColors.RED,
                    resistance=100.0
                )
            )
        return True
    
    def _handle_wire_placement(self, x: int, y: int) -> bool:
        """Handle placing or removing a resistor."""
        if isinstance(self.circuit.components.get((x,y)), Wire):
            self.circuit.remove_component(x, y)
        else:
            self.circuit.add_component(
                Wire(
                    name="W1",  # TODO: Generate unique names
                    n1=0,
                    n2=1,
                    x=x,
                    y=y,
                    orientation=Orientation.E,
                    color=ComponentColors.RED
                )
            )
        return True