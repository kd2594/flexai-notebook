#!/bin/bash

# FlexAI Notebook Platform - Stop Script

set -e

echo "Stopping FlexAI Notebook Platform..."

# Stop Docker containers
docker-compose down

echo ""
echo "Services stopped successfully!"
