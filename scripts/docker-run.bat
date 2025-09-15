@echo off
REM Docker Compose Helper Script for Book Scraper (Windows)
REM Usage: scripts\docker-run.bat [profile] [additional-args]

setlocal enabledelayedexpansion

set PROFILE=%1
if "%PROFILE%"=="" set PROFILE=default

if "%PROFILE%"=="default" goto :basic
if "%PROFILE%"=="basic" goto :basic
if "%PROFILE%"=="performance" goto :performance
if "%PROFILE%"=="perf" goto :performance
if "%PROFILE%"=="light" goto :light
if "%PROFILE%"=="test" goto :light
if "%PROFILE%"=="dev" goto :dev
if "%PROFILE%"=="development" goto :dev
if "%PROFILE%"=="examples" goto :examples
goto :unknown

:basic
echo Running basic scraper configuration...
shift
docker-compose up scraper %*
goto :end

:performance
echo Running high-performance scraper configuration...
shift
docker-compose --profile performance up scraper-performance %*
goto :end

:light
echo Running light scraper configuration...
shift
docker-compose --profile light up scraper-light %*
goto :end

:dev
echo Running development configuration...
shift
docker-compose -f docker-compose.yml -f docker-compose.override.yml up scraper %*
goto :end

:examples
echo Available example configurations:
echo   basic       - Default settings (10 threads, 1 page)
echo   performance - High performance (20 threads, 10 pages)
echo   light       - Light scraping (5 threads, 1 page)
echo   dev         - Development mode with source mounting
echo.
echo Usage: %0 [profile] [docker-compose-args]
echo Example: %0 performance --build
goto :end

:unknown
echo Unknown profile: %PROFILE%
echo Available profiles: default, performance, light, dev
echo Use '%0 examples' to see all options
exit /b 1

:end
endlocal
