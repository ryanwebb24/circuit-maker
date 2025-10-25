
import pygame
# from components.resistor import Resistor
# from core.circuit import Circuit

class Renderer:
    def __init__(self, circuit, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Circuit Maker")
        self.clock = pygame.time.Clock()
        self.fps = 60

        self.circuit = circuit
        self.running = True

        # Colors
        self.WHITE = (255, 255, 255)
        self.LIGHT_GRAY = (220, 220, 220)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)

    def draw_grid(self):
        for x in range(0, self.width, self.circuit.width):
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (x,0), (x,self.height))
        for y in range(0, self.height, self.circuit.height):
            pygame.draw.line(self.screen, self.LIGHT_GRAY, (0,y), (self.width,y))

    def draw_components(self):
        for comp in self.circuit.components:
            comp.draw(self.screen, self.circuit.height, self.circuit.width)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # TODO: Add component placement, dragging, wire drawing here

    def update(self):
        self.clock.tick(self.fps)
        self.screen.fill(self.WHITE)
        self.draw_grid()
        self.draw_components()
        pygame.display.flip()
        self.handle_events()
