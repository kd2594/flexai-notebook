/**
 * FlexAI GPU Selector - JupyterLab Extension
 * Adds GPU selection UI to JupyterLab toolbar
 */

define(function() {
    return {
        load_ipython_extension: function() {
            console.log('FlexAI GPU Selector extension loaded');
            
            // Add toolbar button
            const addToolbarButton = function() {
                if (Jupyter && Jupyter.toolbar) {
                    Jupyter.toolbar.add_buttons_group([{
                        'label': 'FlexAI GPU',
                        'icon': 'fa-microchip',
                        'callback': showGPUDialog,
                        'id': 'flexai-gpu-button'
                    }]);
                }
            };
            
            // Show GPU selection dialog
            const showGPUDialog = async function() {
                try {
                    const response = await fetch('/flexai/gpu-types');
                    const gpuTypes = await response.json();
                    
                    createDialog(gpuTypes);
                } catch (error) {
                    alert('Error loading GPU types: ' + error.message);
                }
            };
            
            // Create dialog
            const createDialog = function(gpuTypes) {
                const dialog = $('<div/>').attr('title', 'Select FlexAI Compute');
                
                let html = '<div style="padding: 20px;">';
                html += '<h4>Select Hardware Accelerator</h4>';
                html += '<div style="margin: 20px 0;">';
                
                // Add CPU option
                html += createGPUOption('CPU', 'CPU Only', '$0.00/hr', true);
                
                // Add GPU options
                if (gpuTypes && gpuTypes.length > 0) {
                    gpuTypes.forEach(gpu => {
                        html += createGPUOption(
                            gpu.type || gpu.name,
                            `${gpu.name} - ${gpu.memory}`,
                            `$${gpu.price_per_hour}/hr`,
                            false
                        );
                    });
                }
                
                html += '</div>';
                html += '<div id="gpu-status" style="margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px; display: none;"></div>';
                html += '</div>';
                
                dialog.html(html);
                
                // Add to body
                dialog.dialog({
                    width: 600,
                    buttons: {
                        'Select': async function() {
                            const selected = $('input[name="gpu-type"]:checked').val();
                            await selectGPU(selected);
                            $(this).dialog('close');
                        },
                        'Cancel': function() {
                            $(this).dialog('close');
                        }
                    }
                });
            };
            
            // Create GPU option HTML
            const createGPUOption = function(value, label, price, checked) {
                return `
                    <div style="margin: 10px 0; padding: 15px; border: 2px solid ${checked ? '#4CAF50' : '#ddd'}; border-radius: 8px; cursor: pointer;" 
                         onclick="this.querySelector('input').checked = true; 
                                  this.parentElement.querySelectorAll('div').forEach(d => d.style.borderColor='#ddd'); 
                                  this.style.borderColor='#4CAF50';">
                        <label style="cursor: pointer; display: block; width: 100%;">
                            <input type="radio" name="gpu-type" value="${value}" ${checked ? 'checked' : ''} style="margin-right: 10px;">
                            <strong>${label}</strong>
                            <span style="float: right; color: #666;">${price}</span>
                        </label>
                    </div>
                `;
            };
            
            // Select GPU
            const selectGPU = async function(gpuType) {
                const statusDiv = $('#gpu-status');
                statusDiv.show().html('<i class="fa fa-spinner fa-spin"></i> Provisioning ' + gpuType + '...');
                
                try {
                    const response = await fetch('/flexai/gpu-select', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({gpu_type: gpuType})
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        statusDiv.html('<i class="fa fa-check" style="color: green;"></i> ' + result.message);
                        
                        // Update toolbar button
                        $('#flexai-gpu-button').addClass('btn-success').attr('title', 'Current: ' + gpuType);
                        
                        // Show notification
                        setTimeout(() => {
                            alert('✓ Successfully provisioned ' + gpuType + '\n\nYour notebook is now using this compute resource.');
                        }, 500);
                    } else {
                        throw new Error(result.message);
                    }
                } catch (error) {
                    statusDiv.html('<i class="fa fa-exclamation-triangle" style="color: red;"></i> Error: ' + error.message);
                }
            };
            
            // Initialize
            if (Jupyter && Jupyter.notebook) {
                addToolbarButton();
            } else {
                events.on('app_initialized.NotebookApp', addToolbarButton);
            }
        }
    };
});
