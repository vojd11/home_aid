#!/bin/bash
"""
Test runner script for Home Aid Kit Manager

Usage:
    ./run_tests.sh [test_category] [options]

Test Categories:
    all         - Run all tests (default)
    unit        - Run only unit tests
    api         - Run only API tests
    integration - Run only integration tests
    services    - Run only service tests

Options:
    --coverage  - Run with coverage report
    --verbose   - Verbose output
    --fast      - Skip slow tests
    --watch     - Run in watch mode (requires pytest-watch)

Examples:
    ./run_tests.sh                    # Run all tests
    ./run_tests.sh unit --coverage    # Run unit tests with coverage
    ./run_tests.sh api --verbose      # Run API tests with verbose output
    ./run_tests.sh --fast             # Run all tests, skip slow ones
"""

set -e

# Default values
TEST_CATEGORY="all"
COVERAGE=false
VERBOSE=false
FAST=false
WATCH=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        unit|api|integration|services|all)
            TEST_CATEGORY="$1"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        --help|-h)
            echo "$(head -n 25 "$0" | tail -n +2 | sed 's/^"""//' | sed 's/"""$//')"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Set test path based on category
case $TEST_CATEGORY in
    unit)
        PYTEST_CMD="$PYTEST_CMD tests/unit/"
        ;;
    api)
        PYTEST_CMD="$PYTEST_CMD tests/api/"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD tests/integration/"
        ;;
    services)
        PYTEST_CMD="$PYTEST_CMD tests/services/"
        ;;
    all)
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
esac

# Add options
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html --cov-report=term-missing"
fi

# Add common options
PYTEST_CMD="$PYTEST_CMD --tb=short --color=yes"

echo "🧪 Running tests: $TEST_CATEGORY"
echo "Command: $PYTEST_CMD"
echo "=========================================="

# Check if we're in Docker or local environment
if [ -f "/.dockerenv" ] || [ "$DOCKER_ENV" = "true" ]; then
    # Running inside Docker container
    exec $PYTEST_CMD
else
    # Running locally, use Docker Compose
    if [ "$WATCH" = true ]; then
        echo "Watch mode requires running inside the container."
        echo "Use: docker-compose exec api bash, then run this script with --watch"
        exit 1
    fi
    
    docker-compose run --rm api $PYTEST_CMD
fi
