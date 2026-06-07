"""
Tests for AutoFlow workflow engine.
"""

import pytest
from autoflow import Workflow, run


def double_value(context):
    return context.get("value", 0) * 2


def add_ten(context):
    return context.get("value", 0) + 10


def test_single_node():
    """Test running a workflow with a single node."""
    wf = Workflow(name="test-single")
    wf.add_node("double", double_value)
    
    result = run(wf, {"value": 5})
    assert result["double"] == 10


def test_two_nodes_connected():
    """Test two nodes connected in series."""
    wf = Workflow(name="test-series")
    wf.add_node("double", double_value)
    wf.add_node("add_ten", add_ten)
    wf.connect("double", "add_ten")
    
    result = run(wf, {"value": 5})
    # 5 * 2 = 10, then 10 + 10 = 20
    assert result["double"] == 10
    assert result["add_ten"] == 20


def test_workflow_validation():
    """Test that empty workflow raises error."""
    wf = Workflow(name="empty")
    with pytest.raises(ValueError):
        wf.validate()


def test_execution_order():
    """Test topological sort of nodes."""
    wf = Workflow(name="test-order")
    wf.add_node("a", double_value)
    wf.add_node("b", double_value)
    wf.add_node("c", double_value)
    wf.connect("a", "b")
    wf.connect("b", "c")
    
    order = wf.get_execution_order()
    assert order == ["a", "b", "c"]


def test_node_config():
    """Test node configuration options."""
    def custom_func(context):
        return context.get("input", 0)
    
    wf = Workflow(name="test-config")
    wf.add_node(
        "custom", 
        custom_func, 
        retry_count=5,
        timeout=30,
        config={"verbose": True}
    )
    
    result = run(wf, {"input": 42})
    assert result["custom"] == 42