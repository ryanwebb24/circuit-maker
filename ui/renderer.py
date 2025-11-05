
import pygame
import math
from ui.button import Button
from ui.config import Colors, WindowConfig, ButtonConfig, Tool
from ui.grid_renderer import GridRenderer
from ui.component_renderer import ComponentRenderer
from ui.event_handler import EventHandler
from components.resistor import Resistor
from components.enums import Orientation, ComponentColors

class Renderer:
    def __init__(self, circuit, width=WindowConfig.DEFAULT_WIDTH, height=WindowConfig.DEFAULT_HEIGHT):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(WindowConfig.CAPTION)
        self.clock = pygame.time.Clock()
        self.fps = WindowConfig.FPS
        
        self.circuit = circuit
        self.running = True
        
        # Initialize event handler
        self.event_handler = EventHandler(circuit)
        self.event_handler.on_quit = self._on_quit
        
        # Initialize renderers
        self.grid_renderer = GridRenderer(self.screen, circuit)
        self.component_renderer = ComponentRenderer(self.screen, circuit, self.grid_renderer)
        
        self.border = WindowConfig.BORDER
        
        # Initialize UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize UI elements like buttons."""
        btn_w, btn_h = ButtonConfig.WIDTH, ButtonConfig.HEIGHT
        padding = ButtonConfig.PADDING
        spacing = ButtonConfig.SPACING
        
        # Create wire button (top button)
        btn_x = int(round(self.width - padding - btn_w))
        btn_y = int(round(padding))
        self.wire_button = Button(
            (btn_x, btn_y, btn_w, btn_h),
            "Wire",
            on_click=self._on_add_wire,
            selected=True  # Wire is the default tool
        )
        
        # Create resistor button (below wire button)
        btn_y += btn_h + spacing
        self.resistor_button = Button(
            (btn_x, btn_y, btn_w, btn_h),
            "Resistor",
            on_click=self._on_add_resistor
        )
        
        # Update button states to match default tool
        self._update_tool_buttons()

    def _handle_ui_events(self, event):
        """Handle UI-related events."""
        try:
            self.wire_button.handle_event(event)
            self.resistor_button.handle_event(event)
        except Exception as e:
            print(f"Error handling UI event: {e}")

    def _update_tool_buttons(self):
        """Update button states to match current tool."""
        current_tool = self.event_handler.current_tool
        self.wire_button.set_selected(current_tool == Tool.WIRE)
        self.resistor_button.set_selected(current_tool == Tool.RESISTOR)

    def _on_add_wire(self):
        """Callback when the wire button is clicked."""
        self.event_handler.set_current_tool(Tool.WIRE)
        self._update_tool_buttons()

    def _on_add_resistor(self):
        """Callback when the resistor button is clicked."""
        self.event_handler.set_current_tool(Tool.RESISTOR)
        self._update_tool_buttons()

    def _on_quit(self):
        """Handle quit event."""
        self.running = False

    def handle_events(self):
        """Process all pending events."""
        for event in pygame.event.get():
            # Handle UI events first
            self._handle_ui_events(event)

            # Get grid coordinates if it's a mouse event
            grid_coords = None
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if event.pos[0] > self.border and event.pos[1] > self.border:
                    grid_coords = self.grid_renderer.pixel_to_grid(event.pos[0], event.pos[1])

            # Let event handler process the event
            self.event_handler.handle_event(event, grid_coords)

    def _update_ui(self):
        """Update and draw UI elements."""
        try:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update and draw wire button
            self.wire_button.update(mouse_pos)
            self.wire_button.draw(self.screen)
            
            # Update and draw resistor button
            self.resistor_button.update(mouse_pos)
            self.resistor_button.draw(self.screen)
        except Exception as e:
            print(f"Error updating UI: {e}")

    def update(self):
        """Update and render the game state."""
        # Maintain frame rate
        self.clock.tick(self.fps)
        
        # Clear screen
        self.screen.fill(Colors.WHITE)
        
        # Draw circuit elements
        self.grid_renderer.draw()
        self.component_renderer.draw()
        
        # Update UI
        self._update_ui()
        
        # Refresh display
        pygame.display.flip()
        
        # Process events
        self.handle_events()
