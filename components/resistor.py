from base_component import Component

class Resistor(Component):
    def __int__(self, name:str = "", n1:int = 0, n2:int = 0, resistance:float = 0):
        super().__init__(name, [n1, n2])
        self.resistance = resistance