#!/bin/bash
# TMIN Docker Management Script
# Easy commands for Docker operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to show help
show_help() {
    echo "TMIN Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build all Docker images"
    echo "  dev         Start development container"
    echo "  test        Run tests in fresh container"
    echo "  test-cov    Run tests with coverage in fresh container"
    echo "  lint        Run linting in fresh container"
    echo "  format      Format code in fresh container"
    echo "  clean       Clean up Docker resources"
    echo "  jupyter     Start Jupyter notebook server"
    echo "  shell       Open shell in development container"
    echo "  logs        Show container logs"
    echo "  stop        Stop all containers"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build     # Build all images"
    echo "  $0 test      # Run tests in fresh container"
    echo "  $0 dev       # Start development environment"
}

# Function to build images
build_images() {
    print_header "Building TMIN Docker Images"
    
    print_status "Building development image..."
    docker build --target development -t tmin-dev .
    
    print_status "Building testing image..."
    docker build --target testing -t tmin-test .
    
    print_status "Building production image..."
    docker build --target production -t tmin-prod .
    
    print_status "All images built successfully!"
}

# Function to start development container
start_dev() {
    print_header "Starting TMIN Development Environment"
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    print_status "Starting development container..."
    docker-compose up -d tmin-dev
    
    print_status "Development environment ready!"
    print_status "To access the container: docker-compose exec tmin-dev bash"
    print_status "Or use: $0 shell"
}

# Function to run tests in fresh container
run_tests() {
    print_header "Running Tests in Fresh Container"
    
    print_status "Building fresh test container..."
    docker build --target testing -t tmin-test-fresh .
    
    print_status "Running tests..."
    docker run --rm -v "$(pwd)":/app tmin-test-fresh
    
    print_status "Tests completed!"
}

# Function to run tests with coverage
run_tests_cov() {
    print_header "Running Tests with Coverage in Fresh Container"
    
    print_status "Building fresh test container..."
    docker build --target testing -t tmin-test-fresh .
    
    print_status "Running tests with coverage..."
    docker run --rm -v "$(pwd)":/app tmin-test-fresh python -m pytest tests/ --cov=tmin --cov-report=term-missing --cov-report=html -v
    
    print_status "Tests with coverage completed!"
    print_status "Coverage report available in htmlcov/index.html"
}

# Function to run linting
run_lint() {
    print_header "Running Linting in Fresh Container"
    
    print_status "Building fresh development container..."
    docker build --target development -t tmin-dev-fresh .
    
    print_status "Running linting..."
    docker run --rm -v "$(pwd)":/app tmin-dev-fresh bash -c "flake8 tmin tests && mypy tmin --ignore-missing-imports"
    
    print_status "Linting completed!"
}

# Function to format code
format_code() {
    print_header "Formatting Code in Fresh Container"
    
    print_status "Building fresh development container..."
    docker build --target development -t tmin-dev-fresh .
    
    print_status "Formatting code..."
    docker run --rm -v "$(pwd)":/app tmin-dev-fresh black tmin tests
    
    print_status "Code formatting completed!"
}

# Function to clean up Docker resources
clean_docker() {
    print_header "Cleaning Up Docker Resources"
    
    print_status "Stopping all containers..."
    docker-compose down 2>/dev/null || true
    
    print_status "Removing unused images..."
    docker image prune -f
    
    print_status "Removing unused containers..."
    docker container prune -f
    
    print_status "Cleaning completed!"
}

# Function to start Jupyter
start_jupyter() {
    print_header "Starting Jupyter Notebook Server"
    
    print_status "Starting Jupyter container..."
    docker-compose up -d tmin-jupyter
    
    print_status "Jupyter server starting..."
    sleep 5
    
    print_status "Jupyter notebook available at: http://localhost:8888"
    print_status "To stop: docker-compose stop tmin-jupyter"
}

# Function to open shell
open_shell() {
    print_header "Opening Shell in Development Container"
    
    if ! docker-compose ps tmin-dev | grep -q "Up"; then
        print_warning "Development container not running. Starting it..."
        start_dev
        sleep 3
    fi
    
    print_status "Opening shell..."
    docker-compose exec tmin-dev bash
}

# Function to show logs
show_logs() {
    print_header "Showing Container Logs"
    docker-compose logs -f
}

# Function to stop containers
stop_containers() {
    print_header "Stopping All Containers"
    docker-compose down
    print_status "All containers stopped!"
}

# Main script logic
case "${1:-help}" in
    build)
        build_images
        ;;
    dev)
        start_dev
        ;;
    test)
        run_tests
        ;;
    test-cov)
        run_tests_cov
        ;;
    lint)
        run_lint
        ;;
    format)
        format_code
        ;;
    clean)
        clean_docker
        ;;
    jupyter)
        start_jupyter
        ;;
    shell)
        open_shell
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_containers
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
