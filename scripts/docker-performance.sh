#!/bin/bash

# Docker Performance Comparison Script for Book Scraper
# Usage: ./scripts/docker-performance.sh [options]

set -e

# Default values
IMAGE_NAME="book-scraper"
TAG="latest"
ITERATIONS=3
THREADS_LIST="5 10 15"
PAGES_LIST="1 2 3"
OUTPUT_FILE="performance_results.json"
VERBOSE=false

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
Docker Performance Comparison Script for Book Scraper

Usage: $0 [OPTIONS]

OPTIONS:
    -i, --image IMAGE       Docker image to test (default: book-scraper:latest)
    -t, --tag TAG           Image tag to test (default: latest)
    -n, --iterations N      Number of test iterations (default: 3)
    --threads LIST          Thread counts to test (default: "5 10 15")
    --pages LIST            Page counts to test (default: "1 2 3")
    -o, --output FILE       Output file for results (default: performance_results.json)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0                                      # Run default performance tests
    $0 -n 5 --threads "10 20" --pages "1"  # Custom test parameters
    $0 -o my_results.json -v               # Custom output file with verbose

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
        -n|--iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        --threads)
            THREADS_LIST="$2"
            shift 2
            ;;
        --pages)
            PAGES_LIST="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
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
if [[ "$IMAGE_NAME" == *":"* ]]; then
    FULL_IMAGE_NAME="$IMAGE_NAME"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

# Validate dependencies
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_warning "Python3 not found - native performance tests will be skipped"
    NATIVE_AVAILABLE=false
else
    NATIVE_AVAILABLE=true
fi

if ! command -v jq &> /dev/null; then
    print_warning "jq not found - JSON output will be basic"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Verify Docker image exists
if ! docker image inspect "$FULL_IMAGE_NAME" >/dev/null 2>&1; then
    print_error "Docker image $FULL_IMAGE_NAME not found"
    exit 1
fi

# Function to measure execution time
measure_execution() {
    local command="$1"
    local description="$2"

    if [[ "$VERBOSE" == "true" ]]; then
        print_status "Running: $description"
        print_status "Command: $command"
    fi

    local start_time=$(date +%s.%N)
    eval "$command" >/dev/null 2>&1
    local exit_code=$?
    local end_time=$(date +%s.%N)

    local duration=$(echo "$end_time - $start_time" | bc -l)

    if [[ $exit_code -eq 0 ]]; then
        echo "$duration"
    else
        echo "ERROR"
    fi
}

# Function to run performance test
run_performance_test() {
    local threads="$1"
    local pages="$2"
    local test_type="$3"  # "native" or "container"

    local total_time=0
    local successful_runs=0
    local times=()

    for ((i=1; i<=ITERATIONS; i++)); do
        print_status "Running $test_type test $i/$ITERATIONS (threads: $threads, pages: $pages)"

        # Create unique test directories for this run
        local test_dir="perf_test_${test_type}_${threads}t_${pages}p_${i}"
        mkdir -p "$test_dir/output" "$test_dir/logs"

        local command=""
        if [[ "$test_type" == "native" ]]; then
            command="cd $test_dir && python3 ../main.py --threads $threads --pages $pages"
        else
            command="docker run --rm -v \$(pwd)/$test_dir/output:/app/output -v \$(pwd)/$test_dir/logs:/app/logs $FULL_IMAGE_NAME --threads $threads --pages $pages"
        fi

        local duration=$(measure_execution "$command" "$test_type execution")

        if [[ "$duration" != "ERROR" ]]; then
            times+=("$duration")
            total_time=$(echo "$total_time + $duration" | bc -l)
            ((successful_runs++))

            if [[ "$VERBOSE" == "true" ]]; then
                print_status "Run $i completed in ${duration}s"
            fi
        else
            print_warning "Run $i failed"
        fi

        # Cleanup test directory
        rm -rf "$test_dir"
    done

    if [[ $successful_runs -gt 0 ]]; then
        local avg_time=$(echo "scale=3; $total_time / $successful_runs" | bc -l)

        # Calculate standard deviation if we have multiple runs
        local std_dev="0"
        if [[ $successful_runs -gt 1 ]]; then
            local variance=0
            for time in "${times[@]}"; do
                local diff=$(echo "$time - $avg_time" | bc -l)
                local squared_diff=$(echo "$diff * $diff" | bc -l)
                variance=$(echo "$variance + $squared_diff" | bc -l)
            done
            variance=$(echo "scale=6; $variance / $successful_runs" | bc -l)
            std_dev=$(echo "scale=3; sqrt($variance)" | bc -l)
        fi

        # Find min and max times
        local min_time=${times[0]}
        local max_time=${times[0]}
        for time in "${times[@]}"; do
            if (( $(echo "$time < $min_time" | bc -l) )); then
                min_time=$time
            fi
            if (( $(echo "$time > $max_time" | bc -l) )); then
                max_time=$time
            fi
        done

        echo "$avg_time,$std_dev,$min_time,$max_time,$successful_runs"
    else
        echo "ERROR,ERROR,ERROR,ERROR,0"
    fi
}

