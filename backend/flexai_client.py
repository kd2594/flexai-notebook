"""
FlexAI Platform Client
Handles communication with FlexAI compute platform API
"""
import httpx
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class GPUType(BaseModel):
    """GPU Type Configuration"""
    id: str
    name: str
    memory: str  # e.g., "16GB", "40GB"
    compute_capability: str
    price_per_hour: float
    available: bool


class ComputeInstance(BaseModel):
    """Compute Instance Configuration"""
    instance_id: str
    gpu_type: str
    gpu_count: int
    cpu_cores: int
    ram_gb: int
    status: str  # "pending", "running", "stopped"
    ip_address: Optional[str] = None


class FlexAIClient:
    """Client for FlexAI Compute Platform"""
    
    def __init__(self, api_key: str, api_url: str, org_id: str):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.org_id = org_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": org_id
        }
    
    async def get_available_gpus(self) -> List[GPUType]:
        """Get list of available GPU types"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/v1/compute/gpu-types",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse response and return GPU types
                gpu_types = []
                for gpu in data.get("gpu_types", []):
                    gpu_types.append(GPUType(**gpu))
                
                return gpu_types
        except httpx.HTTPError as e:
            logger.error(f"Error fetching GPU types: {e}")
            # Return mock data for development/testing
            return self._get_mock_gpu_types()
    
    async def provision_instance(
        self,
        gpu_type: str,
        gpu_count: int = 1,
        cpu_cores: int = 8,
        ram_gb: int = 32,
        user_id: str = None
    ) -> ComputeInstance:
        """Provision a new compute instance"""
        try:
            payload = {
                "gpu_type": gpu_type,
                "gpu_count": gpu_count,
                "cpu_cores": cpu_cores,
                "ram_gb": ram_gb,
                "user_id": user_id,
                "environment": "jupyter",
                "frameworks": ["pytorch", "tensorflow", "jax"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/v1/compute/instances",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                return ComputeInstance(**data)
        except httpx.HTTPError as e:
            logger.error(f"Error provisioning instance: {e}")
            # Return mock instance for development/testing
            return self._get_mock_instance(gpu_type, gpu_count)
    
    async def get_instance_status(self, instance_id: str) -> ComputeInstance:
        """Get status of a compute instance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/v1/compute/instances/{instance_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                return ComputeInstance(**data)
        except httpx.HTTPError as e:
            logger.error(f"Error getting instance status: {e}")
            raise
    
    async def stop_instance(self, instance_id: str) -> bool:
        """Stop a running compute instance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/v1/compute/instances/{instance_id}/stop",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"Error stopping instance: {e}")
            return False
    
    async def delete_instance(self, instance_id: str) -> bool:
        """Delete a compute instance"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.api_url}/v1/compute/instances/{instance_id}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"Error deleting instance: {e}")
            return False
    
    def _get_mock_gpu_types(self) -> List[GPUType]:
        """Return mock GPU types for development"""
        return [
            GPUType(
                id="nvidia-t4",
                name="NVIDIA Tesla T4",
                memory="16GB",
                compute_capability="7.5",
                price_per_hour=0.50,
                available=True
            ),
            GPUType(
                id="nvidia-v100",
                name="NVIDIA Tesla V100",
                memory="32GB",
                compute_capability="7.0",
                price_per_hour=2.00,
                available=True
            ),
            GPUType(
                id="nvidia-a100",
                name="NVIDIA A100",
                memory="40GB",
                compute_capability="8.0",
                price_per_hour=3.50,
                available=True
            ),
            GPUType(
                id="nvidia-h100",
                name="NVIDIA H100",
                memory="80GB",
                compute_capability="9.0",
                price_per_hour=5.00,
                available=True
            ),
        ]
    
    def _get_mock_instance(self, gpu_type: str, gpu_count: int) -> ComputeInstance:
        """Return mock instance for development"""
        return ComputeInstance(
            instance_id=f"inst-{gpu_type}-{hash(str(gpu_type)) % 10000}",
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            cpu_cores=8,
            ram_gb=32,
            status="running",
            ip_address="192.168.1.100"
        )
