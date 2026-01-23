#!/bin/bash
# Script to run the CRM Analyzer in the background
cd "$(dirname "$0")"
./venv/bin/python main.py >> automation.log 2>&1
