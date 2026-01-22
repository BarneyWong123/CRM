#!/bin/bash
# Script to run the CRM Analyzer in the background

# Navigate to the script's directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ -f "./venv/bin/python" ]; then
    PYTHON_CMD="./venv/bin/python"
else
    PYTHON_CMD="python3"
fi

echo "Starting CRM Analyzer with $PYTHON_CMD..."
nohup $PYTHON_CMD main.py >> automation.log 2>&1 &
echo "Automation running in background (PID $!). Logs: automation.log"
