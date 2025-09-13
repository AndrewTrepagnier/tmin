.PHONY: help install install-dev test test-cov lint format clean build

help:  ## Show this help message
	@echo "TMIN Development Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	python -m pytest tests/ -v

test-cov:  ## Run tests with coverage
	python -m pytest tests/ --cov=tmin --cov-report=term-missing --cov-report=html -v

test-fast:  ## Run only fast tests (exclude slow/integration)
	python -m pytest tests/ -m "not slow" -v

lint:  ## Run linting checks
	flake8 tmin tests
	mypy tmin --ignore-missing-imports

format:  ## Format code with black
	black tmin tests

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

run-tests:  ## Run tests using the test runner script
	python run_tests.py

# Docker commands
docker-build:  ## Build all Docker images
	./docker.sh build

docker-test:  ## Run tests in fresh Docker container
	./docker.sh test

docker-test-cov:  ## Run tests with coverage in fresh Docker container
	./docker.sh test-cov

docker-dev:  ## Start development Docker container
	./docker.sh dev

docker-shell:  ## Open shell in development Docker container
	./docker.sh shell

docker-lint:  ## Run linting in fresh Docker container
	./docker.sh lint

docker-format:  ## Format code in fresh Docker container
	./docker.sh format

docker-clean:  ## Clean up Docker resources
	./docker.sh clean

docker-jupyter:  ## Start Jupyter notebook in Docker
	./docker.sh jupyter
