"""
AutoFlow - Automation Workflow Engine
"""

__version__ = "0.1.0"
__author__ = "AutoFlow Team"

from .workflow import Workflow
from .executor import run, run_async

__all__ = ["Workflow", "run", "run_async"]