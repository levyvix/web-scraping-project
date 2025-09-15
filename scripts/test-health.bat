@echo off
REM Test script for Docker health check functionality

echo Testing Docker health check functionality...

REM Build the container
echo Building container...
docker-compose build scraper
if %errorlevel% neq 0 exit /b %errorlevel%

REM Start container in detached mode
echo Starting container...
docker-compose up -d scraper
if %errorlevel% neq 0 exit /b %errorlevel%

REM Wait for container to start
echo Waiting for container to start...
timeout /t 10 /nobreak > nul

REM Check container status
echo Checking container status...
docker-compose ps scraper

REM Test health check directly
echo Testing health check script...
docker-compose exec scraper python healthcheck.py

REM Check Docker health status
echo Checking Docker health status...
docker inspect book-scraper --format="{{.State.Health.Status}}"

REM Show recent logs
echo Recent container logs:
docker-compose logs --tail=20 scraper

REM Test graceful shutdown
echo Testing graceful shutdown...
docker-compose stop scraper

REM Cleanup
echo Cleaning up...
docker-compose down

echo Health check test completed!
