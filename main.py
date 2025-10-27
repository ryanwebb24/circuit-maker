import pygame

from core.circuit import Circuit
from ui.renderer import Renderer
from components import Resistor
def main():
    circuit = Circuit(32,32)
    ui = Renderer(circuit, 800, 800)

    while ui.running:
        ui.update()

    pygame.quit()

if __name__ == "__main__":
    main()