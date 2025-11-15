#!/usr/bin/env python3
"""
Test script to reproduce and analyze the floating nodes issue.
"""

from core.solver import CircuitSolver
from components.resistor import Resistor
from components.power_supply import PowerSupply
from components.ground import Ground
from components.wire import Wire

def test_floating_nodes():
    """Reproduce the exact floating nodes issue from the user's circuit."""
    print("Testing floating nodes issue...")
    print("=" * 60)
    
    # Recreate the exact circuit from the error
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=15.0)
    wire1 = Wire("W1", n1=3, n2=4)
    wire2 = Wire("W2", n1=5, n2=6)  
    wire3 = Wire("W3", n1=4, n2=5)
    gnd = Ground("GND", n1=7)
    
    components = [vs, wire1, wire2, wire3, gnd]
    
    print("Components:")
    for comp in components:
        print(f"  {type(comp).__name__}: {comp.nodes}")
    
    # Analyze connectivity
    print("\nConnectivity Analysis:")
    analyze_connectivity(components)
    
    # Try to solve
    solver = CircuitSolver()
    try:
        voltages = solver.solve(components)
        print("✓ Circuit solved successfully")
        print(f"Voltages: {voltages}")
    except Exception as e:
        print(f"✗ Circuit failed: {e}")

def test_fixed_circuit():
    """Test a corrected version of the circuit."""
    print("\n" + "=" * 60)
    print("Testing FIXED circuit with proper connections...")
    print("=" * 60)
    
    # Fixed circuit: VS -> Wire -> Resistor -> Ground
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=15.0)
    wire1 = Wire("W1", n1=1, n2=2)    # Connect power supply to wire network
    wire2 = Wire("W2", n1=2, n2=3)    # Continue wire network
    wire3 = Wire("W3", n1=3, n2=4)    # Continue wire network  
    resistor = Resistor("R1", n1=4, n2=0, resistance=1000.0)  # Load resistor
    gnd = Ground("GND", n1=0)         # Ground at node 0
    
    components = [vs, wire1, wire2, wire3, resistor, gnd]
    
    print("Fixed Components:")
    for comp in components:
        print(f"  {type(comp).__name__}: {comp.nodes}")
    
    # Analyze connectivity
    print("\nConnectivity Analysis:")
    analyze_connectivity(components)
    
    # Try to solve
    solver = CircuitSolver()
    try:
        voltages = solver.solve(components)
        print("✓ Circuit solved successfully")
        print(f"Voltages: {voltages}")
        
        currents = solver.calculate_currents(voltages)
        print(f"Currents: {currents}")
        
    except Exception as e:
        print(f"✗ Circuit failed: {e}")

def analyze_connectivity(components):
    """Analyze circuit connectivity to find floating nodes."""
    from collections import defaultdict, deque
    
    # Build adjacency graph
    graph = defaultdict(set)
    all_nodes = set()
    
    for comp in components:
        nodes = comp.nodes
        all_nodes.update(nodes)
        
        # Add edges for multi-terminal components
        if len(nodes) >= 2:
            n1, n2 = nodes[0], nodes[1]
            graph[n1].add(n2)
            graph[n2].add(n1)
    
    print(f"  All nodes: {sorted(all_nodes)}")
    print(f"  Connections: {dict(graph)}")
    
    # Find connected components using BFS
    visited = set()
    components_list = []
    
    for node in all_nodes:
        if node not in visited:
            # BFS to find connected component
            component = set()
            queue = deque([node])
            
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    component.add(current)
                    
                    # Add neighbors
                    for neighbor in graph[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)
            
            components_list.append(component)
    
    print(f"  Connected components: {components_list}")
    
    if len(components_list) > 1:
        print("  ⚠️  PROBLEM: Multiple isolated networks detected!")
        for i, comp in enumerate(components_list):
            print(f"    Network {i+1}: nodes {sorted(comp)}")
    else:
        print("  ✓ All nodes are connected")

if __name__ == "__main__":
    test_floating_nodes()
    test_fixed_circuit()