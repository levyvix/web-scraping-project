@echo off
REM Docker Build Script for Book Scraper (Windows)
REM Usage: scripts\docker-build.bat [options]

setlocal enabledelayedexpansion

REM Default values
set IMAGE_NAME=book-scraper
set TAG=latest
set PLATFORM=
set NO_CACHE=false
set VERBOSE=false
set PUSH=false
set REGISTRY=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :start_build
if "%~1"=="-t" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--tag" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-n" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--name" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set PLATFORM=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--platform" (
    set PLATFORM=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--no-cache" (
    set NO_CACHE=true
    shift
    goto :parse_args
)
if "%~1"=="--push" (
    set PUSH=true
    shift
    goto :parse_args
)
if "%~1"=="--registry" (
    set REGISTRY=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage

echo [ERROR] Unknown option: %~1
goto :show_usage

:show_usage
echo Docker Build Script for Book Scraper (Windows)
echo.
echo Usage: %0 [OPTIONS]
echo.
echo OPTIONS:
echo     -t, --tag TAG           Set image tag (default: latest)
echo     -n, --name NAME         Set image name (default: book-scraper)
echo     -p, --platform PLATFORM Set target platform
echo     --no-cache              Build without using cache
echo     --push                  Push image to registry after build
echo     --registry REGISTRY     Registry to push to (requires --push)
echo     -v, --verbose           Enable verbose output
echo     -h, --help              Show this help message
echo.
echo EXAMPLES:
echo     %0                                    # Basic build
echo     %0 -t v1.0.0                        # Build with specific tag
echo     %0 --no-cache -t dev                # Build without cache
echo     %0 --push --registry myregistry.com -t prod # Build and push
goto :end

:start_build
REM Validate Docker installation
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    exit /b 1
)

REM Set full image name
if not "%REGISTRY%"=="" (
    set FULL_IMAGE_NAME=%REGISTRY%/%IMAGE_NAME%:%TAG%
) else (
    set FULL_IMAGE_NAME=%IMAGE_NAME%:%TAG%
)

echo [INFO] Starting Docker build process...
echo [INFO] Image: !FULL_IMAGE_NAME!

REM Build Docker build command
set BUILD_CMD=docker build

REM Add build arguments
if "%NO_CACHE%"=="true" (
    set BUILD_CMD=!BUILD_CMD! --no-cache
    echo [INFO] Cache disabled
)

if not "%PLATFORM%"=="" (
    set BUILD_CMD=!BUILD_CMD! --platform %PLATFORM%
    echo [INFO] Target platform: %PLATFORM%
)

REM Add optimization flags
set BUILD_CMD=!BUILD_CMD! --compress --rm

REM Add tag
set BUILD_CMD=!BUILD_CMD! -t !FULL_IMAGE_NAME!

REM Add context
set BUILD_CMD=!BUILD_CMD! .

REM Show command if verbose
if "%VERBOSE%"=="true" (
    echo [INFO] Build command: !BUILD_CMD!
)

REM Execute build
echo [INFO] Building Docker image...
!BUILD_CMD!
if errorlevel 1 (
    echo [ERROR] Docker build failed
    exit /b 1
)

echo [SUCCESS] Docker image built successfully: !FULL_IMAGE_NAME!

REM Get image size
for /f "skip=1 tokens=*" %%i in ('docker images --format "{{.Size}}" "!FULL_IMAGE_NAME!"') do (
    echo [INFO] Image size: %%i
    goto :size_done
)
:size_done

REM Show image layers if verbose
if "%VERBOSE%"=="true" (
    echo [INFO] Image layers:
    docker history "!FULL_IMAGE_NAME!" --format "table {{.CreatedBy}}\t{{.Size}}" | more
)

REM Push if requested
if "%PUSH%"=="true" (
    if "%REGISTRY%"=="" (
        echo [WARNING] No registry specified, pushing to default registry
    )

    echo [INFO] Pushing image to registry...
    docker push "!FULL_IMAGE_NAME!"
    if errorlevel 1 (
        echo [ERROR] Failed to push image
        exit /b 1
    )
    echo [SUCCESS] Image pushed successfully: !FULL_IMAGE_NAME!
)

echo [SUCCESS] Build process completed successfully!
echo [INFO] You can now run the container with:
echo [INFO]   docker run --rm -v "%cd%\output:/app/output" -v "%cd%\logs:/app/logs" !FULL_IMAGE_NAME!

:end
endlocal
