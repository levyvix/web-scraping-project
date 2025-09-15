#!/bin/bash

# Docker Compose Helper Script for Book Scraper
# Usage: ./scripts/docker-run.sh [profile] [additional-args]

set -e

PROFILE=${1:-default}
shift || true  # Remove first argument, keep the rest

case $PROFILE in
    "default"|"basic")
        echo "Running basic scraper configuration..."
        docker-compose up scraper "$@"
        ;;
    "performance"|"perf")
        echo "Running high-performance scraper configuration..."
        docker-compose --profile performance up scraper-performance "$@"
        ;;
    "light"|"test")
        echo "Running light scraper configuration..."
        docker-compose --profile light up scraper-light "$@"
        ;;
    "dev"|"development")
        echo "Running development configuration..."
        docker-compose -f docker-compose.yml -f docker-compose.override.yml up scraper "$@"
        ;;
    "examples")
        echo "Available example configurations:"
        echo "  basic       - Default settings (10 threads, 1 page)"
        echo "  performance - High performance (20 threads, 10 pages)"
        echo "  light       - Light scraping (5 threads, 1 page)"
        echo "  dev         - Development mode with source mounting"
        echo ""
        echo "Usage: $0 [profile] [docker-compose-args]"
        echo "Example: $0 performance --build"
        ;;
    *)
        echo "Unknown profile: $PROFILE"
        echo "Available profiles: default, performance, light, dev"
        echo "Use '$0 examples' to see all options"
        exit 1
        ;;
esac