# Initialize results
print_status "Starting performance comparison tests..."
print_status "Image: $FULL_IMAGE_NAME"
print_status "Iterations per test: $ITERATIONS"
print_status "Thread counts: $THREADS_LIST"
print_status "Page counts: $PAGES_LIST"

# Create results array
declare -a results=()
results+=('{"timestamp":"'$(date -Iseconds)'","image":"'$FULL_IMAGE_NAME'","iterations":'$ITERATIONS',"tests":[')

first_test=true

# Run tests for each combination
for threads in $THREADS_LIST; do
    for pages in $PAGES_LIST; do
        print_status "Testing configuration: $threads threads, $pages pages"

        # Add comma separator for JSON
        if [[ "$first_test" == "false" ]]; then
            results+=(',')
        fi
        first_test=false

        # Run native test if available
        native_result="null"
        if [[ "$NATIVE_AVAILABLE" == "true" && -f "main.py" ]]; then
            print_status "Running native performance test..."
            native_data=$(run_performance_test "$threads" "$pages" "native")
            IFS=',' read -r avg_time std_dev min_time max_time successful_runs <<< "$native_data"

            if [[ "$avg_time" != "ERROR" ]]; then
                native_result='{"avg_time":'$avg_time',"std_dev":'$std_dev',"min_time":'$min_time',"max_time":'$max_time',"successful_runs":'$successful_runs'}'
                print_success "Native test completed: ${avg_time}s average"
            else
                print_warning "Native test failed"
            fi
        fi

        # Run container test
        print_status "Running container performance test..."
        container_data=$(run_performance_test "$threads" "$pages" "container")
        IFS=',' read -r avg_time std_dev min_time max_time successful_runs <<< "$container_data"

        container_result="null"
        if [[ "$avg_time" != "ERROR" ]]; then
            container_result='{"avg_time":'$avg_time',"std_dev":'$std_dev',"min_time":'$min_time',"max_time":'$max_time',"successful_runs":'$successful_runs'}'
            print_success "Container test completed: ${avg_time}s average"
        else
            print_warning "Container test failed"
        fi

        # Calculate overhead if both tests succeeded
        overhead="null"
        if [[ "$native_result" != "null" && "$container_result" != "null" ]]; then
            native_avg=$(echo "$native_data" | cut -d',' -f1)
            container_avg=$(echo "$container_data" | cut -d',' -f1)
            overhead_pct=$(echo "scale=2; (($container_avg - $native_avg) / $native_avg) * 100" | bc -l)
            overhead="$overhead_pct"

            if (( $(echo "$overhead_pct > 0" | bc -l) )); then
                print_status "Container overhead: +${overhead_pct}%"
            else
                print_status "Container performance: ${overhead_pct}% (faster than native)"
            fi
        fi

        # Add test result to JSON
        results+=('{')
        results+=('  "threads":'$threads',')
        results+=('  "pages":'$pages',')
        results+=('  "native":'$native_result',')
        results+=('  "container":'$container_result',')
        results+=('  "overhead_percent":'$overhead)
        results+=('}')
    done
done

# Close JSON structure
results+=(']}')

# Write results to file
printf '%s\n' "${results[@]}" > "$OUTPUT_FILE"

# Pretty print if jq is available
if [[ "$JQ_AVAILABLE" == "true" ]]; then
    jq . "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
fi

print_success "Performance test completed!"
print_status "Results saved to: $OUTPUT_FILE"

# Display summary
print_status "Performance Summary:"
echo "===================="

if [[ "$JQ_AVAILABLE" == "true" ]]; then
    jq -r '.tests[] | "Threads: \(.threads), Pages: \(.pages) - Native: \(.native.avg_time // "N/A")s, Container: \(.container.avg_time // "N/A")s, Overhead: \(.overhead_percent // "N/A")%"' "$OUTPUT_FILE"
else
    print_status "Install 'jq' for formatted summary output"
    print_status "Raw results available in: $OUTPUT_FILE"
fi

print_success "Performance comparison completed successfully!"
