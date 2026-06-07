"""
Workflow executor - runs workflows.
"""

from typing import Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

from .workflow import Workflow, Node

logger = logging.getLogger(__name__)


def run(workflow: Workflow, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a workflow synchronously.
    
    Args:
        workflow: The workflow to execute
        context: Initial context data
        
    Returns:
        Final context after all nodes executed
    """
    workflow.validate()
    ctx = context or {}
    
    execution_order = workflow.get_execution_order()
    logger.info(f"Executing workflow '{workflow.name}' in order: {execution_order}")
    
    for node_name in execution_order:
        node = workflow.nodes[node_name]
        result = node.execute(ctx)
        ctx[node_name] = result
    
    logger.info(f"Workflow '{workflow.name}' completed")
    return ctx


async def run_async(workflow: Workflow, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a workflow asynchronously.
    
    Args:
        workflow: The workflow to execute
        context: Initial context data
        
    Returns:
        Final context after all nodes executed
    """
    workflow.validate()
    ctx = context or {}
    
    execution_order = workflow.get_execution_order()
    logger.info(f"Executing workflow '{workflow.name}' async")
    
    for node_name in execution_order:
        node = workflow.nodes[node_name]
        if asyncio.iscoroutinefunction(node.func):
            result = await node.func(ctx)
        else:
            result = node.func(ctx)
        ctx[node_name] = result
    
    return ctx


def run_parallel(workflow: Workflow, context: Dict[str, Any] = None, max_workers: int = 4) -> Dict[str, Any]:
    """
    Execute independent nodes in parallel.
    
    Note: Only works for nodes with no dependencies.
    """
    workflow.validate()
    ctx = context or {}
    
    # Find nodes with no incoming edges
    in_edges = {to_node for _, to_node in workflow.edges}
    parallel_nodes = [name for name in workflow.nodes if name not in in_edges]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(workflow.nodes[name].execute, ctx): name
            for name in parallel_nodes
        }
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                ctx[name] = future.result()
            except Exception as e:
                logger.error(f"Parallel node {name} failed: {e}")
                raise
    
    return ctx