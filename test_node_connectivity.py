#!/usr/bin/env python3
"""
Test script to verify that the UI properly assigns connected node numbers.
"""

from ui.event_handler import EventHandler
from core.circuit import Circuit
from ui.config import Tool

def test_node_connectivity():
    """Test that placing adjacent components creates proper electrical connections."""
    print("🔧 TESTING NODE CONNECTIVITY IN UI")
    print("=" * 50)
    
    # Create a test circuit and event handler
    circuit = Circuit(10, 10)
    handler = EventHandler(circuit)
    
    print("1. Testing horizontal component placement:")
    print("   Placing PowerSupply at (2,2), Wire at (3,2), Resistor at (4,2)")
    
    # Simulate placing components horizontally next to each other
    handler._handle_component_placement(2, 2, Tool.POWER_SUPPLY)  # PowerSupply at (2,2)
    handler._handle_component_placement(3, 2, Tool.WIRE)          # Wire at (3,2) 
    handler._handle_component_placement(4, 2, Tool.RESISTOR)      # Resistor at (4,2)
    handler._handle_component_placement(1, 2, Tool.GROUND)        # Ground at (1,2)
    
    # Check the resulting components
    print("\n📊 Resulting components:")
    for pos, component in circuit.components.items():
        comp_type = type(component).__name__
        nodes = getattr(component, 'nodes', [])
        print(f"   {comp_type} at {pos}: nodes {nodes}")
    
    # Analyze connectivity
    print("\n🔍 Connectivity Analysis:")
    analyze_node_connections(circuit)
    
    print("\n" + "=" * 50)
    print("2. Testing with circuit solver:")
    
    # Test with the actual solver
    from core.solver import CircuitSolver
    solver = CircuitSolver()
    
    try:
        components = list(circuit.components.values())
        voltages = solver.solve(components)
        currents = solver.calculate_currents(voltages)
        
        print("✅ Circuit solved successfully!")
        print("Node voltages:")
        for node, voltage in sorted(voltages.items()):
            print(f"   Node {node}: {voltage:.3f} V")
        
        print("\nComponent currents:")
        for comp_name, current in currents.items():
            if abs(current) > 1e-9:
                print(f"   {comp_name}: {current:.6f} A ({current*1000:.3f} mA)")
                
    except Exception as e:
        print(f"❌ Circuit solving failed: {e}")

def analyze_node_connections(circuit):
    """Analyze and report node connections."""
    from collections import defaultdict
    
    # Build a map of nodes to components
    node_to_components = defaultdict(list)
    
    for pos, component in circuit.components.items():
        comp_name = f"{type(component).__name__}@{pos}"
        nodes = getattr(component, 'nodes', [])
        
        for node in nodes:
            if node != 0:  # Skip ground
                node_to_components[node].append(comp_name)
    
    # Report connections
    for node, components in sorted(node_to_components.items()):
        if len(components) > 1:
            print(f"   Node {node}: {' <-> '.join(components)} ✅")
        else:
            print(f"   Node {node}: {components[0]} ⚠️ (isolated)")

if __name__ == "__main__":
    test_node_connectivity()