#!/bin/bash
# TMIN Docker Test Script
# Tests Docker configuration without running containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        print_status "✓ $1 exists"
        return 0
    else
        print_error "✗ $1 missing"
        return 1
    fi
}

# Function to check Docker syntax
check_dockerfile() {
    print_status "Checking Dockerfile syntax..."
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        # Try to parse the Dockerfile without building
        if docker build --no-cache --target base . >/dev/null 2>&1; then
            print_status "✓ Dockerfile syntax is valid"
        else
            print_error "✗ Dockerfile syntax error"
            return 1
        fi
    else
        print_status "⚠ Docker not available or not running, skipping syntax check"
    fi
}

# Function to check docker-compose syntax
check_compose() {
    print_status "Checking docker-compose.yml syntax..."
    if command -v docker-compose >/dev/null 2>&1; then
        if docker-compose config >/dev/null 2>&1; then
            print_status "✓ docker-compose.yml syntax is valid"
        else
            print_error "✗ docker-compose.yml syntax error"
            return 1
        fi
    else
        print_status "⚠ docker-compose not available, skipping syntax check"
    fi
}

# Main test function
main() {
    print_header "TMIN Docker Configuration Test"
    
    local errors=0
    
    # Check required files
    print_status "Checking required files..."
    check_file "Dockerfile" || ((errors++))
    check_file "docker-compose.yml" || ((errors++))
    check_file ".dockerignore" || ((errors++))
    check_file "docker.sh" || ((errors++))
    check_file "DOCKER_README.md" || ((errors++))
    
    # Check if docker.sh is executable
    if [ -x "docker.sh" ]; then
        print_status "✓ docker.sh is executable"
    else
        print_error "✗ docker.sh is not executable"
        ((errors++))
    fi
    
    # Check Dockerfile syntax
    check_dockerfile || ((errors++))
    
    # Check docker-compose syntax
    check_compose || ((errors++))
    
    # Check if pyproject.toml exists (required for Docker build)
    check_file "pyproject.toml" || ((errors++))
    
    # Check if tmin package exists
    if [ -d "tmin" ]; then
        print_status "✓ tmin package directory exists"
    else
        print_error "✗ tmin package directory missing"
        ((errors++))
    fi
    
    # Check if tests directory exists
    if [ -d "tests" ]; then
        print_status "✓ tests directory exists"
    else
        print_error "✗ tests directory missing"
        ((errors++))
    fi
    
    print_header "Test Results"
    
    if [ $errors -eq 0 ]; then
        print_status "✓ All Docker configuration tests passed!"
        print_status "You can now run: ./docker.sh build"
        print_status "Make sure Docker is running first!"
    else
        print_error "✗ $errors test(s) failed"
        print_error "Please fix the issues above before using Docker"
        exit 1
    fi
}

# Run main function
main "$@"
