#!/bin/bash

# Test automation script for Python Trivia Game
# This script handles starting the Flask app, running tests, and cleanup

set -e  # Exit on any error

# Configuration
FLASK_APP="app.py"
FLASK_PORT=5001
TEST_TIMEOUT=300  # 5 minutes
HEADLESS=${HEADLESS:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Flask app is running
check_flask_app() {
    local max_attempts=30
    local attempt=1
    
    log_info "Checking if Flask app is running..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$FLASK_PORT/ > /dev/null 2>&1; then
            log_success "Flask app is running on port $FLASK_PORT"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for Flask app..."
        sleep 2
        ((attempt++))
    done
    
    log_error "Flask app failed to start after $max_attempts attempts"
    return 1
}

# Start Flask app in background
start_flask_app() {
    log_info "Starting Flask application..."
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Start Flask app in background
    python $FLASK_APP > flask.log 2>&1 &
    FLASK_PID=$!
    
    log_info "Flask app started with PID: $FLASK_PID"
    
    # Wait for app to be ready
    if check_flask_app; then
        return 0
    else
        log_error "Failed to start Flask app"
        return 1
    fi
}

# Stop Flask app
stop_flask_app() {
    if [ ! -z "$FLASK_PID" ]; then
        log_info "Stopping Flask app (PID: $FLASK_PID)..."
        kill $FLASK_PID 2>/dev/null || true
        wait $FLASK_PID 2>/dev/null || true
        log_success "Flask app stopped"
    fi
}

# Run tests
run_tests() {
    local test_type=$1
    
    log_info "Running $test_type tests..."
    
    # Create reports directory
    mkdir -p reports/screenshots
    
    # Set environment variables
    export HEADLESS=$HEADLESS
    export PYTHONPATH=$PWD:$PYTHONPATH
    
    case $test_type in
        "smoke")
            pytest -m smoke --html=reports/smoke-report.html --self-contained-html
            ;;
        "ui")
            pytest -m ui --html=reports/ui-report.html --self-contained-html
            ;;
        "api")
            pytest -m api --html=reports/api-report.html --self-contained-html
            ;;
        "integration")
            pytest -m integration --html=reports/integration-report.html --self-contained-html
            ;;
        "all")
            pytest --html=reports/full-report.html --self-contained-html --cov=src --cov=app --cov-report=html --cov-report=term
            ;;
        *)
            pytest tests/ --html=reports/test-report.html --self-contained-html
            ;;
    esac
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    stop_flask_app
    
    # Kill any remaining Chrome processes (if any)
    pkill -f "chrome" 2>/dev/null || true
    pkill -f "chromedriver" 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Trap cleanup on script exit
trap cleanup EXIT

# Main execution
main() {
    local test_type=${1:-"all"}
    
    log_info "Starting Python Trivia Game test automation"
    log_info "Test type: $test_type"
    log_info "Headless mode: $HEADLESS"
    
    # Check dependencies
    log_info "Checking dependencies..."
    
    if ! command -v python &> /dev/null; then
        log_error "Python is not installed"
        exit 1
    fi
    
    if ! python -c "import pytest" 2>/dev/null; then
        log_error "pytest is not installed. Run: pip install -r requirements.txt"
        exit 1
    fi
    
    if ! python -c "import selenium" 2>/dev/null; then
        log_error "selenium is not installed. Run: pip install -r requirements.txt"
        exit 1
    fi
    
    # Start Flask app only for UI and integration tests
    if [[ "$test_type" == "ui" || "$test_type" == "integration" || "$test_type" == "all" ]]; then
        if ! start_flask_app; then
            log_error "Failed to start Flask application"
            exit 1
        fi
    fi
    
    # Run tests
    if run_tests $test_type; then
        log_success "All tests completed successfully!"
        
        # Display results
        if [ -f "reports/test-report.html" ] || [ -f "reports/full-report.html" ]; then
            log_info "Test reports generated in reports/ directory"
        fi
        
        if [ -f "reports/coverage/index.html" ]; then
            log_info "Coverage report available at reports/coverage/index.html"
        fi
        
        exit 0
    else
        log_error "Some tests failed!"
        
        # Show recent logs if available
        if [ -f "flask.log" ]; then
            log_warning "Recent Flask logs:"
            tail -20 flask.log
        fi
        
        exit 1
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [TEST_TYPE]"
    echo ""
    echo "TEST_TYPE options:"
    echo "  smoke       - Run smoke tests only"
    echo "  ui          - Run UI tests only"
    echo "  api         - Run API tests only"
    echo "  integration - Run integration tests only"
    echo "  all         - Run all tests (default)"
    echo ""
    echo "Environment variables:"
    echo "  HEADLESS=true   - Run tests in headless mode"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 smoke              # Run smoke tests"
    echo "  HEADLESS=true $0 ui   # Run UI tests in headless mode"
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"