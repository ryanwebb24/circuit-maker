#!/usr/bin/env python3
"""Test a complete circuit with proper return path to ground."""

import pygame
from ui.event_handler import EventHandler, Tool
from core.circuit import Circuit

def test_complete_circuit():
    print("🔧 TESTING COMPLETE CIRCUIT")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create circuit and event handler  
    circuit = Circuit()
    handler = EventHandler(circuit)
    
    print("Creating complete circuit: Ground - PowerSupply - Resistor - Wire - Ground")
    print("Layout:")
    print("   (1,2)     (2,2)        (3,2)     (4,2)     (5,2)     (6,2)")  
    print("   Ground -> PowerSupply -> Resistor -> Wire -> Ground")
    print()
    
    # Place components to create a complete loop
    handler._handle_component_placement(1, 2, Tool.GROUND)       # Ground at (1,2)
    handler._handle_component_placement(2, 2, Tool.POWER_SUPPLY) # PowerSupply at (2,2)  
    handler._handle_component_placement(3, 2, Tool.RESISTOR)     # Resistor at (3,2)
    handler._handle_component_placement(4, 2, Tool.WIRE)         # Wire at (4,2) 
    handler._handle_component_placement(5, 2, Tool.GROUND)       # Another Ground at (5,2)
    
    print("Component placement:")
    for pos, comp in circuit.components.items():
        print(f"   {type(comp).__name__} at {pos}: nodes {comp.nodes}")
    
    print(f"\\nNode mapping:")
    for pos, node in sorted(handler.node_map.items()):
        print(f"   Position {pos} -> Node {node}")
    
    # Test connectivity  
    print(f"\\n🔍 Testing connectivity:")
    ground1 = circuit.components[(1, 2)]
    power = circuit.components[(2, 2)] 
    resistor = circuit.components[(3, 2)]
    wire = circuit.components[(4, 2)]
    ground2 = circuit.components[(5, 2)]
    
    print(f"   Ground1 node: {ground1.nodes[0]}")
    print(f"   PowerSupply nodes: {power.nodes} (positive={power.nodes[0]}, negative={power.nodes[1]})")
    print(f"   Resistor nodes: {resistor.nodes}")
    print(f"   Wire nodes: {wire.nodes}")
    print(f"   Ground2 node: {ground2.nodes[0]}")
    
    # Check if it's a complete loop
    if (ground1.nodes[0] == power.nodes[1] and 
        power.nodes[0] == resistor.nodes[0] and
        resistor.nodes[1] == wire.nodes[0] and
        wire.nodes[1] == ground2.nodes[0]):
        print("\\n✅ Complete electrical loop formed!")
    else:
        print("\\n❌ Circuit is not a complete loop")
    
    # Test with solver
    print(f"\n🧮 Testing with circuit solver:")
    try:
        from core.solver import CircuitSolver
        solver = CircuitSolver()
        components = list(circuit.components.values())
        result = solver.solve(components)
        print("✅ Circuit solved successfully!")
        print("\nVoltages:")
        for node, voltage in result.items():
            print(f"   Node {node}: {voltage:.3f} V")
    except Exception as e:
        print(f"❌ Circuit solving failed: {e}")
    
    pygame.quit()

if __name__ == "__main__":
    test_complete_circuit()