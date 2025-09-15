#!/bin/bash

# Docker CI Script for Book Scraper
# Combines build, test, and optional performance testing
# Usage: ./scripts/docker-ci.sh [options]

set -e

# Default values
IMAGE_NAME="book-scraper"
TAG="latest"
RUN_TESTS=true
RUN_PERFORMANCE=false
PUSH=false
REGISTRY=""
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[CI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[CI SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[CI WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[CI ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Docker CI Script for Book Scraper

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --tag TAG           Set image tag (default: latest)
    -n, --name NAME         Set image name (default: book-scraper)
    --no-tests              Skip running tests
    -p, --performance       Run performance tests
    --push                  Push image to registry after successful build and test
    --registry REGISTRY     Registry to push to (requires --push)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

WORKFLOW:
    1. Build Docker image
    2. Run container tests (unless --no-tests)
    3. Run performance tests (if --performance)
    4. Push to registry (if --push and all tests pass)

EXAMPLES:
    $0                                      # Build and test
    $0 -t v1.0.0 -p                       # Build, test, and performance test
    $0 --push --registry myregistry.com    # Build, test, and push
    $0 --no-tests -t dev                   # Build only, no tests

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --no-tests)
            RUN_TESTS=false
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
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
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

print_status "Starting CI pipeline for: $FULL_IMAGE_NAME"

# Step 1: Build
print_status "Step 1: Building Docker image..."
BUILD_ARGS="-t $TAG -n $IMAGE_NAME"
if [[ "$VERBOSE" == "true" ]]; then
    BUILD_ARGS="$BUILD_ARGS -v"
fi
if [[ -n "$REGISTRY" ]]; then
    BUILD_ARGS="$BUILD_ARGS --registry $REGISTRY"
fi

if ./scripts/docker-build.sh $BUILD_ARGS; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Step 2: Test
if [[ "$RUN_TESTS" == "true" ]]; then
    print_status "Step 2: Running container tests..."
    TEST_ARGS="-i $FULL_IMAGE_NAME"
    if [[ "$VERBOSE" == "true" ]]; then
        TEST_ARGS="$TEST_ARGS -v"
    fi

    if ./scripts/docker-test.sh $TEST_ARGS; then
        print_success "Tests passed successfully"
    else
        print_error "Tests failed"
        exit 1
    fi
else
    print_warning "Skipping tests (--no-tests specified)"
fi

# Step 3: Performance tests
if [[ "$RUN_PERFORMANCE" == "true" ]]; then
    print_status "Step 3: Running performance tests..."
    PERF_ARGS="-i $FULL_IMAGE_NAME"
    if [[ "$VERBOSE" == "true" ]]; then
        PERF_ARGS="$PERF_ARGS -v"
    fi

    if ./scripts/docker-performance.sh $PERF_ARGS; then
        print_success "Performance tests completed successfully"
    else
        print_warning "Performance tests failed (continuing with CI)"
    fi
else
    print_status "Skipping performance tests (use -p to enable)"
fi

# Step 4: Push
if [[ "$PUSH" == "true" ]]; then
    print_status "Step 4: Pushing image to registry..."
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image"
        exit 1
    fi
else
    print_status "Skipping push (use --push to enable)"
fi

print_success "CI pipeline completed successfully!"
print_status "Image: $FULL_IMAGE_NAME"
print_status "You can now run the container with:"
print_status "  docker run --rm -v \$(pwd)/output:/app/output -v \$(pwd)/logs:/app/logs $FULL_IMAGE_NAME"
