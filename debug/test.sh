#!/bin/bash

# CucoV2 Quality Testing Script
echo "🤖 CucoV2 Quality Testing Tool"
echo "=============================="

cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if required packages are installed
python3 -c "import requests" 2>/dev/null || {
    echo "⚠️  Installing required packages..."
    pip install requests pandas matplotlib seaborn
}

# Run the testing tool
echo "🚀 Starting quality testing tool..."
python3 test_query.py "$@"
