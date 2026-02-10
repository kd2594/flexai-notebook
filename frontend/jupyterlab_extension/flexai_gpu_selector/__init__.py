"""
FlexAI GPU Selector - JupyterLab Extension
A JupyterLab extension that adds GPU selection UI to notebooks
"""
from .handlers import setup_handlers

__version__ = "0.1.0"


def _jupyter_labextension_paths():
    """Required for JupyterLab extension discovery"""
    return [{
        "src": "labextension",
        "dest": "flexai-gpu-selector"
    }]


def _jupyter_server_extension_points():
    """Register the server extension"""
    return [{"module": "flexai_gpu_selector"}]


def _load_jupyter_server_extension(server_app):
    """Load the server extension"""
    setup_handlers(server_app.web_app)
    server_app.log.info("FlexAI GPU Selector extension loaded!")
