"""
Expenses package for managing and visualizing financial data.
"""

__version__ = "1.0.0"

from .model.model import Model
from .view.view import View
from .controller.controller import Controller
from .classifier import Classifier
from .plot import Plot

__all__ = ["Model", "View", "Controller", "Classifier", "Plot"]
