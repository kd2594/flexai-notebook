#!/bin/bash

# FlexAI Notebook Platform - Stop Local Services

echo "========================================="
echo "Stopping FlexAI Notebook Platform"
echo "========================================="
echo ""

# Stop processes by PID if available
if [ -f logs/mock-api.pid ]; then
    PID=$(cat logs/mock-api.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped Mock API (PID: $PID)"
    rm logs/mock-api.pid
fi

if [ -f logs/backend.pid ]; then
    PID=$(cat logs/backend.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped Backend API (PID: $PID)"
    rm logs/backend.pid
fi

if [ -f logs/jupyter.pid ]; then
    PID=$(cat logs/jupyter.pid)
    kill $PID 2>/dev/null && echo "✓ Stopped Jupyter (PID: $PID)"
    rm logs/jupyter.pid
fi

# Fallback: kill by process name
pkill -f "mock_flexai_server" 2>/dev/null && echo "✓ Stopped Mock API processes"
pkill -f "uvicorn main:app" 2>/dev/null && echo "✓ Stopped Backend API processes"
pkill -f "jupyter-notebook" 2>/dev/null && echo "✓ Stopped Jupyter processes"

echo ""
echo "========================================="
echo "✅ All services stopped"
echo "========================================="
