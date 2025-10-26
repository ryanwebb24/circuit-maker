import pygame

from core.circuit import Circuit
from ui.renderer import Renderer

def main():
    circuit = Circuit()
    ui = Renderer(circuit, 1000, 800)

    while ui.running:
        ui.update()

    pygame.quit()

if __name__ == "__main__":
    main()