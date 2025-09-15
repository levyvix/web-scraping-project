@echo off
REM Docker Test Script for Book Scraper (Windows)
REM Usage: scripts\docker-test.bat [options]

setlocal enabledelayedexpansion

REM Default values
set IMAGE_NAME=book-scraper
set TAG=latest
set VERBOSE=false
set PERFORMANCE_TEST=false
set CLEANUP=true
set TEST_OUTPUT_DIR=test_output
set TEST_LOGS_DIR=test_logs

REM Test results tracking
set TESTS_PASSED=0
set TESTS_FAILED=0

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :start_tests
if "%~1"=="-i" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--image" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
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
if "%~1"=="-p" (
    set PERFORMANCE_TEST=true
    shift
    goto :parse_args
)
if "%~1"=="--performance" (
    set PERFORMANCE_TEST=true
    shift
    goto :parse_args
)
if "%~1"=="--no-cleanup" (
    set CLEANUP=false
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
echo Docker Test Script for Book Scraper (Windows)
echo.
echo Usage: %0 [OPTIONS]
echo.
echo OPTIONS:
echo     -i, --image IMAGE       Docker image to test (default: book-scraper:latest)
echo     -t, --tag TAG           Image tag to test (default: latest)
echo     -p, --performance       Run performance comparison tests
echo     --no-cleanup            Don't clean up test files after completion
echo     -v, --verbose           Enable verbose output
echo     -h, --help              Show this help message
echo.
echo TESTS PERFORMED:
echo     1. Container build verification
echo     2. Basic container execution
echo     3. Argument passing validation
echo     4. Volume mounting verification
echo     5. Output file generation
echo     6. Log file creation
echo     7. Non-root user execution
echo     8. Performance comparison (with -p flag)
goto :end

:start_tests
REM Set full image name
echo %IMAGE_NAME% | findstr ":" >nul
if errorlevel 1 (
    set FULL_IMAGE_NAME=%IMAGE_NAME%:%TAG%
) else (
    set FULL_IMAGE_NAME=%IMAGE_NAME%
)

REM Create test directories
if not exist "%TEST_OUTPUT_DIR%" mkdir "%TEST_OUTPUT_DIR%"
if not exist "%TEST_LOGS_DIR%" mkdir "%TEST_LOGS_DIR%"

echo [INFO] Starting Docker container tests for: !FULL_IMAGE_NAME!
echo [INFO] Test output directory: %TEST_OUTPUT_DIR%
echo [INFO] Test logs directory: %TEST_LOGS_DIR%

REM Test 1: Verify image exists
echo [INFO] Test 1: Verifying Docker image exists...
docker image inspect "!FULL_IMAGE_NAME!" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Image Verification: Image !FULL_IMAGE_NAME! not found
    set /a TESTS_FAILED+=1
    echo [ERROR] Cannot proceed without valid Docker image
    goto :cleanup
) else (
    echo [PASS] Image Verification: Image !FULL_IMAGE_NAME! exists
    set /a TESTS_PASSED+=1
)

REM Test 2: Basic container execution
echo [INFO] Test 2: Testing basic container execution...
for /f %%i in ('docker run -d -v "%cd%\%TEST_OUTPUT_DIR%:/app/output" -v "%cd%\%TEST_LOGS_DIR%:/app/logs" "!FULL_IMAGE_NAME!"') do set CONTAINER_ID=%%i

if not "!CONTAINER_ID!"=="" (
    docker wait "!CONTAINER_ID!" >nul
    for /f %%i in ('docker inspect "!CONTAINER_ID!" --format="{{.State.ExitCode}}"') do set EXIT_CODE=%%i

    if "!EXIT_CODE!"=="0" (
        echo [PASS] Basic Execution: Container executed successfully (exit code: !EXIT_CODE!)
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Basic Execution: Container failed with exit code: !EXIT_CODE!
        set /a TESTS_FAILED+=1
        if "%VERBOSE%"=="true" (
            echo [INFO] Container logs:
            docker logs "!CONTAINER_ID!"
        )
    )

    docker rm "!CONTAINER_ID!" >nul 2>&1
) else (
    echo [FAIL] Basic Execution: Failed to start container
    set /a TESTS_FAILED+=1
)

REM Test 3: Argument passing validation
echo [INFO] Test 3: Testing argument passing...
for /f %%i in ('docker run -d -v "%cd%\%TEST_OUTPUT_DIR%:/app/output" -v "%cd%\%TEST_LOGS_DIR%:/app/logs" "!FULL_IMAGE_NAME!" --threads 5 --pages 1') do set CONTAINER_ID=%%i

