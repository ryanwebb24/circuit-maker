#!/usr/bin/env python3
"""
Circuit validation and auto-fix utilities for the circuit maker.
Helps identify and suggest fixes for common circuit issues.
"""

from typing import List, Dict, Tuple, Set
from collections import defaultdict, deque
from components.base_component import Component
from components.wire import Wire
from components.power_supply import PowerSupply
from components.ground import Ground
from components.resistor import Resistor

class CircuitValidator:
    """Validates circuits and suggests fixes for common issues."""
    
    def __init__(self):
        self.components = []
        self.connectivity_graph = defaultdict(set)
        self.all_nodes = set()
    
    def validate_circuit(self, components: List[Component]) -> Dict[str, any]:
        """
        Validate a circuit and return analysis results.
        
        Args:
            components: List of circuit components
            
        Returns:
            Dictionary with validation results and suggestions
        """
        self.components = components
        self._build_connectivity_graph()
        
        result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'connected_components': self._find_connected_components()
        }
        
        # Check for floating nodes
        floating_issue = self._check_floating_nodes()
        if floating_issue:
            result['is_valid'] = False
            result['issues'].append(floating_issue)
            result['suggestions'].extend(self._suggest_connection_fixes())
        
        # Check for missing ground
        ground_issue = self._check_ground_connections()
        if ground_issue:
            result['warnings'].append(ground_issue)
        
        # Check for missing load
        load_issue = self._check_load_components()
        if load_issue:
            result['warnings'].append(load_issue)
            
        return result
    
    def _build_connectivity_graph(self):
        """Build adjacency graph of component connections."""
        self.connectivity_graph = defaultdict(set)
        self.all_nodes = set()
        
        for comp in self.components:
            nodes = comp.nodes
            self.all_nodes.update(nodes)
            
            # Add edges for multi-terminal components
            if len(nodes) >= 2:
                n1, n2 = nodes[0], nodes[1]
                if n1 != n2:  # Avoid self-loops
                    self.connectivity_graph[n1].add(n2)
                    self.connectivity_graph[n2].add(n1)
    
    def _find_connected_components(self) -> List[Set[int]]:
        """Find all connected components in the circuit."""
        visited = set()
        connected_components = []
        
        for node in self.all_nodes:
            if node not in visited:
                component = self._bfs_component(node, visited)
                connected_components.append(component)
        
        return connected_components
    
    def _bfs_component(self, start_node: int, visited: set) -> Set[int]:
        """BFS to find connected component starting from a node."""
        component = set()
        queue = deque([start_node])
        
        while queue:
            current = queue.popleft()
            if current not in visited:
                visited.add(current)
                component.add(current)
                
                for neighbor in self.connectivity_graph[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return component
    
    def _check_floating_nodes(self) -> Dict[str, any] or None:
        """Check for floating (isolated) nodes."""
        connected_components = self._find_connected_components()
        
        if len(connected_components) <= 1:
            return None  # All good
        
        # Identify what's in each component
        component_details = []
        for i, nodes in enumerate(connected_components):
            comp_types = set()
            comp_names = []
            
            for comp in self.components:
                if any(node in nodes for node in comp.nodes):
                    comp_types.add(type(comp).__name__)
                    comp_names.append(comp.name or f"{type(comp).__name__}")
            
            component_details.append({
                'nodes': sorted(nodes),
                'component_types': list(comp_types),
                'component_names': comp_names
            })
        
        return {
            'type': 'floating_nodes',
            'message': f"Circuit has {len(connected_components)} isolated networks",
            'details': component_details
        }
    
    def _check_ground_connections(self) -> Dict[str, any] or None:
        """Check for proper ground connections."""
        ground_components = [c for c in self.components if isinstance(c, Ground)]
        power_components = [c for c in self.components if isinstance(c, PowerSupply)]
        
        if not ground_components and power_components:
            return {
                'type': 'missing_ground',
                'message': 'Circuit has voltage sources but no explicit ground connection',
                'suggestion': 'Add a ground component to provide a voltage reference'
            }
        
        return None
    
    def _check_load_components(self) -> Dict[str, any] or None:
        """Check for load components (resistors, etc.)."""
        power_components = [c for c in self.components if isinstance(c, PowerSupply)]
        resistor_components = [c for c in self.components if isinstance(c, Resistor)]
        
        if power_components and not resistor_components:
            return {
                'type': 'missing_load', 
                'message': 'Circuit has voltage sources but no load resistors',
                'suggestion': 'Add resistors to create a complete current path and prevent short circuits'
            }
        
        return None
    
    def _suggest_connection_fixes(self) -> List[Dict[str, any]]:
        """Suggest ways to fix connectivity issues."""
        connected_components = self._find_connected_components()
        suggestions = []
        
        if len(connected_components) <= 1:
            return suggestions
        
        # Find components that should be connected
        power_networks = []
        ground_networks = []
        other_networks = []
        
        for i, nodes in enumerate(connected_components):
            has_power = any(isinstance(c, PowerSupply) and any(n in nodes for n in c.nodes) 
                          for c in self.components)
            has_ground = any(isinstance(c, Ground) and any(n in nodes for n in c.nodes)
                           for c in self.components)
            
            if has_power:
                power_networks.append((i, nodes))
            elif has_ground:
                ground_networks.append((i, nodes))
            else:
                other_networks.append((i, nodes))
        
        # Suggest connecting power to other networks
        if power_networks and (ground_networks or other_networks):
            power_nodes = power_networks[0][1]
            
            if ground_networks:
                ground_nodes = ground_networks[0][1]
                suggestions.append({
                    'type': 'connect_power_to_ground',
                    'message': 'Connect power source to ground through a load resistor',
                    'from_nodes': list(power_nodes),
                    'to_nodes': list(ground_nodes),
                    'suggested_component': 'Resistor'
                })
            
            if other_networks:
                other_nodes = other_networks[0][1]
                suggestions.append({
                    'type': 'connect_power_to_components',
                    'message': 'Connect power source to component network',
                    'from_nodes': list(power_nodes),
                    'to_nodes': list(other_nodes),
                    'suggested_component': 'Wire'
                })
        
        return suggestions

def validate_and_report(components: List[Component]) -> str:
    """Quick validation function that returns a formatted report."""
    validator = CircuitValidator()
    result = validator.validate_circuit(components)
    
    report = "🔍 CIRCUIT VALIDATION REPORT\n"
    report += "=" * 40 + "\n"
    
    if result['is_valid']:
        report += "✅ Circuit appears valid!\n"
    else:
        report += "❌ Circuit has issues that need fixing:\n"
        
        for issue in result['issues']:
            report += f"\n🚫 {issue['message']}\n"
            if 'details' in issue:
                for i, detail in enumerate(issue['details']):
                    report += f"   Network {i+1}: nodes {detail['nodes']} "
                    report += f"({', '.join(detail['component_types'])})\n"
    
    if result['warnings']:
        report += "\n⚠️ Warnings:\n"
        for warning in result['warnings']:
            report += f"   • {warning['message']}\n"
    
    if result['suggestions']:
        report += "\n💡 Suggestions to fix issues:\n"
        for suggestion in result['suggestions']:
            report += f"   • {suggestion['message']}\n"
    
    return report

if __name__ == "__main__":
    # Test with the floating nodes example
    vs = PowerSupply("VS1", n1=1, n2=0, voltage=15.0)
    wire1 = Wire("W1", n1=3, n2=4)
    wire2 = Wire("W2", n1=5, n2=6)  
    wire3 = Wire("W3", n1=4, n2=5)
    gnd = Ground("GND", n1=7)
    
    components = [vs, wire1, wire2, wire3, gnd]
    
    print(validate_and_report(components))