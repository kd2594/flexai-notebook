# 🚀 FlexAI Notebook - Local Setup WITHOUT Docker

## Overview

This guide shows you how to run the FlexAI Notebook platform locally **without Docker**, using just Python and local services.

## ✅ Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- macOS, Linux, or Windows with WSL2

## 🔧 Installation Steps

### Step 1: Install Dependencies

```bash
cd flexai-notebook

# Install Python packages
pip install -r requirements.txt

# Additional packages for the mock server
pip install fastapi uvicorn[standard] httpx pydantic redis psycopg2-binary
```

### Step 2: Set Up Environment

```bash
# Copy the environment file
cp .env.example .env.local

# Edit .env.local and update these values:
# - Change PostgreSQL URL to use localhost instead of 'postgres' hostname
# - Change Redis URL to use localhost instead of 'redis' hostname
# - Change Mock FlexAI URL to use localhost instead of 'mock-flexai' hostname
```

Edit [.env.local](.env.local):
```env
MOCK_MODE=true
FLEXAI_API_KEY=mock_api_key_12345_local_testing_only
FLEXAI_API_URL=http://localhost:9000
FLEXAI_ORG_ID=mock_org_local_demo_001

JUPYTER_TOKEN=local_demo_token_secure_123
JUPYTER_PORT=8888

DATABASE_URL=postgresql://flexai_user:flexai_password_local@localhost:5432/flexai_notebook_db
REDIS_URL=redis://localhost:6379

SECRET_KEY=local_dev_secret_key_change_in_production_f8e7d6c5b4a39281
```

### Step 3: Install and Start PostgreSQL

#### On macOS (using Homebrew):
```bash
# Install PostgreSQL
brew install postgresql@16

# Start PostgreSQL
brew services start postgresql@16

# Create database and user
createuser flexai_user
createdb -O flexai_user flexai_notebook_db

# Set password
psql -d flexai_notebook_db -c "ALTER USER flexai_user WITH PASSWORD 'flexai_password_local';"

# Initialize database schema
psql -U flexai_user -d flexai_notebook_db -f docker/init-db.sql
```

#### On Ubuntu/Debian:
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database and user
sudo -u postgres createuser flexai_user
sudo -u postgres createdb -O flexai_user flexai_notebook_db
sudo -u postgres psql -c "ALTER USER flexai_user WITH PASSWORD 'flexai_password_local';"

# Initialize database schema
sudo -u postgres psql -U flexai_user -d flexai_notebook_db -f docker/init-db.sql
```

### Step 4: Install and Start Redis

#### On macOS (using Homebrew):
```bash
# Install Redis
brew install redis

# Start Redis
brew services start redis

# Verify it's running
redis-cli ping  # Should return "PONG"
```

#### On Ubuntu/Debian:
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Verify it's running
redis-cli ping  # Should return "PONG"
```

### Step 5: Start the Mock FlexAI API Server

```bash
# In a new terminal window
cd flexai-notebook
export $(cat .env.local | grep -v '^#' | xargs)
python backend/mock_flexai_server.py
```

The mock API will start on http://localhost:9000

### Step 6: Start the Backend API

```bash
# In a new terminal window
cd flexai-notebook
export $(cat .env.local | grep -v '^#' | xargs)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will start on http://localhost:8000

### Step 7: Start Jupyter Notebook

```bash
# In a new terminal window
cd flexai-notebook
export $(cat .env.local | grep -v '^#' | xargs)

# Start Jupyter with custom extensions
jupyter notebook --port=8888 \
  --NotebookApp.token='local_demo_token_secure_123' \
  --NotebookApp.allow_origin='*' \
  --notebook-dir=./notebooks
```

Jupyter will start on http://localhost:8888

## 🎯 Access the Services

Once all services are running:

- **Jupyter Notebook**: http://localhost:8888
  - Token: `local_demo_token_secure_123`
  
- **Backend API**: http://localhost:8000
  - Docs: http://localhost:8000/docs
  
- **Mock FlexAI API**: http://localhost:9000
  - Docs: http://localhost:9000/docs

## 📝 Quick Start Script

Create a file called `start-no-docker.sh`:

```bash
#!/bin/bash

