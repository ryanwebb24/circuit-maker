from components.base_component import Component

class Circuit:
    def __init__(self, height:int = 64, width:int = 64):
        self.height = height
        self.width = width
        self.components = {}

    def add_component(self, component:Component):
        self.components[(component.x, component.y)] = component