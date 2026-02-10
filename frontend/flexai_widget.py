"""
FlexAI GPU Selector Widget for Jupyter
Simple widget that displays GPU selection UI directly in notebooks
"""
import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
import httpx
import asyncio
from typing import List, Dict


class FlexAIGPUSelector:
    """GPU Selection Widget for FlexAI"""
    
    def __init__(self, backend_url="http://backend:8000"):
        self.backend_url = backend_url
        self.gpu_types = []
        self.selected_gpu = None
        self.output = widgets.Output()
        
    async def fetch_gpu_types(self):
        """Fetch available GPU types from backend"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/api/compute/available", timeout=5.0)
                response.raise_for_status()
                self.gpu_types = response.json()
                return self.gpu_types
        except Exception as e:
            print(f"Error fetching GPU types: {e}")
            return []
    
    async def select_gpu(self, gpu_type):
        """Select and provision a GPU"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/compute/instances",
                    json={"gpu_type": gpu_type, "gpu_count": 1},
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                self.selected_gpu = gpu_type
                return result
        except Exception as e:
            print(f"Error selecting GPU: {e}")
            return None
    
    def create_gpu_card(self, gpu):
        """Create HTML card for GPU option"""
        gpu_name = gpu.get('name', gpu.get('type', 'Unknown'))
        gpu_memory = gpu.get('memory', 'N/A')
        gpu_price = gpu.get('price_per_hour', 0)
        gpu_type = gpu.get('id', gpu.get('type', gpu_name))
        
        return f"""
        <div class="gpu-card" style="
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: all 0.3s;
        " onclick="selectGPU('{gpu_type}')">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 16px;">{gpu_name}</strong>
                    <div style="color: #666; font-size: 14px;">{gpu_memory}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 16px; color: #28a745;">${gpu_price}/hr</div>
                </div>
            </div>
        </div>
        """
    
    def show(self):
        """Display the GPU selector widget"""
        # Fetch GPU types
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a task
            import nest_asyncio
            nest_asyncio.apply()
        
        gpu_types = loop.run_until_complete(self.fetch_gpu_types())
        
        # Create HTML UI
        html_content = """
        <style>
            .flexai-gpu-selector {
                background: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .gpu-card:hover {
                border-color: #28a745 !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transform: translateY(-2px);
            }
            .flexai-header {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #333;
            }
            .flexai-subtitle {
                color: #666;
                margin-bottom: 20px;
            }
        </style>
        
        <div class="flexai-gpu-selector">
            <div class="flexai-header">🚀 Select FlexAI Compute</div>
            <div class="flexai-subtitle">Choose your hardware accelerator</div>
            
            <!-- CPU Option -->
            <div class="gpu-card" style="
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s;
                background: #f8f9fa;
            " onclick="selectGPU('CPU')">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 16px;">💻 CPU Only</strong>
                        <div style="color: #666; font-size: 14px;">Standard compute without acceleration</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 16px; color: #28a745;">$0.00/hr</div>
                    </div>
                </div>
            </div>
        """
        
        # Add GPU options
        for gpu in gpu_types:
            if gpu.get('available', True):  # Only show available GPUs
                html_content += self.create_gpu_card(gpu)
        
        html_content += """
            <div id="gpu-status" style="
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                display: none;
                background: #e7f3ff;
                border: 1px solid #2196F3;
            "></div>
        </div>
        
        <script>
        async function selectGPU(gpuType) {
            const statusDiv = document.getElementById('gpu-status');
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = '<strong>⏳ Provisioning ' + gpuType + '...</strong>';
            statusDiv.style.background = '#fff3cd';
            statusDiv.style.borderColor = '#ffc107';
            
            try {
                // Use relative URL or construct from window.location
                const backendUrl = window.location.protocol + '//' + window.location.hostname + ':8000';
                const response = await fetch(backendUrl + '/api/compute/instances', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gpu_type: gpuType, gpu_count: 1})
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = '<strong>✅ Successfully provisioned ' + gpuType + '!</strong><br>' +
                                        '<small>Your notebook is now using this compute resource.</small>';
                    statusDiv.style.background = '#d4edda';
                    statusDiv.style.borderColor = '#28a745';
                } else {
                    throw new Error(result.message || 'Failed to provision');
                }
            } catch (error) {
                statusDiv.innerHTML = '<strong>❌ Error:</strong> ' + error.message;
                statusDiv.style.background = '#f8d7da';
                statusDiv.style.borderColor = '#dc3545';
            }
        }
        </script>
        """
        
        display(HTML(html_content))


def show_gpu_selector(backend_url="http://backend:8000"):
    """Convenience function to display GPU selector"""
    selector = FlexAIGPUSelector(backend_url=backend_url)
    selector.show()
