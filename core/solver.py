import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict, deque
from components.base_component import Component
from components.ground import Ground
from components.power_supply import PowerSupply

class CircuitSolver:
    def __init__(self):
        """Initialize the circuit solver."""
        self.node_map: Dict[int, int] = {}  # Maps user node numbers to matrix indices
        self.voltage_sources: List[Component] = []  # List of voltage sources
        self.components: List[Component] = []  # All components
        self.node_count = 0  # Number of nodes (excluding ground)
        self.num_voltage_sources = 0  # Number of independent voltage sources
        
    def prepare_system(self, components: List[Component]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare the system matrices for Modified Nodal Analysis.
        Creates the augmented matrix [G C; B D] and RHS vector [I; E].
        
        Args:
            components: List of all components in the circuit
            
        Returns:
            Tuple of (A, z) - system matrix and RHS vector
        """
        print("\nPreparing circuit system...")
        print("Components:", [(type(c).__name__, c.nodes) for c in components])
        
        if not components:
            return np.array([[1]]), np.array([0])  # Return minimal system for empty circuit
            
        self.components = components
        
        # First pass: count nodes and identify voltage sources
        self._count_nodes_and_sources()
        
        print(f"Node mapping: {self.node_map}")
        print(f"Found {self.num_voltage_sources} voltage sources")
        
        # Create system matrices using proper MNA formulation
        n = max(self.node_count, 1)  # Number of nodes (excluding ground)
        m = self.num_voltage_sources  # Number of voltage sources
        total_size = n + m
        
        # Initialize system matrix A = [G C; B D] and RHS vector z = [I; E]
        A = np.zeros((total_size, total_size), dtype=float)
        z = np.zeros(total_size, dtype=float)
        
        print(f"Created {total_size}x{total_size} system matrix ({n} nodes + {m} voltage sources)")
        
        # Extract submatrices for clarity
        G = A[:n, :n]        # Conductance matrix (node-to-node)
        C = A[:n, n:]        # Node-to-voltage-source
        B = A[n:, :n]        # Voltage-source-to-node  
        D = A[n:, n:]        # Voltage-source-to-voltage-source
        I_vec = z[:n]        # Current injection vector
        E_vec = z[n:]        # Voltage source vector
        
        # Add small conductance to ground for numerical stability
        for i in range(n):
            G[i, i] += 1e-12
        
        # Handle ground connections
        self._handle_ground_connections(G, components)
        
        # Second pass: stamp each component into the matrices
        voltage_source_index = 0
        
        for component in components:
            # Skip ground components (already handled)
            if isinstance(component, Ground):
                continue
                
            print(f"\nStamping {type(component).__name__} with nodes {component.nodes}")
            
            if isinstance(component, PowerSupply):
                # Handle voltage source using proper MNA
                self._stamp_voltage_source(component, G, C, B, E_vec, voltage_source_index)
                voltage_source_index += 1
            else:
                # Handle passive components (resistors, wires)
                self._stamp_passive_component(component, G, I_vec)
                
        print("\nFinal system matrix A:")
        print(A)
        print("\nFinal RHS vector z:")
        print(z)
                
        return A, z
    
    def solve(self, components: List[Component]) -> Dict[int, float]:
        """
        Solve the circuit using Modified Nodal Analysis.
        
        Args:
            components: List of all components in the circuit
            
        Returns:
            Dictionary mapping node numbers to their voltages
        """
        # Store components for connectivity analysis
        self.components = components
        
        # Validate circuit connectivity before attempting to solve
        try:
            self._validate_circuit_connectivity()
        except ValueError as e:
            # Re-raise with cleaner error message
            raise ValueError(str(e))
        
        # Prepare the system
        A, z = self.prepare_system(components)
        
        try:
            # Solve the system Ax = z for unknowns x = [V; J]
            # where V are node voltages and J are voltage source currents
            x = np.linalg.solve(A, z)
            
            # Extract node voltages (first n elements)
            node_voltages = x[:self.node_count]
            
            # Create result dictionary mapping original node numbers to voltages
            result = {}
            for node, idx in self.node_map.items():
                result[node] = node_voltages[idx]
            
            # Ground node is always 0V
            result[0] = 0.0
            
            # Store voltage source currents for later use
            if self.num_voltage_sources > 0:
                self.voltage_source_currents = x[self.node_count:]
            
            return result
            
        except np.linalg.LinAlgError as e:
            # Handle singular matrix error with better diagnostics
            print(f"Linear algebra error: {e}")
            print(f"Matrix condition number: {np.linalg.cond(A)}")
            
            # Check for common issues
            if np.linalg.cond(A) > 1e12:
                raise ValueError(
                    "Circuit matrix is poorly conditioned. This usually indicates:\n"
                    "1. Floating nodes (isolated components)\n"
                    "2. Very large conductance values causing numerical issues\n"
                    "3. Missing connections between components\n"
                    "4. Multiple voltage sources in parallel without resistance"
                )
            else:
                raise ValueError("Circuit cannot be solved. Check for floating nodes or invalid connections.")
    
    def _count_nodes_and_sources(self):
        """
        Count nodes and voltage sources in the circuit.
        Node 0 is ground and is not included in the matrices.
        """
        self.node_map.clear()
        self.voltage_sources.clear()
        used_nodes = set()
        
        # Collect all used node numbers and identify voltage sources
        for component in self.components:
            # Count voltage sources
            if isinstance(component, PowerSupply):
                self.voltage_sources.append(component)
            
            # Collect node numbers
            for node in component.nodes:
                if node > 0:  # Skip ground nodes (0 or negative)
                    used_nodes.add(node)
        
        # Sort nodes for consistent ordering
        node_list = sorted(list(used_nodes))
        
        # Create mapping from node numbers to matrix indices
        for idx, node in enumerate(node_list):
            self.node_map[node] = idx
            
        self.node_count = len(used_nodes)
        self.num_voltage_sources = len(self.voltage_sources)
        
        if self.node_count == 0:
            self.node_count = 1  # Ensure at least one node for empty circuits
    
    def _handle_ground_connections(self, G: np.ndarray, components: List[Component]):
        """
        Handle ground connections in the circuit.
        """
        grounded_nodes = set()
        
        # Find explicitly grounded nodes
        for component in components:
            if isinstance(component, Ground):
                node = component.nodes[0]
                if node > 0 and node in self.node_map:
                    idx = self.node_map[node]
                    grounded_nodes.add(idx)
                    print(f"Found explicit ground at node {node} (matrix index {idx})")
        
        # If no explicit ground found, ground the first node
        if not grounded_nodes and self.node_count > 0:
            grounded_nodes.add(0)  # Ground first matrix index
            print(f"No explicit ground found, grounding matrix index 0")
        
        # Apply ground connections by adding large conductance to diagonal
        for idx in grounded_nodes:
            if idx < len(G):
                G[idx, idx] += 1e6
                print(f"Applied ground connection at matrix index {idx}")
    
    def _stamp_voltage_source(self, vs: PowerSupply, G: np.ndarray, C: np.ndarray, 
                             B: np.ndarray, E: np.ndarray, vs_idx: int):
        """
        Stamp a voltage source using proper MNA formulation.
        """
        n1, n2 = vs.nodes
        
        # Convert node numbers to matrix indices
        idx1 = self.node_map.get(n1, -1) if n1 > 0 else -1
        idx2 = self.node_map.get(n2, -1) if n2 > 0 else -1
        
        print(f"Voltage source {vs.voltage}V between nodes {n1},{n2} (indices {idx1},{idx2})")
        
        # Stamp the C matrix (node-to-voltage-source coupling)
        if idx1 >= 0:
            C[idx1, vs_idx] = 1.0
        if idx2 >= 0:
            C[idx2, vs_idx] = -1.0
            
        # Stamp the B matrix (voltage-source-to-node coupling) - transpose of C
        if idx1 >= 0:
            B[vs_idx, idx1] = 1.0
        if idx2 >= 0:
            B[vs_idx, idx2] = -1.0
            
        # Stamp the E vector (voltage source values)
        E[vs_idx] = vs.voltage
        
        print(f"Stamped voltage source: C[:,{vs_idx}] = {C[:, vs_idx]}")
        print(f"Stamped voltage source: B[{vs_idx},:] = {B[vs_idx, :]}")
        print(f"Stamped voltage source: E[{vs_idx}] = {E[vs_idx]}")
    
    def _stamp_passive_component(self, component: Component, G: np.ndarray, I: np.ndarray):
        """
        Stamp a passive component (resistor, wire) into the G matrix.
        """
        if len(component.nodes) < 2:
            return  # Skip single-node components
            
        n1, n2 = component.nodes[:2]
        
        # Convert node numbers to matrix indices  
        idx1 = self.node_map.get(n1, -1) if n1 > 0 else -1
        idx2 = self.node_map.get(n2, -1) if n2 > 0 else -1
        
        # Get component conductance
        if hasattr(component, 'resistance') and component.resistance > 0:
            g = 1.0 / component.resistance
        else:
            # For wires or zero-resistance components, use large conductance
            g = 1e6
            
        print(f"Passive component conductance: {g} S between indices {idx1},{idx2}")
        
        # Stamp conductance matrix
        if idx1 >= 0:
            G[idx1, idx1] += g
        if idx2 >= 0:
            G[idx2, idx2] += g
        if idx1 >= 0 and idx2 >= 0:
            G[idx1, idx2] -= g
            G[idx2, idx1] -= g
            
        print(f"Stamped conductance: diagonal += {g}, off-diagonal -= {g}")

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

    def _analyze_connectivity(self) -> List[set]:
        """
        Analyze circuit connectivity to detect floating nodes.
        Returns a list of connected components (sets of connected nodes).
        """
        # Build adjacency graph
        graph = defaultdict(set)
        all_nodes = set()
        
        for comp in self.components:
            nodes = comp.nodes
            all_nodes.update(nodes)
            
            # Add edges for multi-terminal components  
            if len(nodes) >= 2:
                n1, n2 = nodes[0], nodes[1]
                if n1 != n2:  # Avoid self-loops
                    graph[n1].add(n2)
                    graph[n2].add(n1)
        
        # Find connected components using BFS
        visited = set()
        connected_components = []
        
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
                
                connected_components.append(component)
        
        return connected_components
    
    def _validate_circuit_connectivity(self):
        """
        Validate that the circuit doesn't have floating nodes.
        Raises detailed error message if connectivity issues are found.
        """
        connected_components = self._analyze_connectivity()
        
        if len(connected_components) <= 1:
            return  # All good - single connected network
        
        # Analyze each component to provide helpful error message
        error_msg = "Circuit has floating nodes - multiple isolated networks detected:\n"
        
        for i, component in enumerate(connected_components):
            component_types = []
            for comp in self.components:
                if any(node in component for node in comp.nodes):
                    component_types.append(type(comp).__name__)
            
            error_msg += f"  Network {i+1}: nodes {sorted(component)} "
            error_msg += f"(contains: {', '.join(set(component_types))})\n"
        
        error_msg += "\nTo fix this issue:\n"
        error_msg += "1. Make sure all components are electrically connected\n"
        error_msg += "2. Add wires to connect isolated component groups\n"
        error_msg += "3. Ensure there's a complete current path from power source to ground\n"
        
        raise ValueError(error_msg)