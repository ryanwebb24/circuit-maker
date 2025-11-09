
import pygame
import math
from ui.button import Button
from ui.config import Colors, WindowConfig, ButtonConfig, Tool
from ui.grid_renderer import GridRenderer
from ui.component_renderer import ComponentRenderer
from ui.event_handler import EventHandler
from components.resistor import Resistor
from components.enums import Orientation, ComponentColors
from core.solver import CircuitSolver
from ui.circuit_visualizer import CircuitVisualizer

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
        self.circuit_visualizer = CircuitVisualizer(self.screen, self.grid_renderer)
        self.circuit_solver = CircuitSolver()

        # Circuit analysis results
        self.node_voltages = {}
        self.component_currents = {}

        self.tool_buttons = []
        
        self.border = WindowConfig.BORDER
        
        # Initialize UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize UI elements like buttons."""
        btn_w, btn_h = ButtonConfig.WIDTH, ButtonConfig.HEIGHT
        padding = ButtonConfig.PADDING
        spacing = ButtonConfig.SPACING
        
        # Create wire button (top button)
        btn_x = int(round(padding))
        btn_y = int(round(padding))

        
        # Add ui buttons
        for tool in Tool:
            # Create lambda with tool parameter bound at creation time
            onclick = lambda t=tool: self._on_add_component(t)
            self.tool_buttons.append(Button(
                (btn_x, btn_y, btn_w, btn_h),
                tool.name,
                " ".join(word.capitalize() for word in tool.name.split("_")),
                on_click=onclick,
                selected=tool.value == "WIRE"  # Wire is the default tool
            ))
            btn_x += btn_w + spacing
        
        # Update button states to match default tool
        self._update_tool_buttons()

    def _handle_ui_events(self, event):
        """Handle UI-related events."""
        try:
            for button in self.tool_buttons:
                button.handle_event(event)

        except Exception as e:
            print(f"Error handling UI event: {e}")

    def _update_tool_buttons(self):
        """Update button states to match current tool."""
        current_tool = self.event_handler.current_tool
        print(current_tool)
        for button in self.tool_buttons:
            button.set_selected(current_tool.name == button.button_id)


    def _on_add_component(self, tool:Tool = Tool.WIRE):
        """Callback when a component button is clicked"""
        self.event_handler.set_current_tool(tool)
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

            for button in self.tool_buttons:
                button.update(mouse_pos)
                button.draw(self.screen)

        except Exception as e:
            print(f"Error updating UI: {e}")

    def solve_circuit(self):
        """Solve the circuit and update visualization values."""
        try:
            # Get list of components
            components = list(self.circuit.components.values())
            if not components:
                self.node_voltages = {}
                self.component_currents = {}
                return

            # Solve the circuit
            self.node_voltages = self.circuit_solver.solve(components)
            self.component_currents = self.circuit_solver.calculate_currents(self.node_voltages)
            
            # Update visualizer
            self.circuit_visualizer.set_values(self.node_voltages, self.component_currents)
            
            print("Node voltages:", self.node_voltages)
            print("Component currents:", self.component_currents)
            
        except ValueError as e:
            import traceback
            print(f"Circuit solving error: {e}")
            traceback.print_exc()
            self.node_voltages = {}
            self.component_currents = {}

    def update(self):
        """Update and render the game state."""
        # Maintain frame rate
        self.clock.tick(self.fps)
        
        # Clear screen
        self.screen.fill(Colors.WHITE)
        
        # Draw circuit elements
        self.grid_renderer.draw()
        self.component_renderer.draw()
        
        # Solve and visualize circuit
        self.solve_circuit()
        
        # Update hover state for visualization
        mouse_pos = pygame.mouse.get_pos()
        components = list(self.circuit.components.values())
        self.circuit_visualizer.update_hover(mouse_pos, components)
        self.circuit_visualizer.draw(components)
        
        # Update UI
        self._update_ui()
        
        # Refresh display
        pygame.display.flip()
        
        # Process events
        self.handle_events()
