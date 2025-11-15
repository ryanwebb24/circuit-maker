#!/usr/bin/env python3
"""Test simpler circuit: just Ground + PowerSupply + Resistor + Ground (no wire)."""

import pygame
from ui.event_handler import EventHandler, Tool
from core.circuit import Circuit

def test_simple_complete_circuit():
    print("🔧 TESTING SIMPLE COMPLETE CIRCUIT")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create circuit and event handler  
    circuit = Circuit()
    handler = EventHandler(circuit)
    
    print("Creating simple complete circuit: Ground - PowerSupply - Resistor - Ground")
    print("Layout:")
    print("   (1,2)     (2,2)        (3,2)     (4,2)")  
    print("   Ground -> PowerSupply -> Resistor -> Ground")
    print()
    
    # Place components to create a complete loop
    handler._handle_component_placement(1, 2, Tool.GROUND)       # Ground at (1,2)
    handler._handle_component_placement(2, 2, Tool.POWER_SUPPLY) # PowerSupply at (2,2)  
    handler._handle_component_placement(3, 2, Tool.RESISTOR)     # Resistor at (3,2)
    handler._handle_component_placement(4, 2, Tool.GROUND)       # Another Ground at (4,2)
    
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
    ground2 = circuit.components[(4, 2)]
    
    print(f"   Ground1 node: {ground1.nodes[0]}")
    print(f"   PowerSupply nodes: {power.nodes} (positive={power.nodes[0]}, negative={power.nodes[1]})")
    print(f"   Resistor nodes: {resistor.nodes}")
    print(f"   Ground2 node: {ground2.nodes[0]}")
    
    # Expected connectivity:
    # Ground1(2) - PowerSupply(3,2) - Resistor(3,4) - Ground2(4)
    # For complete loop: Ground2 should connect to node 4 (same as Resistor right terminal)
    if (ground1.nodes[0] == power.nodes[1] and 
        power.nodes[0] == resistor.nodes[0] and
        resistor.nodes[1] == ground2.nodes[0]):
        print("\\n✅ Complete electrical loop formed!")
    else:
        print("\\n❌ Circuit is not a complete loop")
        print(f"   Expected: G1({ground1.nodes[0]}) = PS_neg({power.nodes[1]}) ✅")
        print(f"   Expected: PS_pos({power.nodes[0]}) = R_left({resistor.nodes[0]}) {'✅' if power.nodes[0] == resistor.nodes[0] else '❌'}")
        print(f"   Expected: R_right({resistor.nodes[1]}) = G2({ground2.nodes[0]}) {'✅' if resistor.nodes[1] == ground2.nodes[0] else '❌'}")
    
    # Test with solver
    print(f"\\n🧮 Testing with circuit solver:")
    try:
        from core.solver import CircuitSolver
        solver = CircuitSolver()
        components = list(circuit.components.values())
        result = solver.solve(components)
        print("✅ Circuit solved successfully!")
        print("\\nVoltages:")
        for node, voltage in result.items():
            print(f"   Node {node}: {voltage:.3f} V")
    except Exception as e:
        print(f"❌ Circuit solving failed: {e}")
    
    pygame.quit()

if __name__ == "__main__":
    test_simple_complete_circuit()