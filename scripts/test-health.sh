#!/bin/bash
# Test script for Docker health check functionality

set -e

echo "Testing Docker health check functionality..."

# Build the container
echo "Building container..."
docker-compose build scraper

# Start container in detached mode
echo "Starting container..."
docker-compose up -d scraper

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Check container status
echo "Checking container status..."
docker-compose ps scraper

# Test health check directly
echo "Testing health check script..."
docker-compose exec scraper python healthcheck.py

# Check Docker health status
echo "Checking Docker health status..."
docker inspect book-scraper --format='{{.State.Health.Status}}'

# Show recent logs
echo "Recent container logs:"
docker-compose logs --tail=20 scraper

# Test graceful shutdown
echo "Testing graceful shutdown..."
docker-compose stop scraper

# Cleanup
echo "Cleaning up..."
docker-compose down

echo "Health check test completed!"
