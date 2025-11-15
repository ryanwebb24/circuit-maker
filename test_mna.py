#!/usr/bin/env python3
"""
Test script for the Modified Nodal Analysis implementation.
Tests various circuit configurations to ensure the MNA solver works correctly.
"""

try:
    import numpy as np
except ImportError:
    print("NumPy is required for this test. Please install it with: pip install numpy")
    exit(1)

from core.solver import CircuitSolver
from components.resistor import Resistor
from components.power_supply import PowerSupply
from components.ground import Ground
from components.wire import Wire
from components.enums import Orientation

def test_simple_resistor_circuit():
    """Test a simple circuit with voltage source and resistor."""
    print("\n" + "="*60)
    print("TEST 1: Simple Voltage Divider Circuit")
    print("Voltage Source (5V) - Resistor (1000) - Ground")
    print("Expected: Node 1 = 5V, Node 0 = 0V, Current = 5mA")
    print("="*60)
    
    # Create components
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=5.0)
    r1 = Resistor("R1", n1=1, n2=0, resistance=1000.0)
    gnd = Ground("GND", n1=0)
    
    # Create solver and solve
    solver = CircuitSolver()
    components = [vs, r1, gnd]
    
    try:
        voltages = solver.solve(components)
        currents = solver.calculate_currents(voltages)
        
        print(f"Node voltages: {voltages}")
        print(f"Component currents: {currents}")
        
        # Check results
        assert abs(voltages[1] - 5.0) < 0.01, f"Node 1 should be 5V, got {voltages[1]}V"
        assert abs(voltages[0] - 0.0) < 0.01, f"Node 0 should be 0V, got {voltages[0]}V"
        
        expected_current = 5.0 / 1000.0  # I = V/R = 5V/1000Ω = 5mA
        assert abs(currents['R1'] - expected_current) < 0.001, f"Current should be {expected_current}A, got {currents['R1']}A"
        
        print("Test 1 PASSED")
        return True
        
    except Exception as e:
        print(f"Test 1 FAILED: {e}")
        return False

def test_voltage_divider():
    """Test a voltage divider circuit."""
    print("\n" + "="*60)
    print("TEST 2: Voltage Divider Circuit")
    print("VS(10V) - R1(1k) - Node2 - R2(2k) - Ground")
    print("Expected: Node 1 = 10V, Node 2 = 6.67V, Node 0 = 0V")
    print("="*60)
    
    # Create components
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=10.0)
    r1 = Resistor("R1", n1=1, n2=2, resistance=1000.0)
    r2 = Resistor("R2", n1=2, n2=0, resistance=2000.0)
    gnd = Ground("GND", n1=0)
    
    # Create solver and solve
    solver = CircuitSolver()
    components = [vs, r1, r2, gnd]
    
    try:
        voltages = solver.solve(components)
        currents = solver.calculate_currents(voltages)
        
        print(f"Node voltages: {voltages}")
        print(f"Component currents: {currents}")
        
        # Check results - voltage divider formula: V2 = VS * R2/(R1+R2)
        expected_v2 = 10.0 * 2000.0 / (1000.0 + 2000.0)  # = 6.67V
        expected_current = 10.0 / (1000.0 + 2000.0)  # = 3.33mA
        
        assert abs(voltages[1] - 10.0) < 0.01, f"Node 1 should be 10V, got {voltages[1]}V"
        assert abs(voltages[2] - expected_v2) < 0.01, f"Node 2 should be {expected_v2}V, got {voltages[2]}V"
        assert abs(voltages[0] - 0.0) < 0.01, f"Node 0 should be 0V, got {voltages[0]}V"
        
        print("Test 2 PASSED")
        return True
        
    except Exception as e:
        print(f"Test 2 FAILED: {e}")
        return False

def test_parallel_resistors():
    """Test parallel resistors circuit."""
    print("\n" + "="*60)
    print("TEST 3: Parallel Resistors Circuit") 
    print("VS(12V) - Node1 - [R1(100) || R2(200)] - Ground")
    print("Expected: Node 1 = 12V, Total current = 0.18A")
    print("="*60)
    
    # Create components
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=12.0)
    r1 = Resistor("R1", n1=1, n2=0, resistance=100.0)
    r2 = Resistor("R2", n1=1, n2=0, resistance=200.0)
    gnd = Ground("GND", n1=0)
    
    # Create solver and solve
    solver = CircuitSolver()
    components = [vs, r1, r2, gnd]
    
    try:
        voltages = solver.solve(components)
        currents = solver.calculate_currents(voltages)
        
        print(f"Node voltages: {voltages}")
        print(f"Component currents: {currents}")
        
        # Check results - parallel resistance: 1/Rtotal = 1/R1 + 1/R2
        r_total = 1.0 / (1.0/100.0 + 1.0/200.0)  # = 66.67Ω
        expected_current_total = 12.0 / r_total  # ≈ 0.18A
        actual_current_total = currents['R1'] + currents['R2']
        
        assert abs(voltages[1] - 12.0) < 0.01, f"Node 1 should be 12V, got {voltages[1]}V"
        assert abs(actual_current_total - expected_current_total) < 0.001, f"Total current should be {expected_current_total}A, got {actual_current_total}A"
        
        print("Test 3 PASSED")
        return True
        
    except Exception as e:
        print(f"Test 3 FAILED: {e}")
        return False

def test_wire_connection():
    """Test circuit with wire connections."""
    print("\n" + "="*60)
    print("TEST 4: Wire Connection Circuit")
    print("VS(5V) - Wire - R1(500) - Ground")
    print("Expected: Both ends of wire at same potential")
    print("="*60)
    
    # Create components
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=5.0)
    wire = Wire("W1", n1=1, n2=2)
    r1 = Resistor("R1", n1=2, n2=0, resistance=500.0)
    gnd = Ground("GND", n1=0)
    
    # Create solver and solve
    solver = CircuitSolver()
    components = [vs, wire, r1, gnd]
    
    try:
        voltages = solver.solve(components)
        currents = solver.calculate_currents(voltages)
        
        print(f"Node voltages: {voltages}")
        print(f"Component currents: {currents}")
        
        # Check results - wire should make nodes 1 and 2 essentially the same voltage
        assert abs(voltages[1] - voltages[2]) < 0.001, f"Wire nodes should be at same potential: {voltages[1]}V vs {voltages[2]}V"
        assert abs(voltages[1] - 5.0) < 0.01, f"Node 1 should be 5V, got {voltages[1]}V"
        
        print("Test 4 PASSED")
        return True
        
    except Exception as e:
        print(f"Test 4 FAILED: {e}")
        return False

def run_all_tests():
    """Run all MNA tests and report results."""
    print("\nMODIFIED NODAL ANALYSIS TESTING SUITE")
    print("Testing circuit solver implementation...")
    
    tests = [
        test_simple_resistor_circuit,
        test_voltage_divider,
        test_parallel_resistors,
        test_wire_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("All tests PASSED! MNA implementation is working correctly.")
    else:
        print(f"{total - passed} test(s) FAILED. Check the implementation.")
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()