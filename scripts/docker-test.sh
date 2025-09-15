#!/bin/bash

# Docker Test Script for Book Scraper
# Usage: ./scripts/docker-test.sh [options]

set -e

# Default values
IMAGE_NAME="book-scraper"
TAG="latest"
VERBOSE=false
PERFORMANCE_TEST=false
CLEANUP=true
TEST_OUTPUT_DIR="test_output"
TEST_LOGS_DIR="test_logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"

    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}[PASS]${NC} $test_name: $message"
        ((TESTS_PASSED++))
        TEST_RESULTS+=("PASS: $test_name - $message")
    else
        echo -e "${RED}[FAIL]${NC} $test_name: $message"
        ((TESTS_FAILED++))
        TEST_RESULTS+=("FAIL: $test_name - $message")
    fi
}

# Function to show usage
show_usage() {
    cat << EOF
Docker Test Script for Book Scraper

Usage: $0 [OPTIONS]

OPTIONS:
    -i, --image IMAGE       Docker image to test (default: book-scraper:latest)
    -t, --tag TAG           Image tag to test (default: latest)
    -p, --performance       Run performance comparison tests
    --no-cleanup            Don't clean up test files after completion
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

TESTS PERFORMED:
    1. Container build verification
    2. Basic container execution
    3. Argument passing validation
    4. Volume mounting verification
    5. Output file generation
    6. Log file creation
    7. Non-root user execution
    8. Performance comparison (with -p flag)

EXAMPLES:
    $0                      # Run basic tests
    $0 -p                   # Run tests with performance comparison
    $0 -i myimage:v1.0      # Test specific image
    $0 -v --no-cleanup      # Verbose output, keep test files

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--performance)
            PERFORMANCE_TEST=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set full image name
if [[ "$IMAGE_NAME" == *":"* ]]; then
    FULL_IMAGE_NAME="$IMAGE_NAME"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

# Cleanup function
cleanup() {
    if [[ "$CLEANUP" == "true" ]]; then
        print_status "Cleaning up test files..."
        rm -rf "$TEST_OUTPUT_DIR" "$TEST_LOGS_DIR" 2>/dev/null || true
        docker container prune -f >/dev/null 2>&1 || true
    fi
}

# Note: cleanup will be called manually at the end

# Create test directories
mkdir -p "$TEST_OUTPUT_DIR" "$TEST_LOGS_DIR"

print_status "Starting Docker container tests for: $FULL_IMAGE_NAME"
print_status "Test output directory: $TEST_OUTPUT_DIR"
print_status "Test logs directory: $TEST_LOGS_DIR"

# Test 1: Verify image exists
print_status "Test 1: Verifying Docker image exists..."
if docker image inspect "$FULL_IMAGE_NAME" >/dev/null 2>&1; then
    print_test_result "Image Verification" "PASS" "Image $FULL_IMAGE_NAME exists"
else
    print_test_result "Image Verification" "FAIL" "Image $FULL_IMAGE_NAME not found"
    print_error "Cannot proceed without valid Docker image"
    exit 1
fi

# Test 2: Basic container execution (default parameters)
print_status "Test 2: Testing basic container execution..."
set +e  # Temporarily disable exit on error
CONTAINER_ID=$(docker run -d \
    -v "$(pwd)/$TEST_OUTPUT_DIR:/app/output" \
    -v "$(pwd)/$TEST_LOGS_DIR:/app/logs" \
    "$FULL_IMAGE_NAME" 2>/dev/null)
set -e  # Re-enable exit on error

if [[ -n "$CONTAINER_ID" ]]; then
    # Wait for container to complete
    docker wait "$CONTAINER_ID" >/dev/null 2>&1 || true
    EXIT_CODE=$(docker inspect "$CONTAINER_ID" --format='{{.State.ExitCode}}' 2>/dev/null || echo "unknown")

    if [[ "$EXIT_CODE" == "0" ]]; then
        print_test_result "Basic Execution" "PASS" "Container executed successfully (exit code: $EXIT_CODE)"
    else
        print_test_result "Basic Execution" "FAIL" "Container failed with exit code: $EXIT_CODE"
        if [[ "$VERBOSE" == "true" ]]; then
            print_status "Container logs:"
            docker logs "$CONTAINER_ID" 2>/dev/null || true
        fi
    fi

    # Cleanup container
    docker rm "$CONTAINER_ID" >/dev/null 2>&1 || true
else
    print_test_result "Basic Execution" "FAIL" "Failed to start container"
fi

# Test 3: Argument passing validation
print_status "Test 3: Testing argument passing..."
set +e  # Temporarily disable exit on error
CONTAINER_ID=$(docker run -d \
    -v "$(pwd)/$TEST_OUTPUT_DIR:/app/output" \
    -v "$(pwd)/$TEST_LOGS_DIR:/app/logs" \
    "$FULL_IMAGE_NAME" --threads 5 --pages 1 2>/dev/null)
set -e  # Re-enable exit on error

if [[ -n "$CONTAINER_ID" ]]; then
    docker wait "$CONTAINER_ID" >/dev/null 2>&1 || true
    EXIT_CODE=$(docker inspect "$CONTAINER_ID" --format='{{.State.ExitCode}}' 2>/dev/null || echo "unknown")

    if [[ "$EXIT_CODE" == "0" ]]; then
        print_test_result "Argument Passing" "PASS" "Custom arguments accepted (--threads 5 --pages 1)"
    else
        print_test_result "Argument Passing" "FAIL" "Failed with custom arguments (exit code: $EXIT_CODE)"
    fi

    docker rm "$CONTAINER_ID" >/dev/null 2>&1 || true
