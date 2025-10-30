#!/bin/bash
# Comprehensive test coverage runner for AsciiDoc Artisan
# Generates detailed coverage reports and performance metrics

set -e  # Exit on error

echo "========================================="
echo "AsciiDoc Artisan Test Coverage Runner"
echo "========================================="
echo ""

# Configuration
COVERAGE_TARGET=100
MIN_COVERAGE=90
VENV_PATH="venv"
SRC_DIR="src/asciidoc_artisan"
TESTS_DIR="tests"
REPORTS_DIR="coverage_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create it with: python3 -m venv $VENV_PATH"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing test dependencies..."
    pip install -q pytest pytest-cov pytest-qt psutil
fi

# Set Qt platform to offscreen for headless testing
export QT_QPA_PLATFORM=offscreen

echo ""
echo "Running test suite with coverage analysis..."
echo "Target coverage: ${COVERAGE_TARGET}%"
echo "Minimum coverage: ${MIN_COVERAGE}%"
echo ""

# Run tests with coverage
pytest "$TESTS_DIR/" \
    --cov="$SRC_DIR" \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=json:coverage.json \
    --cov-report=xml:coverage.xml \
    -v \
    --tb=short \
    --durations=20 \
    | tee "$REPORTS_DIR/test_run_$TIMESTAMP.log"

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "========================================="
echo "Coverage Analysis"
echo "========================================="

# Extract coverage percentage from coverage.json
if [ -f "coverage.json" ]; then
    COVERAGE=$(python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    print(f\"{data['totals']['percent_covered']:.2f}\")
")

    echo ""
    echo "Overall Coverage: ${COVERAGE}%"
    echo ""

    # Compare to targets
    if (( $(echo "$COVERAGE >= $COVERAGE_TARGET" | bc -l) )); then
        echo -e "${GREEN}✅ Coverage target achieved! (${COVERAGE}% >= ${COVERAGE_TARGET}%)${NC}"
    elif (( $(echo "$COVERAGE >= $MIN_COVERAGE" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Coverage acceptable but below target (${COVERAGE}% >= ${MIN_COVERAGE}%)${NC}"
    else
        echo -e "${RED}❌ Coverage below minimum! (${COVERAGE}% < ${MIN_COVERAGE}%)${NC}"
    fi

    # Find files with low coverage
    echo ""
    echo "Files with coverage < 90%:"
    python3 -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    for file, stats in data['files'].items():
        pct = stats['summary']['percent_covered']
        if pct < 90:
            print(f'  {pct:5.1f}% - {file}')
" || echo "  None (all files >= 90%)"

else
    echo -e "${RED}Error: coverage.json not found${NC}"
fi

echo ""
echo "========================================="
echo "Test Results Summary"
echo "========================================="
echo ""

# Parse test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
fi

echo ""
echo "Reports generated:"
echo "  - HTML Coverage: htmlcov/index.html"
echo "  - JSON Coverage: coverage.json"
echo "  - XML Coverage:  coverage.xml"
echo "  - Test Log:      $REPORTS_DIR/test_run_$TIMESTAMP.log"
echo ""

# Generate summary file
cat > "$REPORTS_DIR/summary_$TIMESTAMP.txt" << EOF
AsciiDoc Artisan Test Coverage Summary
Generated: $TIMESTAMP

Coverage: ${COVERAGE}%
Target: ${COVERAGE_TARGET}%
Minimum: ${MIN_COVERAGE}%

Test Exit Code: $TEST_EXIT_CODE

Reports:
- HTML: htmlcov/index.html
- JSON: coverage.json
- XML: coverage.xml
- Log: coverage_reports/test_run_$TIMESTAMP.log
EOF

echo "Summary saved to: $REPORTS_DIR/summary_$TIMESTAMP.txt"
echo ""

# Open HTML report if in interactive mode and coverage is complete
if [ -t 0 ] && [ -f "htmlcov/index.html" ]; then
    read -p "Open HTML coverage report? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open htmlcov/index.html 2>/dev/null || open htmlcov/index.html 2>/dev/null || echo "Please open htmlcov/index.html manually"
    fi
fi

exit $TEST_EXIT_CODE
