#!/bin/bash

# Docker Build Script for Book Scraper
# Usage: ./scripts/docker-build.sh [options]

set -e

# Default values
IMAGE_NAME="book-scraper"
TAG="latest"
BUILD_ARGS=""
PLATFORM=""
NO_CACHE=false
VERBOSE=false
PUSH=false
REGISTRY=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to show usage
show_usage() {
    cat << EOF
Docker Build Script for Book Scraper

Usage: $0 [OPTIONS]

OPTIONS:
    -t, --tag TAG           Set image tag (default: latest)
    -n, --name NAME         Set image name (default: book-scraper)
    -p, --platform PLATFORM Set target platform (e.g., linux/amd64,linux/arm64)
    --no-cache              Build without using cache
    --push                  Push image to registry after build
    --registry REGISTRY     Registry to push to (requires --push)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0                                          # Basic build
    $0 -t v1.0.0                              # Build with specific tag
    $0 --no-cache -t dev                       # Build without cache
    $0 -p linux/amd64,linux/arm64 -t multi    # Multi-platform build
    $0 --push --registry myregistry.com -t prod # Build and push

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
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
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

# Validate dependencies
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Set full image name
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

print_status "Starting Docker build process..."
print_status "Image: $FULL_IMAGE_NAME"

# Build Docker build command
BUILD_CMD="docker build"

# Add build arguments
if [[ "$NO_CACHE" == "true" ]]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
    print_status "Cache disabled"
fi

if [[ -n "$PLATFORM" ]]; then
    BUILD_CMD="$BUILD_CMD --platform $PLATFORM"
    print_status "Target platform: $PLATFORM"
fi

# Add optimization flags
BUILD_CMD="$BUILD_CMD --compress"
BUILD_CMD="$BUILD_CMD --rm"

# Add tag
BUILD_CMD="$BUILD_CMD -t $FULL_IMAGE_NAME"

# Add context
BUILD_CMD="$BUILD_CMD ."

# Show command if verbose
if [[ "$VERBOSE" == "true" ]]; then
    print_status "Build command: $BUILD_CMD"
fi

# Execute build
print_status "Building Docker image..."
if eval "$BUILD_CMD"; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Docker build failed"
    exit 1
fi

# Get image size
IMAGE_SIZE=$(docker images --format "table {{.Size}}" "$FULL_IMAGE_NAME" | tail -n 1)
print_status "Image size: $IMAGE_SIZE"

# Show image layers if verbose
if [[ "$VERBOSE" == "true" ]]; then
    print_status "Image layers:"
    docker history "$FULL_IMAGE_NAME" --format "table {{.CreatedBy}}\t{{.Size}}" | head -10
fi

# Push if requested
if [[ "$PUSH" == "true" ]]; then
    if [[ -z "$REGISTRY" ]]; then
        print_warning "No registry specified, pushing to default registry"
    fi

    print_status "Pushing image to registry..."
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image"
        exit 1
    fi
fi

# Security scan (if available)
if command -v docker &> /dev/null && docker version --format '{{.Server.Version}}' | grep -q "^2[0-9]"; then
    print_status "Running security scan..."
    if docker scout cves "$FULL_IMAGE_NAME" 2>/dev/null || true; then
        print_status "Security scan completed (check output above)"
    else
        print_warning "Security scan not available or failed"
    fi
fi

print_success "Build process completed successfully!"
print_status "You can now run the container with:"
print_status "  docker run --rm -v \$(pwd)/output:/app/output -v \$(pwd)/logs:/app/logs $FULL_IMAGE_NAME"
