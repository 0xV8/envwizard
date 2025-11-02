"""Tests for virtual environment management."""

import platform
import pytest
from pathlib import Path

from envwizard.venv import VirtualEnvManager


class TestVirtualEnvManager:
    """Tests for VirtualEnvManager."""

    def test_create_venv(self, temp_project_dir):
        """Test virtual environment creation."""
        manager = VirtualEnvManager(temp_project_dir)
        success, message, venv_path = manager.create_venv("test_venv")

        assert success is True
        assert venv_path.exists()
        assert (venv_path / "pyvenv.cfg").exists()

    def test_create_venv_already_exists(self, temp_project_dir):
        """Test creating venv when it already exists."""
        manager = VirtualEnvManager(temp_project_dir)

        # Create first time
        success, _, venv_path = manager.create_venv("test_venv")
        assert success is True

        # Try to create again
        success, message, _ = manager.create_venv("test_venv")
        assert success is False
        assert "already exists" in message

    def test_get_python_executable(self, temp_project_dir):
        """Test getting Python executable path."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        python_exe = manager.get_python_executable(venv_path)

        if platform.system() == "Windows":
            assert python_exe.name == "python.exe"
        else:
            assert python_exe.name == "python"

        assert python_exe.exists()

    def test_get_pip_executable(self, temp_project_dir):
        """Test getting pip executable path."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        pip_exe = manager.get_pip_executable(venv_path)

        if platform.system() == "Windows":
            assert pip_exe.name == "pip.exe"
        else:
            assert pip_exe.name == "pip"

        assert pip_exe.exists()

    def test_get_activation_command(self, temp_project_dir):
        """Test getting activation command."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        activation_cmd = manager.get_activation_command(venv_path)

        assert activation_cmd is not None
        if platform.system() == "Windows":
            assert "Scripts" in activation_cmd
        else:
            assert "source" in activation_cmd
            assert "bin/activate" in activation_cmd

    def test_install_dependencies_no_file(self, temp_project_dir):
        """Test installing dependencies when no requirements file exists."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        success, message = manager.install_dependencies(venv_path)
        assert "No requirements file" in message

    def test_install_dependencies_with_file(self, temp_project_dir):
        """Test installing dependencies from requirements file."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        # Create a simple requirements file
        req_file = temp_project_dir / "requirements.txt"
        req_file.write_text("click>=8.0.0\n")

        success, message = manager.install_dependencies(venv_path, req_file)
        assert success is True

    def test_install_package(self, temp_project_dir):
        """Test installing a single package."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        success, message = manager.install_package(venv_path, "click")
        assert success is True

    def test_get_venv_info(self, temp_project_dir):
        """Test getting venv information."""
        manager = VirtualEnvManager(temp_project_dir)
        success, _, venv_path = manager.create_venv("test_venv")

        info = manager.get_venv_info(venv_path)

        assert info["exists"] is True
        assert "python_executable" in info
        assert "activation_command" in info
        assert "python_version" in info or "path" in info

    def test_get_venv_info_nonexistent(self, temp_project_dir):
        """Test getting info for non-existent venv."""
        manager = VirtualEnvManager(temp_project_dir)
        venv_path = temp_project_dir / "nonexistent_venv"

        info = manager.get_venv_info(venv_path)
        assert info["exists"] is False
