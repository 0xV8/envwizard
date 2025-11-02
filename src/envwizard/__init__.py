"""envwizard - Smart environment setup tool."""

__version__ = "0.2.0"
__author__ = "Vipin"
__description__ = "One command to create virtual envs, install deps, and configure .env intelligently"

from envwizard.core import EnvWizard

__all__ = ["EnvWizard", "__version__"]