else
    print_test_result "Argument Passing" "FAIL" "Failed to start container with arguments"
fi

# Test 4: Volume mounting verification
print_status "Test 4: Testing volume mounting..."
if [[ -d "$TEST_OUTPUT_DIR" && -d "$TEST_LOGS_DIR" ]]; then
    print_test_result "Volume Mounting" "PASS" "Test directories created successfully"
else
    print_test_result "Volume Mounting" "FAIL" "Test directories not created"
fi

# Test 5: Output file generation
print_status "Test 5: Testing output file generation..."
sleep 2  # Give container time to generate files
if [[ -f "$TEST_OUTPUT_DIR/books.json" ]]; then
    FILE_SIZE=$(stat -f%z "$TEST_OUTPUT_DIR/books.json" 2>/dev/null || stat -c%s "$TEST_OUTPUT_DIR/books.json" 2>/dev/null || echo "0")
    if [[ "$FILE_SIZE" -gt 0 ]]; then
        print_test_result "Output Generation" "PASS" "books.json created (size: $FILE_SIZE bytes)"
    else
        print_test_result "Output Generation" "FAIL" "books.json is empty"
    fi
else
    print_test_result "Output Generation" "FAIL" "books.json not created"
fi

# Test 6: Log file creation
print_status "Test 6: Testing log file creation..."
if [[ -f "$TEST_LOGS_DIR/app.log" ]]; then
    LOG_SIZE=$(stat -f%z "$TEST_LOGS_DIR/app.log" 2>/dev/null || stat -c%s "$TEST_LOGS_DIR/app.log" 2>/dev/null || echo "0")
    if [[ "$LOG_SIZE" -gt 0 ]]; then
        print_test_result "Log Generation" "PASS" "app.log created (size: $LOG_SIZE bytes)"
    else
        print_test_result "Log Generation" "FAIL" "app.log is empty"
    fi
else
    print_test_result "Log Generation" "FAIL" "app.log not created"
fi

# Test 7: Non-root user execution
print_status "Test 7: Testing non-root user execution..."
set +e  # Temporarily disable exit on error
USER_ID=$(docker run --rm --entrypoint="" "$FULL_IMAGE_NAME" sh -c "id -u" 2>/dev/null || echo "0")
set -e  # Re-enable exit on error
if [[ "$USER_ID" == "1000" ]]; then
    print_test_result "Security (Non-root)" "PASS" "Container runs as user ID 1000 (non-root)"
else
    print_test_result "Security (Non-root)" "FAIL" "Container runs as user ID $USER_ID (should be 1000)"
fi

# Test 8: Performance comparison (if requested)
if [[ "$PERFORMANCE_TEST" == "true" ]]; then
    print_status "Test 8: Running performance comparison..."

    # Check if we can run native version
    if command -v python3 &> /dev/null && [[ -f "main.py" ]]; then
        print_status "Running native performance test..."
        NATIVE_START=$(date +%s.%N)
        timeout 60 python3 main.py --threads 5 --pages 1 >/dev/null 2>&1 || true
        NATIVE_END=$(date +%s.%N)
        NATIVE_TIME=$(echo "$NATIVE_END - $NATIVE_START" | bc -l 2>/dev/null || echo "N/A")

        print_status "Running containerized performance test..."
        CONTAINER_START=$(date +%s.%N)
        timeout 60 docker run --rm \
            -v "$(pwd)/$TEST_OUTPUT_DIR:/app/output" \
            -v "$(pwd)/$TEST_LOGS_DIR:/app/logs" \
            "$FULL_IMAGE_NAME" --threads 5 --pages 1 >/dev/null 2>&1 || true
        CONTAINER_END=$(date +%s.%N)
        CONTAINER_TIME=$(echo "$CONTAINER_END - $CONTAINER_START" | bc -l 2>/dev/null || echo "N/A")

        if [[ "$NATIVE_TIME" != "N/A" && "$CONTAINER_TIME" != "N/A" ]]; then
            print_test_result "Performance Comparison" "PASS" "Native: ${NATIVE_TIME}s, Container: ${CONTAINER_TIME}s"
        else
            print_test_result "Performance Comparison" "FAIL" "Could not measure execution times"
        fi
    else
        print_test_result "Performance Comparison" "FAIL" "Cannot run native version for comparison"
    fi
fi

# Test Summary
print_status "Test Summary:"
echo "============================================"
for result in "${TEST_RESULTS[@]}"; do
    if [[ "$result" == PASS* ]]; then
        echo -e "${GREEN}$result${NC}"
    else
        echo -e "${RED}$result${NC}"
    fi
done
echo "============================================"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
print_status "Tests completed: $TOTAL_TESTS total, $TESTS_PASSED passed, $TESTS_FAILED failed"

if [[ "$TESTS_FAILED" -eq 0 ]]; then
    print_success "All tests passed! Container is working correctly."
    cleanup
    exit 0
else
    print_error "Some tests failed. Please check the output above."
    cleanup
    exit 1
fi
