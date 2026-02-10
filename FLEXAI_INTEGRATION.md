# FlexAI Platform Integration Guide

This guide explains how to integrate your existing FlexAI compute platform with this Jupyter Notebook system.

## Overview

The notebook platform communicates with FlexAI through a REST API. You need to implement the FlexAI API endpoints or modify the `backend/flexai_client.py` to work with your existing API.

## FlexAI API Requirements

### Authentication

The client expects an API key and organization ID:

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "X-Organization-ID": org_id
}
```

### Required Endpoints

#### 1. List Available GPU Types

**Endpoint:** `GET /v1/compute/gpu-types`

**Response:**
```json
{
  "gpu_types": [
    {
      "id": "nvidia-a100",
      "name": "NVIDIA A100",
      "memory": "40GB",
      "compute_capability": "8.0",
      "price_per_hour": 3.50,
      "available": true
    }
  ]
}
```

#### 2. Provision Instance

**Endpoint:** `POST /v1/compute/instances`

**Request:**
```json
{
  "gpu_type": "nvidia-a100",
  "gpu_count": 2,
  "cpu_cores": 8,
  "ram_gb": 32,
  "user_id": "user-123",
  "environment": "jupyter",
  "frameworks": ["pytorch", "tensorflow"]
}
```

**Response:**
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

#### 3. Get Instance Status

**Endpoint:** `GET /v1/compute/instances/{instance_id}`

**Response:**
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

#### 4. Stop Instance

**Endpoint:** `POST /v1/compute/instances/{instance_id}/stop`

**Response:**
```json
{
  "success": true,
  "message": "Instance stopped"
}
```

#### 5. Delete Instance

**Endpoint:** `DELETE /v1/compute/instances/{instance_id}`

**Response:**
```json
{
  "success": true,
  "message": "Instance deleted"
}
```

## Customizing the Client

If your FlexAI API differs from the above, modify `backend/flexai_client.py`:

```python
class FlexAIClient:
    async def get_available_gpus(self) -> List[GPUType]:
        # Customize this method to match your API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/your/endpoint",
                headers=self.headers
            )
            # Parse and return GPU types
```

## Connecting Jupyter to Provisioned GPUs

### Option 1: Remote Kernel

Configure Jupyter to connect to the provisioned instance as a remote kernel:

1. Install Jupyter on the compute instance
2. Configure SSH tunneling
3. Update kernel spec with remote connection details

### Option 2: Environment Variables

Set environment variables that ML frameworks can detect:

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'  # Use GPUs 0 and 1
```

### Option 3: Direct CUDA Access

If the Jupyter container runs on the compute instance, CUDA should be automatically available.

## Testing the Integration

1. Update `.env` with your FlexAI credentials:
   ```env
   FLEXAI_API_KEY=your_actual_api_key
   FLEXAI_API_URL=https://your-flexai-api.com
   FLEXAI_ORG_ID=your_org_id
   ```

2. Start the platform:
   ```bash
   ./start.sh
   ```

3. Test API connection:
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
        http://localhost:8000/api/compute/available
   ```

4. In Jupyter:
   - Click FlexAI Compute button
   - Select a GPU
   - Verify provisioning in logs

## Architecture Options

### Option A: Jupyter on Compute Instance

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │─────▶│  Backend API │─────▶│  FlexAI API     │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │                       │
                            │                       ▼
                            │                ┌─────────────────┐
                            │                │ Compute Instance│
                            └───────────────▶│   + Jupyter     │
                                             └─────────────────┘
```

**Pros:** Direct GPU access, low latency
**Cons:** Need to deploy Jupyter on each instance

### Option B: Remote Kernel

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │─────▶│   Jupyter    │      │  FlexAI API     │
└─────────────┘      │  (Frontend)  │      └─────────────────┘
                     └──────────────┘             │
                            │                     ▼
                            │              ┌─────────────────┐
                            │              │ Compute Instance│
                            └─────────────▶│  (Remote Kernel)│
                                 SSH       └─────────────────┘
```

**Pros:** Centralized Jupyter, easier management
**Cons:** SSH overhead, more complex setup

### Option C: Hybrid (Recommended)

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │─────▶│   Jupyter    │      │  Backend API    │
└─────────────┘      │  (Container) │      └─────────────────┘
                     └──────────────┘             │
                            │                     ▼
                            │              ┌─────────────────┐
                            └─────────────▶│  FlexAI API     │
                                           └─────────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────────┐
                                           │ Compute Instance│
                                           │  (GPU Access)   │
                                           └─────────────────┘
```

**Pros:** Flexible, scalable, good separation of concerns
**Cons:** Requires proper networking setup

## Monitoring and Logging

Add monitoring to track:

- Instance provisioning time
- GPU utilization
- User sessions
- API response times
- Errors and failures

Example with Prometheus:

```python
from prometheus_client import Counter, Histogram

provision_requests = Counter('flexai_provision_requests_total', 'Total provision requests')
provision_duration = Histogram('flexai_provision_duration_seconds', 'Provision duration')

@provision_duration.time()
async def provision_instance(...):
    provision_requests.inc()
    # ... provisioning code
```

## Support

For issues with FlexAI integration:

1. Check backend logs: `docker logs flexai-backend`
2. Verify API credentials
3. Test API endpoints directly with curl
4. Contact FlexAI support for API issues
