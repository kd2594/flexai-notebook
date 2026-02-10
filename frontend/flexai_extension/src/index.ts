/**
 * FlexAI GPU Selector Extension
 * Provides Google Colab-style GPU selection UI for JupyterLab
 */

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { Dialog, showDialog } from '@jupyterlab/apputils';

import { ICommandPalette } from '@jupyterlab/apputils';

import { Widget } from '@lumino/widgets';

/**
 * GPU Type interface
 */
interface GPUType {
  id: string;
  name: string;
  memory: string;
  price_per_hour: number;
  available: boolean;
}

/**
 * Create the GPU selector dialog content
 */
class GPUSelectorWidget extends Widget {
  private selectedGPU: string = 'CPU';
  private gpuTypes: GPUType[] = [];

  constructor(gpuTypes: GPUType[]) {
    super();
    this.gpuTypes = gpuTypes;
    this.addClass('flexai-gpu-selector-widget');
    this.buildUI();
  }

  private buildUI(): void {
    this.node.innerHTML = `
      <style>
        .flexai-gpu-selector-widget {
          padding: 20px;
          min-width: 500px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        .gpu-section {
          margin-bottom: 24px;
        }
        
        .gpu-section-title {
          font-size: 13px;
          font-weight: 500;
          color: #5f6368;
          margin-bottom: 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .gpu-option {
          display: flex;
          align-items: center;
          padding: 12px 16px;
          margin-bottom: 8px;
          border: 1px solid #dadce0;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          background: white;
        }
        
        .gpu-option:hover {
          border-color: #1a73e8;
          background: #f8f9fa;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .gpu-option.selected {
          border-color: #1a73e8;
          background: #e8f0fe;
          border-width: 2px;
        }
        
        .gpu-radio {
          width: 20px;
          height: 20px;
          margin-right: 12px;
          cursor: pointer;
          accent-color: #1a73e8;
        }
        
        .gpu-info {
          flex: 1;
        }
        
        .gpu-name {
          font-size: 14px;
          font-weight: 500;
          color: #202124;
          margin-bottom: 2px;
        }
        
        .gpu-specs {
          font-size: 12px;
          color: #5f6368;
        }
        
        .gpu-price {
          font-size: 13px;
          font-weight: 500;
          color: #1a73e8;
          margin-left: 12px;
        }
        
        .info-banner {
          background: #e8f0fe;
          border-left: 4px solid #1a73e8;
          padding: 12px 16px;
          border-radius: 4px;
          font-size: 13px;
          color: #1967d2;
          margin-top: 16px;
        }
        
        .premium-notice {
          background: #fef7e0;
          border-left: 4px solid #f9ab00;
          padding: 12px 16px;
          border-radius: 4px;
          font-size: 12px;
          color: #b85600;
          margin-top: 12px;
        }
      </style>
      
      <div class="gpu-section">
        <div class="gpu-section-title">Hardware Accelerator</div>
        
        <div class="gpu-option selected" data-gpu="CPU">
          <input type="radio" name="gpu" value="CPU" class="gpu-radio" checked>
          <div class="gpu-info">
            <div class="gpu-name">💻 CPU</div>
            <div class="gpu-specs">Standard compute without acceleration</div>
          </div>
          <div class="gpu-price">Free</div>
        </div>
        
        ${this.gpuTypes.map(gpu => `
          <div class="gpu-option" data-gpu="${gpu.id}">
            <input type="radio" name="gpu" value="${gpu.id}" class="gpu-radio">
            <div class="gpu-info">
              <div class="gpu-name">🚀 ${gpu.name}</div>
              <div class="gpu-specs">${gpu.memory} VRAM</div>
            </div>
            <div class="gpu-price">$${gpu.price_per_hour.toFixed(2)}/hr</div>
          </div>
        `).join('')}
      </div>
      
      <div class="info-banner">
        ℹ️ Running in <strong>Mock Mode</strong> - Instant provisioning for testing
      </div>
      
      <div class="premium-notice">
        💡 GPU provisioning is simulated in the current setup. No actual costs incurred.
      </div>
    `;

    // Add event listeners
    const options = this.node.querySelectorAll('.gpu-option');
    options.forEach(option => {
      option.addEventListener('click', (e) => {
        const target = e.currentTarget as HTMLElement;
        const gpu = target.getAttribute('data-gpu') || 'CPU';
        this.selectGPU(gpu);
      });
    });

    const radios = this.node.querySelectorAll('.gpu-radio');
    radios.forEach(radio => {
      radio.addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        this.selectGPU(target.value);
      });
    });
  }

  private selectGPU(gpu: string): void {
    this.selectedGPU = gpu;
    
    // Update UI
    const options = this.node.querySelectorAll('.gpu-option');
    options.forEach(option => {
      option.classList.remove('selected');
      if (option.getAttribute('data-gpu') === gpu) {
        option.classList.add('selected');
      }
    });
    
    const radios = this.node.querySelectorAll('.gpu-radio') as NodeListOf<HTMLInputElement>;
    radios.forEach(radio => {
      radio.checked = radio.value === gpu;
    });
  }

  getSelectedGPU(): string {
    return this.selectedGPU;
  }
}

