"""Tests for AST-based framework detection.

This test module validates Issue #2 fix: False Positive Framework Detection.
Tests ensure that framework detection uses actual import analysis instead of
filename patterns, preventing false positives.
"""

import pytest
from pathlib import Path

from envwizard.detectors import ProjectDetector


class TestASTBasedDetection:
    """Test AST-based import detection for frameworks."""

    def test_empty_app_py_no_detection(self, temp_project_dir):
        """Test that empty app.py does not trigger framework detection.

        Issue #2: Empty app.py should not detect any framework.
        """
        # Create empty app.py
        (temp_project_dir / "app.py").write_text("")

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Empty file should not trigger any framework detection
        assert info["frameworks"] == [], \
            "Empty app.py should not detect any frameworks"

    def test_flask_only_detection(self, temp_project_dir):
        """Test that Flask-only app.py detects only Flask.

        Issue #2: Should detect Flask, NOT FastAPI.
        """
        # Create app.py with Flask imports only
        flask_code = """from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello World"})

if __name__ == '__main__':
    app.run(debug=True)
"""
        (temp_project_dir / "app.py").write_text(flask_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should detect Flask only
        assert "flask" in info["frameworks"], "Should detect Flask"
        assert "fastapi" not in info["frameworks"], \
            "Should NOT detect FastAPI (false positive)"

    def test_fastapi_only_detection(self, temp_project_dir):
        """Test that FastAPI-only app.py detects only FastAPI.

        Issue #2: Should detect FastAPI, NOT Flask.
        """
        # Create app.py with FastAPI imports only
        fastapi_code = """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    return item
"""
        (temp_project_dir / "app.py").write_text(fastapi_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should detect FastAPI only
        assert "fastapi" in info["frameworks"], "Should detect FastAPI"
        assert "flask" not in info["frameworks"], \
            "Should NOT detect Flask (false positive)"

    def test_both_frameworks_detection(self, temp_project_dir):
        """Test detection when both frameworks are actually imported.

        This is a valid case where both frameworks exist in the project.
        """
        # Create app.py with both Flask and FastAPI
        mixed_code = """from flask import Flask
from fastapi import FastAPI

# Some projects might have both for migration purposes
flask_app = Flask(__name__)
fastapi_app = FastAPI()
"""
        (temp_project_dir / "app.py").write_text(mixed_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should detect both when both are actually imported
        assert "flask" in info["frameworks"], "Should detect Flask"
        assert "fastapi" in info["frameworks"], "Should detect FastAPI"

    def test_django_detection_from_imports(self, temp_project_dir):
        """Test Django detection from actual imports."""
        # Create a Django view file
        django_code = """from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

def index(request):
    return HttpResponse("Hello, Django!")

class MyView(View):
    def get(self, request):
        return render(request, 'template.html')
"""
        (temp_project_dir / "views.py").write_text(django_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "django" in info["frameworks"], "Should detect Django from imports"

    def test_multiple_files_detection(self, temp_project_dir):
        """Test detection across multiple Python files."""
        # Create main.py with FastAPI
        (temp_project_dir / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()"
        )

        # Create utils.py with pandas
        (temp_project_dir / "utils.py").write_text(
            "import pandas as pd\nimport numpy as np"
        )

        # Create tests/test_main.py with pytest
        tests_dir = temp_project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text(
            "import pytest\n\ndef test_example():\n    assert True"
        )

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "fastapi" in info["frameworks"], "Should detect FastAPI from main.py"
        assert "pandas" in info["frameworks"], "Should detect pandas from utils.py"
        assert "numpy" in info["frameworks"], "Should detect numpy from utils.py"

    def test_syntax_error_handling(self, temp_project_dir):
        """Test that syntax errors in Python files are handled gracefully."""
        # Create app.py with syntax errors
        invalid_code = """from flask import Flask

def broken_function(
    # Missing closing parenthesis
    return "This won't parse"
"""
        (temp_project_dir / "app.py").write_text(invalid_code)

        # Should not crash, just skip the file
        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should return empty frameworks, not crash
        assert isinstance(info["frameworks"], list), \
            "Should return list even with syntax errors"

    def test_non_utf8_file_handling(self, temp_project_dir):
        """Test that non-UTF8 files are handled gracefully."""
        # Create a file with binary content
        binary_file = temp_project_dir / "data.py"
        binary_file.write_bytes(b'\xff\xfe\x00\x00Invalid UTF-8')

        # Should not crash
        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert isinstance(info["frameworks"], list), \
            "Should handle non-UTF8 files gracefully"

    def test_nested_imports_detection(self, temp_project_dir):
        """Test detection with various import styles."""
        # Create file with different import styles
        code = """import flask
from flask import Flask, render_template
from flask.views import MethodView
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
"""
        (temp_project_dir / "app.py").write_text(code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "flask" in info["frameworks"], "Should detect Flask"
        assert "sqlalchemy" in info["frameworks"], "Should detect SQLAlchemy"

    def test_celery_detection_from_tasks(self, temp_project_dir):
        """Test Celery detection from tasks.py with actual imports."""
        celery_code = """from celery import Celery, Task
from celery.schedules import crontab

app = Celery('myapp', broker='redis://localhost:6379/0')

@app.task
def add(x, y):
    return x + y

@app.task
def process_data():
    pass
"""
        (temp_project_dir / "tasks.py").write_text(celery_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "celery" in info["frameworks"], "Should detect Celery from imports"

    def test_streamlit_detection(self, temp_project_dir):
        """Test Streamlit detection from actual imports."""
        streamlit_code = """import streamlit as st
import pandas as pd

st.title('My Streamlit App')
df = pd.DataFrame({'col1': [1, 2, 3]})
st.dataframe(df)
"""
        (temp_project_dir / "app.py").write_text(streamlit_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "streamlit" in info["frameworks"], "Should detect Streamlit"
        assert "pandas" in info["frameworks"], "Should detect pandas"

    def test_subdirectory_detection(self, temp_project_dir):
        """Test that detection works in common subdirectories."""
        # Create src/app/main.py with FastAPI
        src_dir = temp_project_dir / "src" / "app"
        src_dir.mkdir(parents=True)
        (src_dir / "main.py").write_text("from fastapi import FastAPI")

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "fastapi" in info["frameworks"], \
            "Should detect frameworks in src/app subdirectory"

    def test_requirements_txt_fallback(self, temp_project_dir):
        """Test that requirements.txt is still used for detection."""
        # Create requirements.txt with Flask
        (temp_project_dir / "requirements.txt").write_text("flask>=2.0.0\n")

        # But no Python files with imports

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should detect Flask from requirements.txt
        assert "flask" in info["frameworks"], \
            "Should still detect from requirements.txt"

    def test_comments_and_docstrings_ignored(self, temp_project_dir):
        """Test that imports in comments/docstrings don't trigger detection."""
        code = '''"""
This module demonstrates Flask usage.
Example: from flask import Flask
"""

# from fastapi import FastAPI  # This is commented out

def main():
    """
    Uses Django-style patterns.
    from django import something
    """
    pass
'''
        (temp_project_dir / "app.py").write_text(code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should not detect anything since all imports are in comments/strings
        assert info["frameworks"] == [], \
            "Should not detect frameworks from comments or docstrings"


class TestFrameworkDetectionRegression:
    """Regression tests to ensure Issue #2 is fixed."""

    def test_issue_2_empty_app_py(self, temp_project_dir):
        """Regression test for Issue #2: Empty app.py should not detect frameworks.

        Before fix: Detected both FastAPI and Flask
        After fix: Detects nothing
        """
        (temp_project_dir / "app.py").write_text("")

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "fastapi" not in info["frameworks"], \
            "Issue #2: Empty app.py should not detect FastAPI"
        assert "flask" not in info["frameworks"], \
            "Issue #2: Empty app.py should not detect Flask"
        assert info["frameworks"] == [], \
            "Issue #2: Empty app.py should detect no frameworks"

    def test_issue_2_flask_only(self, temp_project_dir):
        """Regression test for Issue #2: Flask-only code should not detect FastAPI.

        Before fix: Detected both FastAPI and Flask
        After fix: Detects only Flask
        """
        flask_code = """from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World"
"""
        (temp_project_dir / "app.py").write_text(flask_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "flask" in info["frameworks"], \
            "Issue #2: Should detect Flask when imported"
        assert "fastapi" not in info["frameworks"], \
            "Issue #2: Should NOT detect FastAPI when only Flask is used"

    def test_issue_2_fastapi_only(self, temp_project_dir):
        """Regression test for Issue #2: FastAPI-only code should not detect Flask.

        Before fix: Detected both FastAPI and Flask
        After fix: Detects only FastAPI
        """
        fastapi_code = """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
"""
        (temp_project_dir / "app.py").write_text(fastapi_code)

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        assert "fastapi" in info["frameworks"], \
            "Issue #2: Should detect FastAPI when imported"
        assert "flask" not in info["frameworks"], \
            "Issue #2: Should NOT detect Flask when only FastAPI is used"

    def test_issue_2_with_requirements_txt(self, temp_project_dir):
        """Test that AST detection takes precedence over requirements.txt.

        If app.py has Flask but requirements.txt has FastAPI,
        we should trust the actual imports over the dependencies.
        """
        # Create app.py with Flask
        (temp_project_dir / "app.py").write_text("from flask import Flask")

        # Create requirements.txt with FastAPI
        (temp_project_dir / "requirements.txt").write_text("fastapi>=0.100.0")

        detector = ProjectDetector(temp_project_dir)
        info = detector.detect_project_type()

        # Should detect both: Flask from imports, FastAPI from requirements
        assert "flask" in info["frameworks"], \
            "Should detect Flask from actual imports"
        assert "fastapi" in info["frameworks"], \
            "Should detect FastAPI from requirements.txt"
