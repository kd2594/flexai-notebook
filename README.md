# FlexAI Notebook Platform

A Google Colab-like Jupyter Notebook environment integrated with FlexAI compute platform. This platform allows users to run ML workloads (PyTorch, TensorFlow, JAX, etc.) on FlexAI GPUs with an intuitive GPU selection interface.

<img width="2316" height="1510" alt="image" src="https://github.com/user-attachments/assets/2fdde25b-fec1-4b09-a705-307ffecb9bd3" />

<img width="2328" height="1506" alt="image" src="https://github.com/user-attachments/assets/374c7604-46b1-4ee6-a6a7-f0850f46c5ed" />


## ✨ Features

- 🚀 **Jupyter Notebook Environment** - Full-featured Jupyter with JupyterLab support
- 🎮 **Custom GPU Selection UI** - Intuitive modal interface for selecting GPU types
- ⚡ **FlexAI Integration** - Seamless connection to FlexAI compute platform
- 🔌 **Multi-Framework Support** - Pre-installed PyTorch, TensorFlow, JAX, scikit-learn
- 🐳 **Docker-Based Deployment** - Easy setup with Docker Compose
- 🔐 **Session Management** - Automatic session tracking and resource cleanup
- 📊 **Real-time Monitoring** - GPU memory and utilization tracking
- 🔄 **Auto-Provisioning** - Automatic compute instance provisioning and configuration
- 💾 **Persistent Notebooks** - Save and resume your work seamlessly
- 🌐 **RESTful API** - Well-documented API for programmatic access

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [FlexAI Integration](#flexai-integration)
- [Development](#development)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Web UI)                        │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │  Jupyter Notebook    │  │   GPU Selection Widget       ││
│  │      Interface       │  │   (Custom Extension)         ││
│  └──────────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Server                        │
│  ┌──────────────────────┐  ┌──────────────────────────────┐│
│  │   FastAPI Service    │  │   Session Manager            ││
│  │   /api/compute       │  │   /api/sessions              ││
│  └──────────────────────┘  └──────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                FlexAI Compute Platform                       │
│         (GPU/CPU Resource Provisioning)                      │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **Python 3.9+** (for local development)
- **macOS, Linux, or Windows** with WSL2
- **FlexAI API credentials** (only for production mode)

### Quick Start (Mock Mode - No Credentials Required!)

Want to test locally without FlexAI credentials? We've got you covered!

1. **Navigate to the repository:**
```bash
cd flexai-notebook
```

2. **Start the platform (uses pre-configured mock values):**
```bash
chmod +x start.sh stop.sh
./start.sh
```

3. **Access Jupyter:**
- Open http://localhost:8888
- Token: `local_demo_token_secure_123`

That's it! Everything runs locally with a mock FlexAI API. Perfect for testing and demos!

📖 **See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed mock mode documentation.**

### Production Setup (Real FlexAI Connection)

1. **Clone or navigate to the repository:**
```bash
cd flexai-notebook
```

2. **Set up environment variables:**
```bash
cp .env.example .env
```

3. **Edit `.env` with your real FlexAI credentials:**
```env
MOCK_MODE=false
FLEXAI_API_KEY=your_flexai_api_key_here
FLEXAI_API_URL=https://api.flexai.com
FLEXAI_ORG_ID=your_org_id
JUPYTER_TOKEN=my_secure_token_12345
SECRET_KEY=your_secret_key_for_jwt_tokens
```

4. **Make startup script executable:**
```bash
chmod +x start.sh stop.sh
```

5. **Build and run with Docker:**
```bash
./start.sh
```

Or manually:
```bash
docker-compose up --build -d
```

6. **Access the platform:**
- **Jupyter Notebook:** http://localhost:8888
  - Token: The value you set in `JUPYTER_TOKEN`
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### First Time Setup

1. Open your browser to http://localhost:8888
2. Enter the Jupyter token from your `.env` file
3. Open the `getting_started.ipynb` notebook
4. Click the **"FlexAI Compute"** button in the toolbar
5. Select your desired GPU configuration
6. Wait for provisioning (usually 30-60 seconds)
7. Start running your ML code!

## Configuration

### Environment Variables

Edit the `.env` file with your FlexAI credentials:

```env
# FlexAI Platform Configuration
FLEXAI_API_KEY=your_flexai_api_key_here
FLEXAI_API_URL=https://api.flexai.com
FLEXAI_ORG_ID=your_org_id

# Jupyter Configuration
JUPYTER_TOKEN=my_secure_token_12345
JUPYTER_PORT=8888

# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Database Configuration (PostgreSQL running in Docker)
DATABASE_URL=postgresql://flexai_user:flexai_password_local@postgres:5432/flexai_notebook_db

# Redis Configuration (running in Docker)
REDIS_URL=redis://redis:6379

# Security - Auto-generated secure keys for local testing
SECRET_KEY=local_dev_secret_key_change_in_production_f8e7d6c5b4a39281
JWT_SECRET_KEY=jwt_local_secret_7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:8888,http://localhost:3000,http://127.0.0.1:8888

# Logging
LOG_LEVEL=INFO

# Feature Flags
MOCK_MODE=true
ENABLE_METRICS=false
ENABLE_TELEMETRY=false

# Session Configuration
SESSION_TIMEOUT_MINUTES=60
MAX_CONCURRENT_SESSIONS=10
```

### Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLEXAI_API_KEY` | Your FlexAI API key | - | ✅ Yes |
| `FLEXAI_API_URL` | FlexAI API endpoint | `https://api.flexai.com` | ✅ Yes |
| `FLEXAI_ORG_ID` | Your organization ID | - | ✅ Yes |
| `JUPYTER_TOKEN` | Jupyter access token | - | ✅ Yes |
| `SECRET_KEY` | JWT signing key | - | ✅ Yes |
| `JUPYTER_PORT` | Jupyter port | `8888` | ❌ No |
| `API_PORT` | Backend API port | `8000` | ❌ No |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ No |

## Usage Guide

### Selecting GPU Resources

1. **Open a Notebook:**
   - Navigate to http://localhost:8888
   - Open any notebook or create a new one

2. **Click "FlexAI Compute" Button:**
   - Located in the Jupyter toolbar
   - Shows current GPU status if already provisioned

3. **Choose GPU Configuration:**
   - View available GPU types with specifications:
     - **NVIDIA Tesla T4** - 16GB, $0.50/hour
     - **NVIDIA Tesla V100** - 32GB, $2.00/hour
     - **NVIDIA A100** - 40GB, $3.50/hour
     - **NVIDIA H100** - 80GB, $5.00/hour
   - Select number of GPUs (1, 2, 4, or 8)

4. **Wait for Provisioning:**
   - Status messages show provisioning progress
   - Usually completes in 30-60 seconds

5. **Start Coding:**
   - GPUs are now available to your notebook
   - Use PyTorch, TensorFlow, JAX, or any ML framework

### Example: PyTorch with GPU

```python
import torch

# Check GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
print(f"GPU Name: {torch.cuda.get_device_name(0)}")
print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# Create a tensor on GPU
x = torch.randn(1000, 1000).to(device)
y = torch.randn(1000, 1000).to(device)
z = torch.matmul(x, y)

print(f"Result shape: {z.shape}")
```

### Example: TensorFlow with GPU

```python
import tensorflow as tf

# Check GPU availability
print("GPUs Available:", len(tf.config.list_physical_devices('GPU')))

# Simple computation on GPU
with tf.device('/GPU:0'):
    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
    b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
    c = tf.matmul(a, b)
    print("Result:", c)
```

### Managing Sessions

Sessions are automatically created when you select GPU resources and persist across notebook restarts.

**Session Auto-Cleanup:**
- Sessions expire after 24 hours of inactivity
- Stopped instances are automatically cleaned up
- You can manually stop instances via the API

## Supported ML Frameworks

This platform comes pre-installed with:

- **PyTorch** 2.1.2 - Deep learning framework
- **TensorFlow** 2.15.0 - End-to-end ML platform
- **JAX** 0.4.23 - High-performance numerical computing
- **scikit-learn** 1.3.2 - Machine learning library
- **NumPy** 1.26.3 - Numerical computing
- **Pandas** 2.1.4 - Data analysis
- **XGBoost** - Gradient boosting
- Any other Python-based ML framework (installable via pip)

All frameworks are configured to automatically detect and use FlexAI GPU resources.

## Project Structure

```
flexai-notebook/
├── backend/                     # Backend API server
│   ├── main.py                 # FastAPI application (REST API)
│   ├── flexai_client.py        # FlexAI platform client
│   ├── session_manager.py      # Session and resource management
│   └── __init__.py             # Package initialization
├── frontend/                    # Jupyter frontend extensions
│   ├── extension/              # Custom Jupyter extensions
│   │   ├── flexai_compute.js   # JavaScript UI extension
│   │   └── flexai_compute.py   # Python server extension
│   └── static/                 # Static web assets
│       └── custom.css          # Custom Jupyter styles
├── notebooks/                   # Sample notebooks
│   ├── getting_started.ipynb           # Quick start guide
│   └── pytorch_image_classification.ipynb  # PyTorch example
├── docker/                      # Docker configurations
│   ├── Dockerfile.backend      # Backend container
│   └── Dockerfile.jupyter      # Jupyter container
├── tests/                       # Test suite (unit & integration)
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Multi-container orchestration
├── requirements.txt             # Python dependencies
├── start.sh                     # Startup script
├── stop.sh                      # Shutdown script
├── README.md                    # This file
├── DEVELOPMENT.md               # Development guide
└── FLEXAI_INTEGRATION.md        # FlexAI integration guide
```

## Development

### Running Locally Without Docker

For development purposes, you can run the services locally:

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start Redis (required for session management):**
```bash
# macOS
brew install redis
redis-server

# Linux
sudo apt-get install redis-server
redis-server
```

3. **Start the backend API:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

4. **Start Jupyter Notebook:**
```bash
export BACKEND_API_URL=http://localhost:8000
jupyter notebook --NotebookApp.token='your_token' --port 8888
```

5. **Install Jupyter extension:**
```bash
jupyter nbextension install frontend/extension/ --sys-prefix
jupyter nbextension enable flexai_compute/flexai_compute --sys-prefix
```

### Adding New Features

- **Add New GPU Type:** Update FlexAI API - frontend auto-displays it
- **Add Authentication:** Implement JWT middleware in backend
- **Customize UI:** Edit JS/CSS files and rebuild containers

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Test API manually
curl http://localhost:8000/health
curl http://localhost:8000/api/compute/available
```

For detailed development guide, see **[DEVELOPMENT.md](DEVELOPMENT.md)**

## Troubleshooting

### Common Issues

**Jupyter Can't Connect to Backend:**
- Check: `docker logs flexai-backend`
- Verify: `curl http://localhost:8000/health`
- Check CORS settings in `.env`

**GPU Not Available:**
- Verify provisioning status in UI
- Check FlexAI credentials in `.env`
- Review backend logs for errors

**Extension Not Loading:**
- Check: `docker logs flexai-jupyter`
- Clear browser cache and reload
- Rebuild: `docker-compose up --build jupyter`

**Docker Issues:**
- Check logs: `docker-compose logs`
- Ensure ports 8000, 8888, 6379 are free
- Clean up: `docker-compose down -v`

### Getting Help

```bash
# View all logs
docker-compose logs

# Check service status
docker-compose ps

# Access container shell
docker exec -it flexai-backend bash
```

## Security Best Practices

**Production Checklist:**
- ✅ Never commit `.env` file
- ✅ Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- ✅ Enable HTTPS with SSL certificates
- ✅ Implement rate limiting
- ✅ Add user authentication (JWT/OAuth2)
- ✅ Restrict CORS origins
- ✅ Regular security updates
- ✅ Enable audit logging

## Contributing

We welcome contributions!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pytest tests/`
5. Format code: `black .`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open Pull Request

## Roadmap

- [ ] Multi-user authentication
- [ ] Notebook collaboration
- [ ] Cost tracking and budgeting
- [ ] GPU scheduling and queuing
- [ ] MLflow integration
- [ ] Kubernetes operator
- [ ] VS Code extension
- [ ] Mobile monitoring app

## API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

The API uses API key authentication via headers:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "X-Organization-ID: YOUR_ORG_ID" \
     http://localhost:8000/api/compute/available
```

### Endpoints Reference

#### Health Check

**GET /** or **GET /health**

Check API health status.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

#### List Available GPUs

**GET /api/compute/available**

Get list of available GPU types from FlexAI.

```bash
curl http://localhost:8000/api/compute/available
```

Response:
```json
[
  {
    "id": "nvidia-a100",
    "name": "NVIDIA A100",
    "memory": "40GB",
    "compute_capability": "8.0",
    "price_per_hour": 3.5,
    "available": true
  }
]
```

#### Select and Provision Compute

**POST /api/compute/select**

Select GPU configuration and provision compute instance.

Request Body:
```json
{
  "gpu_type": "nvidia-a100",
  "gpu_count": 2,
  "session_id": null,
  "user_id": "user123"
}
```

```bash
curl -X POST http://localhost:8000/api/compute/select \
  -H "Content-Type: application/json" \
  -d '{
    "gpu_type": "nvidia-a100",
    "gpu_count": 2,
    "user_id": "user123"
  }'
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "instance_id": "inst-abc123",
  "status": "active",
  "message": "Successfully provisioned nvidia-a100 x2"
}
```

#### Get Instance Status

**GET /api/compute/instance/{instance_id}**

Get the status of a compute instance.

```bash
curl http://localhost:8000/api/compute/instance/inst-abc123
```

Response:
```json
{
  "instance_id": "inst-abc123",
  "gpu_type": "nvidia-a100",
  "gpu_count": 2,
  "cpu_cores": 8,
  "ram_gb": 32,
  "status": "running",
  "ip_address": "192.168.1.100"
}
```

#### Stop Instance

**POST /api/compute/instance/{instance_id}/stop**

Stop a running compute instance.

```bash
curl -X POST http://localhost:8000/api/compute/instance/inst-abc123/stop
```

Response:
```json
{
  "message": "Instance stopped successfully"
}
```

#### Create Session

**POST /api/sessions/create**

Create a new user session.

```bash
curl -X POST "http://localhost:8000/api/sessions/create?user_id=user123"
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "instance_id": null,
  "gpu_type": null,
  "gpu_count": 0,
  "status": "created"
}
```

#### Get Session Details

**GET /api/sessions/{session_id}**

Get session details.

```bash
curl http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000
```

#### Delete Session

**DELETE /api/sessions/{session_id}**

Delete a session and associated compute resources.

```bash
curl -X DELETE http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000
```

#### Extend Session

**POST /api/sessions/{session_id}/extend**

Extend session expiration by specified hours.

```bash
curl -X POST "http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000/extend?hours=2"
```

### Interactive API Documentation

The API documentation is available at **http://localhost:8000/docs** when the server is running.

Access the interactive Swagger UI documentation:
```
http://localhost:8000/docs
```

Or ReDoc format:
```
http://localhost:8000/redoc
```

## FlexAI Integration

### Required FlexAI API Endpoints

Your FlexAI platform must implement these REST API endpoints:

#### 1. List GPU Types
```
GET /v1/compute/gpu-types
```
Returns available GPU configurations.

#### 2. Provision Instance
```
POST /v1/compute/instances
```
Creates and provisions a new compute instance.

#### 3. Get Instance Status
```
GET /v1/compute/instances/{instance_id}
```
Returns current status of an instance.

#### 4. Stop Instance
```
POST /v1/compute/instances/{instance_id}/stop
```
Stops a running instance.

#### 5. Delete Instance
```
DELETE /v1/compute/instances/{instance_id}
```
Deletes an instance and releases resources.

### Customizing FlexAI Client

If your API structure differs, edit `backend/flexai_client.py`:

```python
class FlexAIClient:
    async def get_available_gpus(self) -> List[GPUType]:
        # Customize this method to match your API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/your/custom/endpoint",
                headers=self.headers
            )
            # Parse and return GPU types
            return parsed_gpu_types
```

### Integration Architecture

**Recommended: Hybrid Architecture**
- Flexible and scalable
- Good separation of concerns
- Proper resource management
- Centralized Jupyter with remote GPU access

For detailed integration guide, see **[FLEXAI_INTEGRATION.md](FLEXAI_INTEGRATION.md)**

## License

MIT License

Copyright (c) 2026 FlexAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- Inspired by Google Colab
- Built with FastAPI, Jupyter, and Docker
- Powered by FlexAI compute platform

## Support

For issues and questions:

- **Documentation:** [README.md](README.md), [DEVELOPMENT.md](DEVELOPMENT.md), [FLEXAI_INTEGRATION.md](FLEXAI_INTEGRATION.md)
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:** Open an issue in this repository
- **FlexAI Support:** Contact FlexAI support for platform-specific issues
- **Email:** support@flexai.com

---

**Built with ❤️ for the ML community**
