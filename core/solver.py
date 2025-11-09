import numpy as np
from typing import Dict, List, Tuple
from components.base_component import Component
from components.ground import Ground

class CircuitSolver:
    def __init__(self):
        """Initialize the circuit solver."""
        self.node_map: Dict[int, int] = {}  # Maps user node numbers to matrix indices
        self.voltage_sources: List[Component] = []  # List of voltage sources
        self.components: List[Component] = []  # All components
        self.node_count = 0  # Number of nodes (excluding ground)
        
    def prepare_system(self, components: List[Component]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare the system matrices for MNA.
        Creates conductance matrix G and current vector I.
        
        Args:
            components: List of all components in the circuit
            
        Returns:
            Tuple of (G, I) - conductance matrix and current vector
        """
        print("\nPreparing circuit system...")
        print("Components:", [(type(c).__name__, c.nodes) for c in components])
        
        if not components:
            return np.array([[1]]), np.array([0])  # Return minimal system for empty circuit
            
        self.components = components
        
        # First pass: count nodes and identify voltage sources
        self._count_nodes()
        
        print("Node mapping:", self.node_map)
        
        # Create system matrices
        n = max(self.node_count, 1)  # Ensure at least 1x1 matrix
        G = np.zeros((n, n), dtype=float)  # Conductance matrix
        I = np.zeros(n, dtype=float)       # Current vector
        
        print(f"Created {n}x{n} conductance matrix")
        
        # Add small conductance to ground for all nodes
        for i in range(n):
            G[i][i] += 1e-9
        
        # Check for ground components and add strong ground connection
        has_ground = False
        for component in components:
            if isinstance(component, Ground):
                has_ground = True
                node = component.nodes[0]
                if node > 0 and node in self.node_map:
                    idx = self.node_map[node]
                    G[idx][idx] += 1e6  # Strong connection to ground
                    print(f"Added ground connection at node {node} (idx {idx})")
                
        # If no explicit ground found, ground the lowest numbered node
        if not has_ground and len(self.node_map) > 0:
            min_node = min(self.node_map.values())
            G[min_node][min_node] += 1e6
            print(f"No explicit ground found, grounding node index {min_node}")
        
        # Second pass: stamp each component into the matrices
        try:
            for component in components:
                # Skip ground components (already handled)
                if isinstance(component, Ground):
                    continue
                    
                # Map component nodes to matrix indices
                mapped_nodes = []
                for node in component.nodes:
                    if node <= 0:  # Ground node
                        mapped_nodes.append(-1)
                    else:
                        mapped_nodes.append(self.node_map.get(node, -1))
                
                print(f"\nStamping {type(component).__name__}")
                print(f"Original nodes: {component.nodes}")
                print(f"Mapped nodes: {mapped_nodes}")
                
                # Set component's nodes to mapped indices before stamping
                original_nodes = component.nodes
                component.nodes = mapped_nodes
                
                # Get matrix state before stamping
                G_before = G.copy()
                I_before = I.copy()
                
                # Stamp the component
                component.stamp(G, I)
                
                # Print changes made by stamping
                print(f"Changes to G matrix:")
                diff = G - G_before
                print(diff)
                print(f"Changes to I vector:")
                print(I - I_before)
                
                # Restore original node numbers
                component.nodes = original_nodes
                
            print("\nFinal system:")
            print("G matrix:")
            print(G)
            print("I vector:")
            print(I)
                
        except Exception as e:
            raise ValueError(f"Error stamping components: {str(e)}")
            
        return G, I
    
    def solve(self, components: List[Component]) -> Dict[int, float]:
        """
        Solve the circuit using Modified Nodal Analysis.
        
        Args:
            components: List of all components in the circuit
            
        Returns:
            Dictionary mapping node numbers to their voltages
        """
        # Prepare the system
        G, I = self.prepare_system(components)
        
        try:
            # Solve the system GV = I for node voltages V
            V = np.linalg.solve(G, I)
            
            # Create result dictionary mapping original node numbers to voltages
            result = {}
            for node, idx in self.node_map.items():
                result[node] = V[idx]
            
            # Ground node is always 0V
            result[0] = 0.0
            
            return result
            
        except np.linalg.LinAlgError:
            # Handle singular matrix error
            raise ValueError("Circuit cannot be solved. Check for floating nodes or invalid connections.")
    
    def _count_nodes(self):
        """
        Count the number of nodes in the circuit and create the node mapping.
        Node 0 is ground and is not included in the matrices.
        """
        self.node_map.clear()
        used_nodes = set()
        
        # First pass: collect all used node numbers
        for component in self.components:
            for node in component.nodes:
                if node > 0:  # Skip ground nodes (0 or negative)
                    used_nodes.add(node)
        
        # Sort nodes for consistent ordering
        node_list = sorted(list(used_nodes))
        
        # Create mapping from node numbers to matrix indices
        for idx, node in enumerate(node_list):
            self.node_map[node] = idx
            
        self.node_count = len(used_nodes)
        if self.node_count == 0:
            self.node_count = 1  # Ensure at least 1x1 matrix for empty circuits
    
    def calculate_currents(self, node_voltages: Dict[int, float]) -> Dict[str, float]:
        """
        Calculate currents through all components given node voltages.
        
        Args:
            node_voltages: Dictionary of node numbers to voltages
            
        Returns:
            Dictionary mapping component names to their currents
        """
        currents = {}
        
        for component in self.components:
            if hasattr(component, 'calculate_current'):
                # Get the voltages for this component's nodes
                v1 = node_voltages.get(component.nodes[0], 0)
                v2 = node_voltages.get(component.nodes[1], 0) if len(component.nodes) > 1 else 0
                
                # Calculate and store the current
                current = component.calculate_current(v1, v2)
                currents[component.name] = current
        
        return currents