#!/bin/bash
set -e

echo "=========================================="
echo "Starting Application"
echo "=========================================="

# Start FastAPI in background
echo "Starting API on http://localhost:8000..."
python -m src.api.main_api &
API_PID=$!

# Wait a moment
sleep 2

# Start Streamlit
echo ""
echo "Starting Dashboard on http://localhost:8501..."
streamlit run src/app/dashboard.py

# Cleanup
kill $API_PID 2>/dev/null || true
