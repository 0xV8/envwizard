.PHONY: help install install-dev test test-cov lint format clean build publish

help:
	@echo "envwizard - Development Commands"
	@echo "================================="
	@echo "install        Install package in production mode"
	@echo "install-dev    Install package with development dependencies"
	@echo "test           Run tests"
	@echo "test-cov       Run tests with coverage report"
	@echo "lint           Run linting checks"
	@echo "format         Format code with black and ruff"
	@echo "type-check     Run mypy type checking"
	@echo "clean          Remove build artifacts"
	@echo "build          Build package"
	@echo "publish-test   Publish to TestPyPI"
	@echo "publish        Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=envwizard --cov-report=html --cov-report=term-missing

lint:
	black --check src/envwizard tests
	ruff check src/envwizard tests

format:
	black src/envwizard tests
	ruff check --fix src/envwizard tests

type-check:
	mypy src/envwizard

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*
