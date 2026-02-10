"""
Jupyter Custom Extension for FlexAI GPU Selection
This extension adds a GPU selection widget to Jupyter Notebook
"""

define([
    'base/js/namespace',
    'base/js/events',
    'jquery',
], function(Jupyter, events, $) {
    'use strict';

    const BACKEND_API_URL = window.location.protocol + '//' + window.location.hostname + ':8000';
    let currentSession = null;

    // Load GPU selection widget
    function loadGPUWidget() {
        const toolbarHTML = `
            <div id="flexai-widget" style="display: inline-block; margin-left: 10px;">
                <button id="flexai-gpu-btn" class="btn btn-default btn-sm" 
                        title="Select FlexAI Compute">
                    <i class="fa fa-microchip"></i> FlexAI Compute
                </button>
            </div>
        `;
        
        $('#maintoolbar-container').append(toolbarHTML);
        $('#flexai-gpu-btn').click(showGPUSelectionDialog);
    }

    // Show GPU selection dialog
    async function showGPUSelectionDialog() {
        const gpuTypes = await fetchAvailableGPUs();
        
        const dialogHTML = `
            <div class="modal fade" id="flexai-gpu-modal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal">&times;</button>
                            <h4 class="modal-title">
                                <i class="fa fa-microchip"></i> Select FlexAI Compute
                            </h4>
                        </div>
                        <div class="modal-body">
                            ${generateGPUCards(gpuTypes)}
                            <div id="gpu-selection-status" style="margin-top: 15px;"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if present
        $('#flexai-gpu-modal').remove();
        
        // Add modal to page
        $('body').append(dialogHTML);
        $('#flexai-gpu-modal').modal('show');
        
        // Add click handlers for GPU cards
        $('.gpu-card').click(function() {
            const gpuType = $(this).data('gpu-type');
            const gpuCount = parseInt($('#gpu-count-' + gpuType).val());
            selectGPU(gpuType, gpuCount);
        });
    }

    // Generate GPU selection cards
    function generateGPUCards(gpuTypes) {
        if (!gpuTypes || gpuTypes.length === 0) {
            return '<p class="text-muted">No GPU types available</p>';
        }

        let html = '<div class="row">';
        
        gpuTypes.forEach(gpu => {
            const available = gpu.available ? '' : 'opacity: 0.5; pointer-events: none;';
            const badge = gpu.available ? 
                '<span class="label label-success">Available</span>' : 
                '<span class="label label-danger">Unavailable</span>';
            
            html += `
                <div class="col-md-6" style="margin-bottom: 15px;">
                    <div class="gpu-card panel panel-default" 
                         data-gpu-type="${gpu.id}" 
                         style="cursor: pointer; ${available}">
                        <div class="panel-heading">
                            <h5 style="margin: 0;">
                                <strong>${gpu.name}</strong>
                                ${badge}
                            </h5>
                        </div>
                        <div class="panel-body">
                            <p><strong>Memory:</strong> ${gpu.memory}</p>
                            <p><strong>Compute Capability:</strong> ${gpu.compute_capability}</p>
                            <p><strong>Price:</strong> $${gpu.price_per_hour}/hour</p>
                            <div class="form-group">
                                <label>Number of GPUs:</label>
                                <select id="gpu-count-${gpu.id}" class="form-control" style="width: auto;">
                                    <option value="1">1</option>
                                    <option value="2">2</option>
                                    <option value="4">4</option>
                                    <option value="8">8</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    // Fetch available GPUs from backend
    async function fetchAvailableGPUs() {
        try {
            const response = await fetch(`${BACKEND_API_URL}/api/compute/available`);
            if (!response.ok) {
                throw new Error('Failed to fetch GPU types');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching GPU types:', error);
            showStatus('Error fetching GPU types', 'danger');
            return [];
        }
    }

    // Select GPU and provision instance
    async function selectGPU(gpuType, gpuCount) {
        showStatus('Provisioning compute resources...', 'info');
        
        try {
            const response = await fetch(`${BACKEND_API_URL}/api/compute/select`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gpu_type: gpuType,
                    gpu_count: gpuCount,
                    session_id: currentSession
                })
            });

            if (!response.ok) {
                throw new Error('Failed to provision compute');
            }

            const data = await response.json();
            currentSession = data.session_id;
            
            // Store session in notebook metadata
            Jupyter.notebook.metadata.flexai_session = {
                session_id: data.session_id,
                instance_id: data.instance_id,
                gpu_type: gpuType,
                gpu_count: gpuCount
            };
            
            showStatus(
                `✓ Successfully provisioned ${gpuType} x${gpuCount}<br>` +
                `Instance ID: ${data.instance_id}`,
                'success'
            );
            
            // Update toolbar button to show active status
            updateToolbarButton(gpuType, gpuCount);
            
        } catch (error) {
            console.error('Error selecting GPU:', error);
            showStatus('Error provisioning compute resources', 'danger');
        }
    }

    // Update toolbar button to show active compute
    function updateToolbarButton(gpuType, gpuCount) {
        $('#flexai-gpu-btn').html(
            `<i class="fa fa-microchip"></i> ${gpuType} x${gpuCount}`
        ).addClass('btn-success').removeClass('btn-default');
    }

    // Show status message
    function showStatus(message, type) {
        const alertClass = `alert-${type}`;
        $('#gpu-selection-status').html(`
            <div class="alert ${alertClass}">
                ${message}
            </div>
        `);
    }

    // Initialize extension
    function loadExtension() {
        console.log('Loading FlexAI Compute extension');
        
        // Wait for notebook to be loaded
        events.on('notebook_loaded.Notebook', function() {
            loadGPUWidget();
            
            // Check if there's an existing session
            if (Jupyter.notebook.metadata.flexai_session) {
                const session = Jupyter.notebook.metadata.flexai_session;
                currentSession = session.session_id;
                updateToolbarButton(session.gpu_type, session.gpu_count);
            }
        });
    }

    return {
        load_ipython_extension: loadExtension
    };
});
