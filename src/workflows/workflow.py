"""
Workflow definition and management.
"""

from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """A single task node in a workflow."""
    
    name: str
    func: Callable
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    timeout: Optional[int] = None
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node function with given context."""
        logger.info(f"Executing node: {self.name}")
        try:
            result = self.func(context)
            return result
        except Exception as e:
            logger.error(f"Node {self.name} failed: {e}")
            raise


@dataclass
class Workflow:
    """
    A directed acyclic graph of nodes to execute.
    """
    
    name: str
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[tuple] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, name: str, func: Callable, **kwargs) -> "Workflow":
        """Add a node to the workflow."""
        node = Node(name=name, func=func, **kwargs)
        self.nodes[name] = node
        logger.info(f"Added node: {name}")
        return self
    
    def connect(self, from_node: str, to_node: str) -> "Workflow":
        """Connect two nodes (from -> to)."""
        self.edges.append((from_node, to_node))
        logger.info(f"Connected: {from_node} -> {to_node}")
        return self
    
    def validate(self) -> bool:
        """Validate the workflow structure."""
        if not self.nodes:
            raise ValueError("Workflow has no nodes")
        
        # Check all edge references exist
        for from_node, to_node in self.edges:
            if from_node not in self.nodes:
                raise ValueError(f"Unknown node: {from_node}")
            if to_node not in self.nodes:
                raise ValueError(f"Unknown node: {to_node}")
        
        return True
    
    def get_execution_order(self) -> List[str]:
        """Return nodes in topological order."""
        # Simple topological sort (Kahn's algorithm)
        in_degree = {name: 0 for name in self.nodes}
        adj_list = {name: [] for name in self.nodes}
        
        for from_node, to_node in self.edges:
            adj_list[from_node].append(to_node)
            in_degree[to_node] += 1
        
        queue = [n for n, d in in_degree.items() if d == 0]
        order = []
        
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(order) != len(self.nodes):
            raise ValueError("Workflow contains a cycle")
        
        return order