#!/bin/bash
# Script to run the CRM Analyzer in the background
cd "/Users/barneywong/.gemini/antigravity/file-automation-analyzer"
./venv/bin/python main.py >> automation.log 2>&1
