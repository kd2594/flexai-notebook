#!/bin/bash

# FlexAI Notebook Platform - Local Startup (No Docker)
# This script starts all services locally without Docker

set -e

echo "========================================="
echo "FlexAI Notebook Platform - Local Mode"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p logs

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓${NC} Loaded environment variables from .env"
else
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

# Update URLs for local mode (replace Docker hostnames with localhost)
export FLEXAI_API_URL="http://localhost:9000"
export DATABASE_URL="postgresql://flexai_user:flexai_password_local@localhost:5432/flexai_notebook_db"
export REDIS_URL="redis://localhost:6379"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python 3 not found! Please install Python 3.9+"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check if required packages are installed
echo ""
echo "Checking Python packages..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}!${NC} Installing required Python packages..."
    pip3 install fastapi uvicorn httpx pydantic redis psycopg2-binary python-dotenv
fi
echo -e "${GREEN}✓${NC} Python packages ready"

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    if pg_isready -h localhost &> /dev/null; then
        echo -e "${GREEN}✓${NC} PostgreSQL is running"
    else
        echo -e "${YELLOW}!${NC} PostgreSQL is installed but not running"
        echo "  Starting PostgreSQL..."
        if command -v brew &> /dev/null; then
            brew services start postgresql@16 || brew services start postgresql
        else
            echo -e "${RED}✗${NC} Please start PostgreSQL manually"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL not installed!"
    echo ""
    echo "Install PostgreSQL:"
    echo "  macOS: brew install postgresql@16"
    echo "  Ubuntu: sudo apt-get install postgresql"
    echo ""
    exit 1
fi

# Check Redis
echo ""
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✓${NC} Redis is running"
    else
        echo -e "${YELLOW}!${NC} Redis is installed but not running"
        echo "  Starting Redis..."
        if command -v brew &> /dev/null; then
            brew services start redis
        else
            echo -e "${RED}✗${NC} Please start Redis manually"
            exit 1
        fi
        sleep 2
    fi
else
    echo -e "${RED}✗${NC} Redis not installed!"
    echo ""
    echo "Install Redis:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    echo ""
    exit 1
fi

# Initialize database if needed
echo ""
echo "Initializing database..."
if psql -h localhost -U flexai_user -d flexai_notebook_db -c "SELECT 1" &> /dev/null; then
    echo -e "${GREEN}✓${NC} Database already exists"
else
    echo "Creating database..."
    createdb -h localhost flexai_notebook_db || true
    psql -h localhost -d flexai_notebook_db -c "CREATE USER flexai_user WITH PASSWORD 'flexai_password_local';" 2>/dev/null || true
    psql -h localhost -d flexai_notebook_db -c "GRANT ALL PRIVILEGES ON DATABASE flexai_notebook_db TO flexai_user;" 2>/dev/null || true
    
    if [ -f docker/init-db.sql ]; then
        psql -h localhost -U flexai_user -d flexai_notebook_db -f docker/init-db.sql
        echo -e "${GREEN}✓${NC} Database initialized"
    fi
fi

# Stop any existing processes
echo ""
echo "Stopping any existing processes..."
pkill -f "mock_flexai_server" 2>/dev/null || true
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "jupyter-notebook" 2>/dev/null || true
sleep 1

# Start Mock FlexAI API
echo ""
echo "Starting Mock FlexAI API..."
cd backend
python3 mock_flexai_server.py > ../logs/mock-api.log 2>&1 &
MOCK_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Mock API started (PID: $MOCK_PID)"
echo "  http://localhost:9000"
sleep 2

# Start Backend API
echo ""
echo "Starting Backend API..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓${NC} Backend API started (PID: $BACKEND_PID)"
echo "  http://localhost:8000"
sleep 2

# Check if jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo ""
    echo -e "${YELLOW}!${NC} Jupyter not found. Installing..."
    pip3 install jupyter jupyterlab notebook
fi

# Start Jupyter Notebook
echo ""
echo "Starting Jupyter Notebook..."
jupyter notebook --port=8888 \
  --NotebookApp.token="${JUPYTER_TOKEN}" \
  --NotebookApp.allow_origin='*' \
  --notebook-dir=./notebooks \
  > logs/jupyter.log 2>&1 &
JUPYTER_PID=$!
echo -e "${GREEN}✓${NC} Jupyter started (PID: $JUPYTER_PID)"
echo "  http://localhost:8888"

# Save PIDs for stop script
echo "$MOCK_PID" > logs/mock-api.pid
echo "$BACKEND_PID" > logs/backend.pid
echo "$JUPYTER_PID" > logs/jupyter.pid

echo ""
echo "========================================="
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo "========================================="
echo ""
echo "📝 Jupyter Notebook: http://localhost:8888"
echo "   Token: ${JUPYTER_TOKEN}"
echo ""
echo "🚀 Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎭 Mock FlexAI API: http://localhost:9000"
echo "   API Docs: http://localhost:9000/docs"
echo ""
echo "Process IDs:"
echo "  Mock API: $MOCK_PID"
echo "  Backend: $BACKEND_PID"
echo "  Jupyter: $JUPYTER_PID"
echo ""
echo "View logs:"
echo "  tail -f logs/mock-api.log"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/jupyter.log"
echo ""
echo "To stop all services:"
echo "  ./stop-local.sh"
echo "========================================="