/**
 * Fetch available GPU types from backend
 */
async function fetchGPUTypes(): Promise<GPUType[]> {
  try {
    const response = await fetch('http://localhost:8000/api/compute/available');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch GPU types:', error);
    // Return default GPUs if backend is unavailable
    return [
      { id: 'nvidia-t4', name: 'NVIDIA T4', memory: '16GB', price_per_hour: 0.35, available: true },
      { id: 'nvidia-v100', name: 'NVIDIA V100', memory: '32GB', price_per_hour: 2.48, available: true },
      { id: 'nvidia-a100-40gb', name: 'NVIDIA A100-40GB', memory: '40GB', price_per_hour: 3.09, available: true },
      { id: 'nvidia-a100-80gb', name: 'NVIDIA A100-80GB', memory: '80GB', price_per_hour: 3.67, available: true }
    ];
  }
}

/**
 * Provision GPU on backend
 */
async function provisionGPU(gpuType: string): Promise<any> {
  const response = await fetch('http://localhost:8000/api/compute/instances', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gpu_type: gpuType, gpu_count: 1 })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Show GPU selector dialog
 */
async function showGPUSelector(): Promise<void> {
  // Fetch GPU types
  const gpuTypes = await fetchGPUTypes();
  
  // Create widget
  const widget = new GPUSelectorWidget(gpuTypes);
  
  // Show dialog
  const result = await showDialog({
    title: '⚙️ Change Runtime Type',
    body: widget,
    buttons: [
      Dialog.cancelButton({ label: 'Cancel' }),
      Dialog.okButton({ label: 'Save' })
    ]
  });
  
  if (result.button.accept) {
    const selectedGPU = widget.getSelectedGPU();
    
    // Show loading dialog
    const loadingWidget = new Widget();
    loadingWidget.node.innerHTML = `
      <div style="padding: 20px; text-align: center;">
        <div style="font-size: 16px; margin-bottom: 10px;">⏳ Provisioning ${selectedGPU}...</div>
        <div style="font-size: 13px; color: #5f6368;">This may take a moment</div>
      </div>
    `;
    
    const loadingDialog = new Dialog({
      title: 'Provisioning Compute',
      body: loadingWidget,
      buttons: []
    });
    
    loadingDialog.launch();
    
    try {
      // Provision GPU
      await provisionGPU(selectedGPU);
      
      loadingDialog.close();
      
      // Show success
      await showDialog({
        title: '✅ Success',
        body: `Successfully provisioned ${selectedGPU}!\n\nYour notebook is now using this compute resource.`,
        buttons: [Dialog.okButton({ label: 'OK' })]
      });
    } catch (error) {
      loadingDialog.close();
      
      // Show error
      await showDialog({
        title: '❌ Error',
        body: `Failed to provision GPU: ${error}`,
        buttons: [Dialog.okButton({ label: 'OK' })]
      });
    }
  }
}

/**
 * Initialization plugin
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@flexai/gpu-selector:plugin',
  autoStart: true,
  requires: [ICommandPalette],
  activate: (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('FlexAI GPU Selector extension activated');

    const command = 'flexai:select-gpu';

    // Add command
    app.commands.addCommand(command, {
      label: 'Select GPU / Change Runtime',
      caption: 'Select hardware accelerator for compute',
      icon: 'jp-Icon',
      execute: showGPUSelector
    });

    // Add to command palette
    palette.addItem({ command, category: 'FlexAI' });

    // Add to toolbar (optional - would need toolbar registry)
    console.log('GPU selector available in command palette: Cmd+Shift+C → "Select GPU"');
  }
};

export default extension;
