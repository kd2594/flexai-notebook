#!/bin/bash

# FlexAI Notebook Platform - Startup Script

set -e

# Set Docker socket for Colima (macOS)
if [ -S "$HOME/.colima/default/docker.sock" ]; then
    export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
fi

echo "========================================="
echo "FlexAI Notebook Platform"
echo "========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "Starting services..."
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    # Try docker compose (new syntax) first
    if docker compose version &> /dev/null; then
        echo "Using 'docker compose' (Compose V2)..."
        docker compose up -d --build
    # Fall back to docker-compose (old syntax)
    elif command -v docker-compose &> /dev/null; then
        echo "Using 'docker-compose' (Compose V1)..."
        docker-compose up -d --build
    else
        echo "Error: Docker Compose not found!"
        echo "Please install Docker Desktop or Docker Compose."
        exit 1
    fi
else
    echo "Error: Docker not found!"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo ""
    echo "Alternatively, see LOCAL_SETUP_NO_DOCKER.md for running without Docker."
    exit 1
fi

echo ""
echo "========================================="
echo "Services started successfully!"
echo "========================================="
echo ""
echo "📝 Jupyter Notebook: http://localhost:8888"
echo "   Token: ${JUPYTER_TOKEN}"
echo ""
echo "🚀 Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker compose logs -f  # (or docker-compose logs -f)"
echo ""
echo "To stop services:"
echo "  ./stop.sh  # (or docker compose down)"
echo "========================================="
