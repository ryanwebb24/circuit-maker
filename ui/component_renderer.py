class ComponentRenderer:
    def __init__(self, screen, circuit, grid_renderer):
        self.screen = screen
        self.circuit = circuit
        self.grid_renderer = grid_renderer

    def draw(self):
        cell_w, cell_h = self.grid_renderer.grid_cell_size()

        for comp in self.circuit.components.values():
            try:
                px, py = self.grid_renderer.grid_to_pixel(comp.x, comp.y)
                comp.draw(self.screen, px, py, cell_w, cell_h)
            except (AttributeError, ValueError):
                # Skip components with invalid coordinates
                continue