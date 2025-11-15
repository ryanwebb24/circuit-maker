#!/usr/bin/env python3
"""Test proper connectivity for adjacent components."""

import pygame
from ui.event_handler import EventHandler, Tool
from core.circuit import Circuit

def test_adjacent_connectivity():
    print("🔧 TESTING ADJACENT COMPONENT CONNECTIVITY")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create circuit and event handler
    circuit = Circuit()
    handler = EventHandler(circuit)
    
    print("Scenario: Components placed next to each other should be electrically connected")
    print()
    
    # Test 1: Power supply next to resistor
    print("Test 1: PowerSupply at (2,2), Resistor at (3,2)")
    print("Expected: PowerSupply right terminal = Resistor left terminal")
    print()
    
    handler._handle_component_placement(2, 2, Tool.POWER_SUPPLY)
    handler._handle_component_placement(3, 2, Tool.RESISTOR)
    
    power = circuit.components[(2, 2)]
    resistor = circuit.components[(3, 2)]
    
    print(f"PowerSupply nodes: {power.nodes}")
    print(f"Resistor nodes: {resistor.nodes}")
    print()
    
    # Check if they're connected
    power_right = power.nodes[0]  # Assuming first node is positive terminal
    resistor_left = resistor.nodes[0]  # Assuming first node is left terminal
    
    if power_right == resistor_left:
        print("✅ SUCCESS: Components are electrically connected!")
    else:
        print("❌ FAIL: Components are NOT connected")
        print(f"   PowerSupply right terminal: node {power_right}")
        print(f"   Resistor left terminal: node {resistor_left}")
    
    print("\nNode mapping:")
    for pos, node in sorted(handler.node_map.items()):
        print(f"   Position {pos} -> Node {node}")
    
    pygame.quit()

if __name__ == "__main__":
    test_adjacent_connectivity()