"""
Setup script for FlexAI GPU Selector JupyterLab Extension
"""
from setuptools import setup, find_packages

setup(
    name="flexai-gpu-selector",
    version="0.1.0",
    description="FlexAI GPU selection extension for JupyterLab",
    packages=find_packages(),
    install_requires=[
        "jupyterlab>=3.0",
        "jupyter-server>=1.0",
        "httpx>=0.24.0",
        "tornado>=6.0",
    ],
    include_package_data=True,
    data_files=[
        ("etc/jupyter/jupyter_server_config.d", [
            "jupyter-config/flexai_gpu_selector.json"
        ]),
    ],
    zip_safe=False,
)
