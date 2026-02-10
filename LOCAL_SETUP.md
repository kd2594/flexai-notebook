# 🎭 FlexAI Notebook - Local Mock Mode Setup

## Overview

This is a **fully local, mock version** of the FlexAI Notebook Platform that runs WITHOUT requiring any real FlexAI credentials or external services. Perfect for local development and testing!

## 🌟 What's Included

This local setup includes:

✅ **Mock FlexAI API Server** - Simulates FlexAI compute platform locally  
✅ **PostgreSQL Database** - Open-source database for session persistence  
✅ **Redis Cache** - Open-source in-memory data store  
✅ **Jupyter Notebook** - Full Jupyter environment with JupyterLab  
✅ **Backend API** - FastAPI server connecting all components  
✅ **Pre-configured Everything** - No manual configuration needed!

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (or Docker + Docker Compose)
- macOS, Linux, or Windows with WSL2

### Step 1: Start the Platform

```bash
cd flexai-notebook
./start.sh
```

That's it! Everything is pre-configured with dummy values.

### Step 2: Access the Services

Once started, access:

- **Jupyter Notebook**: http://localhost:8888
  - Token: `local_demo_token_secure_123`
  
- **Backend API**: http://localhost:8000
  - Docs: http://localhost:8000/docs
  
- **Mock FlexAI API**: http://localhost:9000
  - Docs: http://localhost:9000/docs

### Step 3: Test It Out

1. Open Jupyter at http://localhost:8888
2. Use token: `local_demo_token_secure_123`
3. Open the getting started notebook
4. Click the "Select GPU" button
5. Choose a GPU type (all are mocked)
6. Run your code!

## 📦 What's Running

```
┌─────────────────────────────────────────┐
│  Jupyter Notebook (localhost:8888)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Backend API (localhost:8000)           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Mock FlexAI API (localhost:9000)       │
│  PostgreSQL (localhost:5432)            │
│  Redis (localhost:6379)                 │
└─────────────────────────────────────────┘
```

## 🔧 Configuration

All configuration is in the `.env` file with dummy values:

```env
# Mock FlexAI credentials (not real!)
FLEXAI_API_KEY=mock_api_key_12345_local_testing_only
FLEXAI_API_URL=http://mock-flexai:9000
FLEXAI_ORG_ID=mock_org_local_demo_001

# Jupyter access
JUPYTER_TOKEN=local_demo_token_secure_123

# Database (PostgreSQL running locally)
DATABASE_URL=postgresql://flexai_user:flexai_password_local@postgres:5432/flexai_notebook_db

# Redis (running locally)
REDIS_URL=redis://redis:6379
```

## 🎮 Available Mock GPUs

The mock FlexAI API provides these simulated GPU types:

- **NVIDIA T4** - 16GB, $0.50/hr
- **NVIDIA V100** - 32GB, $2.00/hr
- **NVIDIA A100 40GB** - 40GB, $3.50/hr
- **NVIDIA A100 80GB** - 80GB, $4.50/hr
- **NVIDIA H100** - 80GB, $5.00/hr
- **NVIDIA L4** - 24GB, $1.00/hr

## 🔄 Switching to Production

When you're ready to connect to real FlexAI:

1. **Get your FlexAI credentials** from the FlexAI platform
2. **Update `.env` file**:
   ```env
   MOCK_MODE=false
   FLEXAI_API_KEY=your_real_api_key
   FLEXAI_API_URL=https://api.flexai.com
   FLEXAI_ORG_ID=your_real_org_id
   ```
3. **Restart the platform**:
   ```bash
   ./stop.sh
   ./start.sh
   ```

## 🛠️ Development Commands

```bash
# Start all services
./start.sh

# Stop all services
./stop.sh

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f jupyter
docker-compose logs -f mock-flexai

# Restart a service
docker-compose restart backend

# Access database
docker-compose exec postgres psql -U flexai_user -d flexai_notebook_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

## 📊 Testing the Mock API Directly

You can test the mock FlexAI API directly:

```bash
# Get available GPUs
curl http://localhost:9000/v1/compute/gpu-types \
  -H "Authorization: Bearer mock_key"

# Create an instance
curl -X POST http://localhost:9000/v1/compute/instances \
  -H "Authorization: Bearer mock_key" \
  -H "Content-Type: application/json" \
  -d '{
    "gpu_type": "nvidia-a100-40gb",
    "gpu_count": 1,
    "cpu_cores": 8,
    "ram_gb": 32
  }'
```

## 🐛 Troubleshooting

### Services won't start

```bash
# Clean up and rebuild
docker-compose down -v
docker-compose up --build
```

### Can't access Jupyter

1. Check if service is running: `docker-compose ps`
2. Check logs: `docker-compose logs jupyter`
3. Make sure port 8888 is not in use

### Database connection issues

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check if it's healthy
docker-compose ps postgres
```

## 📁 Project Structure

```
flexai-notebook/
├── .env                    # Local configuration (dummy values)
├── docker-compose.yml      # All services defined here
├── start.sh                # Start script
├── stop.sh                 # Stop script
├── backend/
│   ├── main.py            # FastAPI backend
│   ├── flexai_client.py   # FlexAI API client
│   ├── mock_flexai_server.py  # Mock FlexAI API
│   └── session_manager.py
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.jupyter
│   ├── Dockerfile.mock-flexai
│   └── init-db.sql        # Database initialization
├── frontend/
│   └── extension/         # Jupyter custom extensions
└── notebooks/
    └── getting_started.ipynb
```

## 🎯 What's Different from Production?

| Feature | Mock Mode | Production Mode |
|---------|-----------|----------------|
| FlexAI API | Local mock server | Real FlexAI cloud |
| GPU Provisioning | Instant (simulated) | Real provisioning |
| Actual GPU | Simulated | Real GPU hardware |
| Costs | Free (local) | Real costs apply |
| Internet Required | No | Yes |

## 💡 Tips

1. **No real credentials needed** - All values in `.env` are dummy/mock
2. **Everything runs locally** - No internet connection to external services
3. **Safe to experiment** - Nothing affects real infrastructure
4. **Perfect for demos** - Show the UI/UX without costs
5. **Easy handoff** - FlexAI team just needs to swap the API URL

## 🤝 Handing Off to FlexAI Team

Share this with your FlexAI team:

1. "This is a fully working local demo"
2. "To connect to real FlexAI, just update these 3 values in `.env`:"
   - `FLEXAI_API_KEY`
   - `FLEXAI_API_URL`
   - `FLEXAI_ORG_ID`
3. "Set `MOCK_MODE=false` in `.env`"
4. "Everything else stays the same!"

## 📝 Next Steps

1. ✅ Everything is set up and ready to run
2. ✅ Start with `./start.sh`
3. ✅ Test the interface
4. ✅ When ready, get real FlexAI credentials
5. ✅ Update `.env` and set `MOCK_MODE=false`

---

**Questions?** Check the logs:
```bash
docker-compose logs -f
```
