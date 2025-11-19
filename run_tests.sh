#!/bin/bash
# Script: Run tests for fake-analytics project
# Description: Convenient script to run various test configurations

set -e

echo "=================================="
echo "Fake Analytics Test Runner"
echo "=================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

if ! command -v pytest &> /dev/null; then
    print_warning "pytest not found. Installing test dependencies..."
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist
fi

# Parse command line arguments
TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "unit")
        print_info "Running unit tests..."
        pytest -m unit -v
        ;;
    "e2e")
        print_info "Running end-to-end tests..."
        pytest -m e2e -v
        ;;
    "integration")
        print_info "Running integration tests..."
        pytest -m integration -v
        ;;
    "coverage")
        print_info "Running tests with coverage report..."
        pytest --cov=src/fake_analytics --cov-report=html --cov-report=term-missing
        print_success "Coverage report generated in htmlcov/index.html"
        ;;
    "fast")
        print_info "Running tests (excluding slow tests)..."
        pytest -m "not slow" -v
        ;;
    "parallel")
        print_info "Running tests in parallel..."
        pytest -n auto -v
        ;;
    "watch")
        print_info "Running tests in watch mode..."
        pytest-watch
        ;;
    "verbose")
        print_info "Running all tests with verbose output..."
        pytest -vv -s
        ;;
    "quick")
        print_info "Running quick test (stop on first failure)..."
        pytest -x -v
        ;;
    "all")
        print_info "Running all tests..."
        pytest -v
        ;;
    "help"|"-h"|"--help")
        echo ""
        echo "Usage: ./run_tests.sh [TEST_TYPE]"
        echo ""
        echo "Available test types:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run only unit tests"
        echo "  e2e          - Run only end-to-end tests"
        echo "  integration  - Run only integration tests"
        echo "  coverage     - Run tests with coverage report"
        echo "  fast         - Run tests excluding slow tests"
        echo "  parallel     - Run tests in parallel"
        echo "  verbose      - Run tests with verbose output"
        echo "  quick        - Run tests until first failure"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh unit         # Run unit tests only"
        echo "  ./run_tests.sh coverage     # Generate coverage report"
        echo ""
        exit 0
        ;;
    *)
        print_warning "Unknown test type: $TEST_TYPE"
        echo "Use './run_tests.sh help' to see available options"
        exit 1
        ;;
esac

# Print success message
echo ""
print_success "Tests completed!"
