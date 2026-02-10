"""
FlexAI GPU Selector - Google Colab Style UI
Professional modal dialog for GPU selection in JupyterLab
"""

from IPython.display import display, HTML, Javascript
import httpx
import asyncio
from typing import List, Dict
import json


class FlexAIGPUSelector:
    """
    Google Colab-style GPU selector with modal dialog
    """
    
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.gpu_types = []
    
    async def fetch_gpu_types(self) -> List[Dict]:
        """Fetch available GPU types from backend"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/compute/available",
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"⚠️ Could not fetch GPUs from backend: {e}")
            # Return fallback GPUs
            return [
                {"id": "nvidia-t4", "name": "NVIDIA T4", "memory": "16GB", "price_per_hour": 0.35, "available": True},
                {"id": "nvidia-v100", "name": "NVIDIA V100", "memory": "32GB", "price_per_hour": 2.48, "available": True},
                {"id": "nvidia-a100-40gb", "name": "NVIDIA A100-40GB", "memory": "40GB", "price_per_hour": 3.09, "available": True},
                {"id": "nvidia-a100-80gb", "name": "NVIDIA A100-80GB", "memory": "80GB", "price_per_hour": 3.67, "available": True},
                {"id": "nvidia-h100", "name": "NVIDIA H100", "memory": "80GB", "price_per_hour": 4.76, "available": True},
                {"id": "nvidia-l4", "name": "NVIDIA L4", "memory": "24GB", "price_per_hour": 0.61, "available": True}
            ]
    
    def show(self):
        """Display the Google Colab-style GPU selector"""
        # Fetch GPU types synchronously
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        gpu_types = loop.run_until_complete(self.fetch_gpu_types())
        
        # Generate GPU options HTML
        gpu_options_html = self._generate_gpu_options(gpu_types)
        
        # Create the complete UI
        html = f"""
        <style>
            /* Modal overlay */
            #flexai-modal-overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 10000;
                justify-content: center;
                align-items: center;
                backdrop-filter: blur(2px);
            }}
            
            #flexai-modal-overlay.show {{
                display: flex !important;
            }}
            
            /* Modal dialog */
            .flexai-modal {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                max-width: 580px;
                width: 90%;
                max-height: 80vh;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                animation: modalSlideIn 0.3s ease-out;
            }}
            
            @keyframes modalSlideIn {{
                from {{
                    transform: translateY(-50px);
                    opacity: 0;
                }}
                to {{
                    transform: translateY(0);
                    opacity: 1;
                }}
            }}
            
            /* Modal header */
            .flexai-modal-header {{
                padding: 20px 24px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .flexai-modal-title {{
                font-size: 18px;
                font-weight: 500;
                color: #202124;
                margin: 0;
            }}
            
            .flexai-modal-close {{
                background: none;
                border: none;
                font-size: 24px;
                color: #5f6368;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s;
            }}
            
            .flexai-modal-close:hover {{
                background: #f1f3f4;
            }}
            
            /* Modal body */
            .flexai-modal-body {{
                padding: 24px;
                overflow-y: auto;
                flex: 1;
            }}
            
            .flexai-section {{
                margin-bottom: 24px;
            }}
            
            .flexai-section-title {{
                font-size: 13px;
                font-weight: 500;
                color: #5f6368;
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
            }}
            
            .flexai-section-title::before {{
                content: '⚙️';
                margin-right: 8px;
            }}
            
            /* GPU options */
            .flexai-gpu-option {{
                display: flex;
                align-items: center;
                padding: 14px 16px;
                margin-bottom: 10px;
                border: 2px solid #dadce0;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s ease;
                background: white;
            }}
            
            .flexai-gpu-option:hover {{
                border-color: #1a73e8;
                background: #f8f9fa;
                transform: translateX(2px);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .flexai-gpu-option.selected {{
                border-color: #1a73e8;
                background: #e8f0fe;
                border-width: 2px;
                box-shadow: 0 2px 8px rgba(26,115,232,0.15);
            }}
            
            .flexai-gpu-radio {{
                width: 20px;
                height: 20px;
                margin-right: 14px;
                cursor: pointer;
                accent-color: #1a73e8;
            }}
            
            .flexai-gpu-info {{
                flex: 1;
            }}
            
            .flexai-gpu-name {{
                font-size: 14px;
                font-weight: 500;
                color: #202124;
                margin-bottom: 3px;
            }}
            
            .flexai-gpu-specs {{
                font-size: 12px;
                color: #5f6368;
            }}
            
            .flexai-gpu-price {{
                font-size: 14px;
                font-weight: 600;
                color: #1a73e8;
                margin-left: 12px;
            }}
            
            .flexai-gpu-price.free {{
                color: #0f9d58;
            }}
            
            /* Info banners */
            .flexai-info-banner {{
                background: #e8f0fe;
                border-left: 4px solid #1a73e8;
                padding: 12px 16px;
                border-radius: 4px;
                font-size: 13px;
                color: #1967d2;
                margin-top: 16px;
                display: flex;
                align-items: flex-start;
            }}
            
            .flexai-info-banner::before {{
                content: 'ℹ️';
                margin-right: 10px;
                font-size: 16px;
            }}
            
            .flexai-premium-notice {{
                background: #fef7e0;
                border-left: 4px solid #f9ab00;
                padding: 12px 16px;
                border-radius: 4px;
                font-size: 12px;
                color: #b85600;
                margin-top: 12px;
                display: flex;
                align-items: flex-start;
            }}
            
            .flexai-premium-notice::before {{
                content: '💡';
                margin-right: 10px;
                font-size: 14px;
            }}
            
            /* Modal footer */
            .flexai-modal-footer {{
                padding: 16px 24px;
                border-top: 1px solid #e0e0e0;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }}
            
            .flexai-btn {{
                padding: 10px 24px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                border: none;
                font-family: inherit;
            }}
            
            .flexai-btn-cancel {{
                background: white;
                color: #1a73e8;
                border: 1px solid #dadce0;
            }}
            
            .flexai-btn-cancel:hover {{
                background: #f8f9fa;
            }}
            
            .flexai-btn-save {{
                background: #1a73e8;
                color: white;
            }}
            
            .flexai-btn-save:hover {{
                background: #1765cc;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }}
            
            .flexai-btn-save:active {{
                background: #1557b0;
            }}
            
            /* Status message */
            #flexai-status {{
                margin-top: 16px;
                padding: 12px 16px;
                border-radius: 6px;
                font-size: 13px;
                display: none;
            }}
            
            #flexai-status.success {{
                background: #e6f4ea;
                border-left: 4px solid #0f9d58;
                color: #137333;
                display: block;
            }}
            
            #flexai-status.error {{
                background: #fce8e6;
                border-left: 4px solid #d93025;
                color: #c5221f;
                display: block;
            }}
            
            #flexai-status.loading {{
                background: #e8f0fe;
                border-left: 4px solid #1a73e8;
                color: #1967d2;
                display: block;
            }}
            
            /* Button to open modal */
            .flexai-open-btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                transition: all 0.3s ease;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }}
            
            .flexai-open-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
            }}
            
            .flexai-open-btn::before {{
                content: '🚀';
                font-size: 18px;
            }}
        </style>
        
        <!-- Trigger Button -->
        <div style="margin: 20px 0;">
            <button class="flexai-open-btn" onclick="openFlexAIModal()">
                Change Runtime Type
            </button>
        </div>
        
        <!-- Modal -->
        <div id="flexai-modal-overlay">
            <div class="flexai-modal">
                <div class="flexai-modal-header">
                    <h2 class="flexai-modal-title">Change Runtime Type</h2>
                    <button class="flexai-modal-close" onclick="closeFlexAIModal()">×</button>
                </div>
                
                <div class="flexai-modal-body">
                    <div class="flexai-section">
                        <div class="flexai-section-title">Hardware Accelerator</div>
                        
                        <div class="flexai-gpu-option selected" data-gpu="CPU" onclick="selectFlexAIGPU('CPU', this)">
                            <input type="radio" name="flexai-gpu" value="CPU" class="flexai-gpu-radio" checked>
                            <div class="flexai-gpu-info">
                                <div class="flexai-gpu-name">💻 CPU</div>
                                <div class="flexai-gpu-specs">Standard compute without acceleration</div>
                            </div>
                            <div class="flexai-gpu-price free">Free</div>
                        </div>
                        
                        {gpu_options_html}
                    </div>
                    
                    <div class="flexai-info-banner">
                        <div>Running in <strong>Mock Mode</strong> - Instant provisioning for testing</div>
                    </div>
                    
                    <div class="flexai-premium-notice">
                        <div>GPU provisioning is simulated in the current setup. No actual costs incurred.</div>
                    </div>
                    
                    <div id="flexai-status"></div>
                </div>
                
                <div class="flexai-modal-footer">
                    <button class="flexai-btn flexai-btn-cancel" onclick="closeFlexAIModal()">Cancel</button>
                    <button class="flexai-btn flexai-btn-save" onclick="saveFlexAIGPU()">Save</button>
                </div>
            </div>
        </div>
        
        <script>
            let selectedFlexAIGPU = 'CPU';
            
            function openFlexAIModal() {{
                document.getElementById('flexai-modal-overlay').classList.add('show');
            }}
            
            function closeFlexAIModal() {{
                document.getElementById('flexai-modal-overlay').classList.remove('show');
            }}
            
            function selectFlexAIGPU(gpu, element) {{
                selectedFlexAIGPU = gpu;
                
                // Update UI
                document.querySelectorAll('.flexai-gpu-option').forEach(opt => {{
                    opt.classList.remove('selected');
                }});
                element.classList.add('selected');
                
                // Update radio
                document.querySelectorAll('input[name="flexai-gpu"]').forEach(radio => {{
                    radio.checked = radio.value === gpu;
                }});
            }}
            
            async function saveFlexAIGPU() {{
                const statusDiv = document.getElementById('flexai-status');
                statusDiv.className = 'loading';
                statusDiv.innerHTML = '⏳ Provisioning ' + selectedFlexAIGPU + '...';
                
                try {{
                    const backendUrl = window.location.protocol + '//' + window.location.hostname + ':8000';
                    const response = await fetch(backendUrl + '/api/compute/instances', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{gpu_type: selectedFlexAIGPU, gpu_count: 1}})
                    }});
                    
                    if (!response.ok) {{
                        throw new Error('HTTP ' + response.status);
                    }}
                    
                    const result = await response.json();
                    
                    statusDiv.className = 'success';
                    statusDiv.innerHTML = '✅ Successfully provisioned ' + selectedFlexAIGPU + '!<br><small>Your notebook is now using this compute resource.</small>';
                    
                    setTimeout(() => {{
                        closeFlexAIModal();
                        statusDiv.style.display = 'none';
                    }}, 2000);
                    
                }} catch (error) {{
                    statusDiv.className = 'error';
                    statusDiv.innerHTML = '❌ Error: ' + error.message + '<br><small>Please check backend connection.</small>';
                }}
            }}
            
            // Close modal on overlay click
            document.getElementById('flexai-modal-overlay').addEventListener('click', function(e) {{
                if (e.target === this) {{
                    closeFlexAIModal();
                }}
            }});
            
            // Close modal on Escape key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    closeFlexAIModal();
                }}
            }});
        </script>
        """
        
        display(HTML(html))
    
    def _generate_gpu_options(self, gpu_types: List[Dict]) -> str:
        """Generate HTML for GPU options"""
        html_parts = []
        
        for gpu in gpu_types:
            if gpu.get('available', True):
                gpu_id = gpu.get('id', gpu.get('name', 'unknown'))
                gpu_name = gpu.get('name', 'Unknown GPU')
                gpu_memory = gpu.get('memory', 'N/A')
                gpu_price = gpu.get('price_per_hour', 0)
                
                html_parts.append(f"""
                    <div class="flexai-gpu-option" data-gpu="{gpu_id}" onclick="selectFlexAIGPU('{gpu_id}', this)">
                        <input type="radio" name="flexai-gpu" value="{gpu_id}" class="flexai-gpu-radio">
                        <div class="flexai-gpu-info">
                            <div class="flexai-gpu-name">🚀 {gpu_name}</div>
                            <div class="flexai-gpu-specs">{gpu_memory} VRAM</div>
                        </div>
                        <div class="flexai-gpu-price">${gpu_price:.2f}/hr</div>
                    </div>
                """)
        
        return '\n'.join(html_parts)


def show_gpu_selector(backend_url="http://localhost:8000"):
    """
    Display Google Colab-style GPU selector
    
    Usage:
        from flexai_gpu_selector_pro import show_gpu_selector
        show_gpu_selector()
    """
    selector = FlexAIGPUSelector(backend_url=backend_url)
    selector.show()


# IPython magic command
try:
    from IPython.core.magic import register_line_magic
    
    @register_line_magic
    def flexai(line):
        """
        IPython magic command for FlexAI GPU selector
        Usage: %flexai
        """
        show_gpu_selector()
    
    del flexai  # Remove from namespace, only available as magic
except ImportError:
    pass
