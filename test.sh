#!/bin/bash
#===============================================================================
# Blockchain Forensics Tool - Quick Test Runner
# Run all tests with coverage report
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Blockchain Forensics Tool - Test Runner"
echo "========================================"
echo ""

# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-cov -q

# Run tests
echo ""
echo "Running tests..."
echo ""

python -m pytest tests/ -v \
    --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml:coverage.xml

echo ""
echo "========================================"
echo "Test execution complete!"
echo "========================================"
echo ""
echo "Coverage report: htmlcov/index.html"
echo "Coverage XML: coverage.xml"
echo ""
