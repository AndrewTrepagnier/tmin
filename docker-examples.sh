#!/bin/bash
# TMIN Docker Usage Examples
# Shows how to use the Docker setup for testing

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_example() {
    echo -e "${GREEN}$1${NC}"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_header "TMIN Docker Usage Examples"

echo ""
print_header "1. Build All Docker Images"
print_example "./docker.sh build"
echo "This builds three images:"
echo "  - tmin-dev (development environment)"
echo "  - tmin-test (testing environment)" 
echo "  - tmin-prod (production environment)"

echo ""
print_header "2. Run Tests in Fresh Container"
print_example "./docker.sh test"
echo "This runs all tests in a clean container environment"

echo ""
print_example "./docker.sh test-cov"
echo "This runs tests with coverage reporting"

echo ""
print_header "3. Start Development Environment"
print_example "./docker.sh dev"
echo "This starts a development container with volume mounting"
echo "Then access it with:"
print_example "./docker.sh shell"

echo ""
print_header "4. Run Code Quality Checks"
print_example "./docker.sh lint"
echo "This runs flake8 and mypy in a fresh container"

print_example "./docker.sh format"
echo "This formats code with black in a fresh container"

echo ""
print_header "5. Start Jupyter Notebook"
print_example "./docker.sh jupyter"
echo "This starts Jupyter at http://localhost:8888"

echo ""
print_header "6. Manual Docker Commands"
print_example "docker run --rm -v \$(pwd):/app tmin-test python -m pytest tests/test_core_dev.py -v"
echo "Run specific test file"

print_example "docker run --rm -v \$(pwd):/app tmin-test python -m pytest tests/ -m \"not slow\" -v"
echo "Run only fast tests"

print_example "docker run --rm -v \$(pwd):/app tmin-dev bash"
echo "Open shell in development container"

echo ""
print_header "7. Clean Up"
print_example "./docker.sh clean"
echo "This cleans up Docker resources"

print_example "./docker.sh stop"
echo "This stops all running containers"

echo ""
print_header "8. Multi-Python Version Testing"
print_example "docker build --build-arg PYTHON_VERSION=3.8 -t tmin-test-38 ."
echo "Test with Python 3.8"

print_example "docker build --build-arg PYTHON_VERSION=3.9 -t tmin-test-39 ."
echo "Test with Python 3.9"

print_example "docker build --build-arg PYTHON_VERSION=3.10 -t tmin-test-310 ."
echo "Test with Python 3.10"

print_example "docker build --build-arg PYTHON_VERSION=3.11 -t tmin-test-311 ."
echo "Test with Python 3.11"

echo ""
print_header "9. Docker Compose Commands"
print_example "docker-compose up -d tmin-dev"
echo "Start development container"

print_example "docker-compose up -d tmin-test"
echo "Start testing container"

print_example "docker-compose up -d tmin-jupyter"
echo "Start Jupyter notebook"

print_example "docker-compose down"
echo "Stop all containers"

echo ""
print_header "10. Troubleshooting"
print_example "docker-compose ps"
echo "Check container status"

print_example "./docker.sh logs"
echo "View container logs"

print_example "docker system prune -a"
echo "Clean up all Docker resources"

echo ""
print_header "Quick Start Workflow"
echo "1. Make sure Docker is running"
echo "2. Build images: ./docker.sh build"
echo "3. Run tests: ./docker.sh test"
echo "4. Start development: ./docker.sh dev"
echo "5. Access shell: ./docker.sh shell"
echo ""
echo "For more details, see DOCKER_README.md"