# Load environment
export $(cat .env.local | grep -v '^#' | xargs)

# Check if services are running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start it first."
    exit 1
fi

if ! pg_isready -h localhost > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Please start it first."
    exit 1
fi

# Start Mock FlexAI API
echo "Starting Mock FlexAI API..."
python backend/mock_flexai_server.py > logs/mock-api.log 2>&1 &
MOCK_PID=$!
echo "Mock API started (PID: $MOCK_PID)"

# Wait for mock API to start
sleep 2

# Start Backend API
echo "Starting Backend API..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "Backend API started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 2

# Start Jupyter
echo "Starting Jupyter Notebook..."
jupyter notebook --port=8888 \
  --NotebookApp.token='local_demo_token_secure_123' \
  --NotebookApp.allow_origin='*' \
  --notebook-dir=./notebooks \
  > logs/jupyter.log 2>&1 &
JUPYTER_PID=$!
echo "Jupyter started (PID: $JUPYTER_PID)"

echo ""
echo "==========================================="
echo "✅ All services started!"
echo "==========================================="
echo ""
echo "📝 Jupyter Notebook: http://localhost:8888"
echo "   Token: local_demo_token_secure_123"
echo ""
echo "🚀 Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎭 Mock FlexAI API: http://localhost:9000"
echo ""
echo "Process IDs:"
echo "  Mock API: $MOCK_PID"
echo "  Backend: $BACKEND_PID"
echo "  Jupyter: $JUPYTER_PID"
echo ""
echo "To stop all services:"
echo "  kill $MOCK_PID $BACKEND_PID $JUPYTER_PID"
echo "==========================================="
```

Make it executable and run:
```bash
chmod +x start-no-docker.sh
mkdir -p logs
./start-no-docker.sh
```

## 🛑 Stopping Services

```bash
# Find and kill processes
pkill -f "mock_flexai_server"
pkill -f "uvicorn main:app"
pkill -f "jupyter-notebook"

# Or if you saved PIDs from the start script
kill $MOCK_PID $BACKEND_PID $JUPYTER_PID
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using a port
lsof -i :8888  # For Jupyter
lsof -i :8000  # For Backend
lsof -i :9000  # For Mock API

# Kill the process
kill -9 <PID>
```

### PostgreSQL Connection Error

```bash
# Check if PostgreSQL is running
pg_isready -h localhost

# If not, start it
# macOS:
brew services start postgresql@16
# Linux:
sudo systemctl start postgresql
```

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping

# If not, start it
# macOS:
brew services start redis
# Linux:
sudo systemctl start redis-server
```

### Module Not Found Errors

```bash
# Reinstall requirements
pip install -r requirements.txt
pip install fastapi uvicorn httpx pydantic redis psycopg2-binary
```

## 💡 Tips

1. **Use a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Check logs**:
   ```bash
   tail -f logs/mock-api.log
   tail -f logs/backend.log
   tail -f logs/jupyter.log
   ```

3. **Database GUI** (optional):
   ```bash
   # Install pgAdmin or use psql
   psql -U flexai_user -d flexai_notebook_db
   ```

## 🔄 Switching to Docker Later

If you install Docker later, just:

1. Stop all manual services
2. Use the `.env` file (not `.env.local`)
3. Run `./start.sh`

Everything will work the same way!

## 📊 Comparison: With vs Without Docker

| Feature | With Docker | Without Docker |
|---------|-------------|----------------|
| Setup Complexity | Simple (one command) | Manual (multiple steps) |
| Service Management | Automated | Manual |
| Port Conflicts | Isolated | Can conflict |
| Resource Usage | Higher (containers) | Lower (native) |
| Debugging | Harder (in containers) | Easier (direct access) |
| Production-like | Yes | No |

## 🤝 Need Docker?

**macOS**: Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

**Windows**: Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

**Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/)

Once Docker is installed, you can use the simpler Docker-based setup from [LOCAL_SETUP.md](LOCAL_SETUP.md).
