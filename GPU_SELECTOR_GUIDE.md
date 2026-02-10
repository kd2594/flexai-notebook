# FlexAI GPU Selection UI

## Overview

The FlexAI Notebook platform now includes an interactive GPU selection interface that allows you to choose your compute resources before running ML workloads.

## How to Use the GPU Selector

### Option 1: Use the GPU Selector Notebook

1. **Access Jupyter**: Open http://localhost:8888/lab?token=local_demo_token_secure_123

2. **Open the GPU Selector Notebook**: Navigate to `flexai_gpu_selector.ipynb`

3. **Run the First Cell**: This will display an interactive UI showing available GPU types:
   - 💻 CPU Only ($0.00/hr)
   - NVIDIA T4 - 16GB ($0.35/hr)
   - NVIDIA V100 - 32GB ($2.48/hr)
   - NVIDIA A100-40GB - 40GB ($3.09/hr)
   - NVIDIA A100-80GB - 80GB ($3.67/hr)
   - NVIDIA H100 - 80GB ($4.76/hr)
   - NVIDIA L4 - 24GB ($0.61/hr)

4. **Click to Select**: Click on any GPU card to provision that compute resource

5. **Confirmation**: You'll see a success message once the GPU is provisioned

### Option 2: Use the Widget in Any Notebook

You can add GPU selection to any notebook:

```python
# Add this cell at the top of any notebook
import sys
sys.path.append('/home/jovyan/.flexai')

from flexai_widget import show_gpu_selector
show_gpu_selector()
```

## UI Features

### Interactive GPU Cards
- Each GPU type is displayed in a card showing:
  - GPU name and specifications
  - Memory capacity
  - Price per hour (mock pricing)
  - Hover effects for better UX

### Real-time Status
- Shows provisioning status
- Displays success/error messages
- Updates UI based on current state

### Mock Mode
The current setup runs in **MOCK MODE**, which means:
- Instant GPU provisioning (no waiting)
- No real costs
- Full API simulation for testing

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Jupyter Notebook (flexai_gpu_selector.ipynb)           │
│ ┌─────────────────────────────────────────────────────┐│
││  GPU Selector Widget (flexai_widget.py)              ││
││  - HTML/JavaScript UI                                 ││
││  - Async HTTP client                                  ││
│└───────────────────────┬─────────────────────────────┘│
└────────────────────────┼──────────────────────────────┘
                         │ HTTP API
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Backend API (backend/main.py)                           │
│ - POST /api/compute/instances (provision GPU)           │
│ - GET /api/compute/gpu-types (list GPUs)                │
│ - GET /api/compute/instances (check status)             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Mock FlexAI API (backend/mock_flexai_server.py)         │
│ - Simulates real FlexAI compute platform                │
│ - Instant provisioning                                   │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

### GET /api/compute/gpu-types
Returns list of available GPU types:
```json
[
  {
    "type": "T4",
    "name": "NVIDIA T4",
    "memory": "16GB VRAM",
    "price_per_hour": 0.35,
    "available": true
  },
  ...
]
```

### POST /api/compute/instances
Provision a new compute instance:
```json
{
  "gpu_type": "A100-40GB",
  "gpu_count": 1
}
```

Response:
```json
{
  "status": "success",
  "message": "Successfully provisioned A100-40GB x1",
  "instance": {
    "id": "inst_abc123",
    "gpu_type": "A100-40GB",
    "status": "running"
  }
}
```

### GET /api/compute/instances
List all active instances:
```json
[
  {
    "id": "inst_abc123",
    "gpu_type": "A100-40GB",
    "status": "active"
  }
]
```

## Customization

### Change Backend URL
If your backend is on a different host:

```python
show_gpu_selector(backend_url="http://your-backend:8000")
```

### Add Custom GPU Types
Edit `backend/mock_flexai_server.py` to add more GPU types:

```python
MOCK_GPU_TYPES = [
    {
        "type": "YOUR_GPU",
        "name": "Your Custom GPU",
        "memory": "XGB VRAM",
        "price_per_hour": 1.23,
        "available": True
    },
    # ... existing GPUs
]
```

### Style Customization
The widget uses inline CSS. Modify the styles in `frontend/flexai_widget.py`:

```python
def create_gpu_card(self, gpu):
    return f"""
    <div class="gpu-card" style="
        border: 2px solid #YOUR_COLOR;
        ...
    ">
    ...
    </div>
    ```

## Troubleshooting

### Widget Doesn't Display
1. Check that the widget file exists:
   ```bash
   docker compose exec jupyter ls -la /home/jovyan/.flexai/
   ```

2. Verify nest-asyncio is installed:
   ```bash
   docker compose exec jupyter pip list | grep nest-asyncio
   ```

### Backend Connection Fails
1. Check backend is running:
   ```bash
   docker compose ps backend
   ```

2. Test backend API:
   ```bash
   curl http://localhost:8000/api/compute/gpu-types
   ```

3. Verify network connectivity from Jupyter:
   ```bash
   docker compose exec jupyter curl http://backend:8000/health
   ```

### GPU Not Provisioning
1. Check mock API is running:
   ```bash
   docker compose ps mock-flexai
   ```

2. Check backend logs:
   ```bash
   docker compose logs backend | tail -50
   ```

## Next Steps

1. **Test the UI**: Open `flexai_gpu_selector.ipynb` and try selecting different GPUs
2. **Run ML Workloads**: After selecting a GPU, open `test_ml_environment.ipynb` to test PyTorch/TensorFlow
3. **Build Your Own**: Create custom notebooks with GPU selection at the top
4. **Integrate Production**: Replace mock API with real FlexAI credentials in `.env`

## Files

- **Frontend Widget**: `frontend/flexai_widget.py` - Python widget with HTML/JS UI
- **GPU Selector Notebook**: `notebooks/flexai_gpu_selector.ipynb` - Demo notebook
- **Backend API**: `backend/main.py` - FastAPI endpoints
- **Mock API**: `backend/mock_flexai_server.py` - Simulated FlexAI platform

---

For questions or issues, check the logs with:
```bash
docker compose logs -f
```
