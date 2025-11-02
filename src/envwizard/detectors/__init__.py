"""Project type detection modules."""

from envwizard.detectors.base import ProjectDetector
from envwizard.detectors.framework import FrameworkDetector
from envwizard.detectors.dependency import DependencyDetector

__all__ = ["ProjectDetector", "FrameworkDetector", "DependencyDetector"]
