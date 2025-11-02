"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def django_project(temp_project_dir):
    """Create a mock Django project."""
    # Create manage.py
    (temp_project_dir / "manage.py").write_text("#!/usr/bin/env python\n")

    # Create requirements.txt
    requirements = """
django>=4.0.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
    """.strip()
    (temp_project_dir / "requirements.txt").write_text(requirements)

    return temp_project_dir


@pytest.fixture
def fastapi_project(temp_project_dir):
    """Create a mock FastAPI project."""
    # Create main.py
    (temp_project_dir / "main.py").write_text("from fastapi import FastAPI\n")

    # Create requirements.txt
    requirements = """
fastapi>=0.95.0
uvicorn[standard]>=0.21.0
sqlalchemy>=2.0.0
    """.strip()
    (temp_project_dir / "requirements.txt").write_text(requirements)

    return temp_project_dir


@pytest.fixture
def flask_project(temp_project_dir):
    """Create a mock Flask project."""
    # Create app.py
    (temp_project_dir / "app.py").write_text("from flask import Flask\n")

    # Create requirements.txt
    requirements = """
flask>=2.3.0
flask-sqlalchemy>=3.0.0
    """.strip()
    (temp_project_dir / "requirements.txt").write_text(requirements)

    return temp_project_dir


@pytest.fixture
def pyproject_project(temp_project_dir):
    """Create a project with pyproject.toml."""
    pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.95.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
]
    """.strip()
    (temp_project_dir / "pyproject.toml").write_text(pyproject_content)

    return temp_project_dir


@pytest.fixture
def empty_project(temp_project_dir):
    """Create an empty project directory."""
    return temp_project_dir
