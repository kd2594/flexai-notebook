"""
FlexAI Compute Extension for JupyterLab
This is the Python server extension that bridges Jupyter and FlexAI backend
"""
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import json
import os
import httpx


class FlexAIComputeHandler(IPythonHandler):
    """Handler for FlexAI compute requests"""
    
    async def get(self):
        """Get available GPU types"""
        backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{backend_url}/api/compute/available")
                response.raise_for_status()
                self.finish(response.json())
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
    
    async def post(self):
        """Select GPU and provision compute"""
        backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        data = json.loads(self.request.body)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{backend_url}/api/compute/select",
                    json=data
                )
                response.raise_for_status()
                self.finish(response.json())
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


def load_jupyter_server_extension(nb_app):
    """Load the Jupyter server extension"""
    web_app = nb_app.web_app
    host_pattern = '.*$'
    
    route_pattern = url_path_join(
        web_app.settings['base_url'],
        '/flexai/compute'
    )
    
    web_app.add_handlers(host_pattern, [(route_pattern, FlexAIComputeHandler)])
    nb_app.log.info("FlexAI Compute extension loaded")
