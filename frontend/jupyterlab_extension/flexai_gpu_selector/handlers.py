"""
HTTP Request Handlers for FlexAI GPU Selection
"""
import json
import os
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import httpx


class GPUTypesHandler(APIHandler):
    """Handler for fetching available GPU types"""
    
    @tornado.web.authenticated
    async def get(self):
        """Get available GPU types from backend"""
        backend_url = os.getenv('BACKEND_API_URL', 'http://backend:8000')
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{backend_url}/api/compute/gpu-types", timeout=5.0)
                response.raise_for_status()
                self.finish(json.dumps(response.json()))
        except Exception as e:
            self.log.error(f"Error fetching GPU types: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                "error": str(e),
                "available_gpus": []
            }))


class GPUSelectionHandler(APIHandler):
    """Handler for GPU selection and provisioning"""
    
    @tornado.web.authenticated
    async def post(self):
        """Select GPU and provision compute instance"""
        backend_url = os.getenv('BACKEND_API_URL', 'http://backend:8000')
        
        try:
            data = self.get_json_body()
            gpu_type = data.get('gpu_type', 'CPU')
            
            self.log.info(f"Provisioning GPU: {gpu_type}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{backend_url}/api/compute/instances",
                    json={"gpu_type": gpu_type},
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
            self.finish(json.dumps({
                "status": "success",
                "message": f"Successfully provisioned {gpu_type}",
                "instance": result
            }))
            
        except Exception as e:
            self.log.error(f"Error provisioning GPU: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                "status": "error",
                "message": str(e)
            }))


class GPUStatusHandler(APIHandler):
    """Handler for checking current GPU status"""
    
    @tornado.web.authenticated
    async def get(self):
        """Get current GPU allocation status"""
        backend_url = os.getenv('BACKEND_API_URL', 'http://backend:8000')
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{backend_url}/api/compute/instances", timeout=5.0)
                response.raise_for_status()
                instances = response.json()
                
            if instances:
                current_instance = instances[0]
                self.finish(json.dumps({
                    "status": "active",
                    "gpu_type": current_instance.get('gpu_type', 'Unknown'),
                    "instance_id": current_instance.get('id')
                }))
            else:
                self.finish(json.dumps({
                    "status": "none",
                    "message": "No GPU currently allocated"
                }))
                
        except Exception as e:
            self.log.error(f"Error checking GPU status: {e}")
            self.set_status(500)
            self.finish(json.dumps({
                "status": "error",
                "message": str(e)
            }))


def setup_handlers(web_app):
    """Setup the HTTP handlers"""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Register handlers
    handlers = [
        (url_path_join(base_url, "flexai", "gpu-types"), GPUTypesHandler),
        (url_path_join(base_url, "flexai", "gpu-select"), GPUSelectionHandler),
        (url_path_join(base_url, "flexai", "gpu-status"), GPUStatusHandler),
    ]
    
    web_app.add_handlers(host_pattern, handlers)
