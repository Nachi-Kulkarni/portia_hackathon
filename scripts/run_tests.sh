#!/bin/bash

# Test runner script for Insurance Claim Negotiator
echo "🧪 Running Insurance Claim Negotiator Tests"
echo "==========================================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Set PYTHONPATH to include src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-mock
fi

# Run different test suites
echo ""
echo "🔬 Running Unit Tests"
echo "===================="
python -m pytest tests/unit/ -v --tb=short

echo ""
echo "🔗 Running Integration Tests (if any)"
echo "===================================="
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
    python -m pytest tests/integration/ -v --tb=short
else
    echo "No integration tests found"
fi

echo ""
echo "🎯 Running Demo Tests"
echo "===================="

echo "Testing basic agent functionality..."
python src/demo/basic_test.py
echo ""

echo "Testing complete pipeline..."
python src/demo/full_pipeline_test.py
echo ""

# Code coverage if coverage is installed
if command -v coverage &> /dev/null; then
    echo "📊 Running tests with coverage..."
    coverage run -m pytest tests/
    coverage report -m
    coverage html
    echo "Coverage report generated in htmlcov/"
else
    echo "💡 Install 'coverage' for code coverage reports: pip install coverage"
fi

echo ""
echo "🎉 Test suite completed!"
echo "========================"
echo ""
echo "📊 Test Summary:"
echo "- Unit tests: tests/unit/"
echo "- Demo tests: src/demo/"
echo "- Results saved to: pipeline_test_results.json"
echo ""
echo "🐛 If tests fail:"
echo "1. Check your .env configuration"
echo "2. Ensure all dependencies are installed: uv sync --all-extras"
echo "3. Check that mock data exists: src/data/mock_policies.json"