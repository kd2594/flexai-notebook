"""
Mock FlexAI API Server
Simulates FlexAI compute platform responses for local development and testing
"""
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
import random
import time

app = FastAPI(
    title="Mock FlexAI API",
    description="Mock FlexAI compute platform for local testing",
    version="1.0.0"
)

# In-memory storage for mock instances
mock_instances: Dict[str, dict] = {}


# ============================================================================
# Models
# ============================================================================

class GPUTypeResponse(BaseModel):
    id: str
    name: str
    memory: str
    compute_capability: str
    price_per_hour: float
    available: bool


class CreateInstanceRequest(BaseModel):
    gpu_type: str
    gpu_count: int = 1
    cpu_cores: int = 8
    ram_gb: int = 32
    user_id: Optional[str] = None
    environment: Optional[str] = "jupyter"
    frameworks: Optional[List[str]] = []


class InstanceResponse(BaseModel):
    instance_id: str
    gpu_type: str
    gpu_count: int
    cpu_cores: int
    ram_gb: int
    status: str
    ip_address: Optional[str] = None
    created_at: float


# ============================================================================
# Mock Data
# ============================================================================

MOCK_GPU_TYPES = [
    {
        "id": "nvidia-t4",
        "name": "NVIDIA Tesla T4",
        "memory": "16GB",
        "compute_capability": "7.5",
        "price_per_hour": 0.50,
        "available": True
    },
    {
        "id": "nvidia-v100",
        "name": "NVIDIA Tesla V100",
        "memory": "32GB",
        "compute_capability": "7.0",
        "price_per_hour": 2.00,
        "available": True
    },
    {
        "id": "nvidia-a100-40gb",
        "name": "NVIDIA A100 40GB",
        "memory": "40GB",
        "compute_capability": "8.0",
        "price_per_hour": 3.50,
        "available": True
    },
    {
        "id": "nvidia-a100-80gb",
        "name": "NVIDIA A100 80GB",
        "memory": "80GB",
        "compute_capability": "8.0",
        "price_per_hour": 4.50,
        "available": True
    },
    {
        "id": "nvidia-h100",
        "name": "NVIDIA H100",
        "memory": "80GB",
        "compute_capability": "9.0",
        "price_per_hour": 5.00,
        "available": True
    },
    {
        "id": "nvidia-l4",
        "name": "NVIDIA L4",
        "memory": "24GB",
        "compute_capability": "8.9",
        "price_per_hour": 1.00,
        "available": True
    },
]


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Mock FlexAI API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/v1/compute/gpu-types")
async def get_gpu_types(
    authorization: Optional[str] = Header(None),
    x_organization_id: Optional[str] = Header(None)
):
    """Get available GPU types"""
    # Simulate API validation (but accept any values in mock mode)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    return {"gpu_types": MOCK_GPU_TYPES}


@app.post("/v1/compute/instances")
async def create_instance(
    request: CreateInstanceRequest,
    authorization: Optional[str] = Header(None),
    x_organization_id: Optional[str] = Header(None)
):
    """Provision a new compute instance"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Validate GPU type
    gpu_types = [gpu["id"] for gpu in MOCK_GPU_TYPES]
    if request.gpu_type not in gpu_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GPU type. Available types: {', '.join(gpu_types)}"
        )
    
    # Create mock instance
    instance_id = f"inst-{uuid.uuid4().hex[:12]}"
    mock_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    
    instance = {
        "instance_id": instance_id,
        "gpu_type": request.gpu_type,
        "gpu_count": request.gpu_count,
        "cpu_cores": request.cpu_cores,
        "ram_gb": request.ram_gb,
        "status": "running",  # Instantly running in mock mode
        "ip_address": mock_ip,
        "created_at": time.time()
    }
    
    mock_instances[instance_id] = instance
    
    return instance


@app.get("/v1/compute/instances/{instance_id}")
async def get_instance_status(
    instance_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get instance status"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if instance_id not in mock_instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return mock_instances[instance_id]


@app.post("/v1/compute/instances/{instance_id}/stop")
async def stop_instance(
    instance_id: str,
    authorization: Optional[str] = Header(None)
):
    """Stop a running instance"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if instance_id not in mock_instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    mock_instances[instance_id]["status"] = "stopped"
    
    return {
        "instance_id": instance_id,
        "status": "stopped",
        "message": "Instance stopped successfully"
    }


@app.delete("/v1/compute/instances/{instance_id}")
async def delete_instance(
    instance_id: str,
    authorization: Optional[str] = Header(None)
):
    """Delete an instance"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if instance_id not in mock_instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    del mock_instances[instance_id]
    
    return {
        "instance_id": instance_id,
        "message": "Instance deleted successfully"
    }


@app.get("/v1/compute/instances")
async def list_instances(
    authorization: Optional[str] = Header(None),
    x_organization_id: Optional[str] = Header(None)
):
    """List all instances"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    return {
        "instances": list(mock_instances.values()),
        "count": len(mock_instances)
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mock-flexai-api",
        "instances_count": len(mock_instances)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