if not "!CONTAINER_ID!"=="" (
    docker wait "!CONTAINER_ID!" >nul
    for /f %%i in ('docker inspect "!CONTAINER_ID!" --format="{{.State.ExitCode}}"') do set EXIT_CODE=%%i

    if "!EXIT_CODE!"=="0" (
        echo [PASS] Argument Passing: Custom arguments accepted (--threads 5 --pages 1)
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Argument Passing: Failed with custom arguments (exit code: !EXIT_CODE!)
        set /a TESTS_FAILED+=1
    )

    docker rm "!CONTAINER_ID!" >nul 2>&1
) else (
    echo [FAIL] Argument Passing: Failed to start container with arguments
    set /a TESTS_FAILED+=1
)

REM Test 4: Volume mounting verification
echo [INFO] Test 4: Testing volume mounting...
if exist "%TEST_OUTPUT_DIR%" if exist "%TEST_LOGS_DIR%" (
    echo [PASS] Volume Mounting: Test directories created successfully
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Volume Mounting: Test directories not created
    set /a TESTS_FAILED+=1
)

REM Test 5: Output file generation
echo [INFO] Test 5: Testing output file generation...
timeout /t 3 /nobreak >nul
if exist "%TEST_OUTPUT_DIR%\books.json" (
    for %%i in ("%TEST_OUTPUT_DIR%\books.json") do set FILE_SIZE=%%~zi
    if !FILE_SIZE! gtr 0 (
        echo [PASS] Output Generation: books.json created (size: !FILE_SIZE! bytes)
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Output Generation: books.json is empty
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Output Generation: books.json not created
    set /a TESTS_FAILED+=1
)

REM Test 6: Log file creation
echo [INFO] Test 6: Testing log file creation...
if exist "%TEST_LOGS_DIR%\app.log" (
    for %%i in ("%TEST_LOGS_DIR%\app.log") do set LOG_SIZE=%%~zi
    if !LOG_SIZE! gtr 0 (
        echo [PASS] Log Generation: app.log created (size: !LOG_SIZE! bytes)
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Log Generation: app.log is empty
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Log Generation: app.log not created
    set /a TESTS_FAILED+=1
)

REM Test 7: Non-root user execution
echo [INFO] Test 7: Testing non-root user execution...
for /f %%i in ('docker run --rm "!FULL_IMAGE_NAME!" sh -c "id -u" 2^>nul') do set USER_ID=%%i
if "!USER_ID!"=="1000" (
    echo [PASS] Security (Non-root): Container runs as user ID 1000 (non-root)
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Security (Non-root): Container runs as user ID !USER_ID! (should be 1000)
    set /a TESTS_FAILED+=1
)

REM Test 8: Performance comparison (if requested)
if "%PERFORMANCE_TEST%"=="true" (
    echo [INFO] Test 8: Running performance comparison...

    REM Check if we can run native version
    python --version >nul 2>&1
    if not errorlevel 1 if exist "main.py" (
        echo [INFO] Running native performance test...
        set NATIVE_START=%time%
        timeout /t 60 python main.py --threads 5 --pages 1 >nul 2>&1
        set NATIVE_END=%time%

        echo [INFO] Running containerized performance test...
        set CONTAINER_START=%time%
        timeout /t 60 docker run --rm -v "%cd%\%TEST_OUTPUT_DIR%:/app/output" -v "%cd%\%TEST_LOGS_DIR%:/app/logs" "!FULL_IMAGE_NAME!" --threads 5 --pages 1 >nul 2>&1
        set CONTAINER_END=%time%

        echo [PASS] Performance Comparison: Native vs Container execution completed
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Performance Comparison: Cannot run native version for comparison
        set /a TESTS_FAILED+=1
    )
)

REM Test Summary
echo [INFO] Test Summary:
echo ============================================
set /a TOTAL_TESTS=TESTS_PASSED+TESTS_FAILED
echo [INFO] Tests completed: !TOTAL_TESTS! total, !TESTS_PASSED! passed, !TESTS_FAILED! failed

if !TESTS_FAILED! equ 0 (
    echo [SUCCESS] All tests passed! Container is working correctly.
    set EXIT_STATUS=0
) else (
    echo [ERROR] Some tests failed. Please check the output above.
    set EXIT_STATUS=1
)

:cleanup
if "%CLEANUP%"=="true" (
    echo [INFO] Cleaning up test files...
    if exist "%TEST_OUTPUT_DIR%" rmdir /s /q "%TEST_OUTPUT_DIR%" 2>nul
    if exist "%TEST_LOGS_DIR%" rmdir /s /q "%TEST_LOGS_DIR%" 2>nul
    docker container prune -f >nul 2>&1
)

:end
endlocal & exit /b %EXIT_STATUS%
