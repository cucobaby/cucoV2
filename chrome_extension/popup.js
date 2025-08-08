// Canvas AI Assistant - Popup Script
// Handles popup interface interactions and settings

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🤖 Canvas AI Assistant popup loaded');
    
    // Initialize popup
    await initializePopup();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    await loadSettings();
    await checkAPIHealth();
    await loadStats();
});

async function initializePopup() {
    // Show loading state
    document.getElementById('status-indicator').innerHTML = `
        <span class="status-dot"></span>
        <span class="status-text">Initializing...</span>
    `;
}

function setupEventListeners() {
    try {
        // Action buttons
        document.getElementById('analyze-current').addEventListener('click', analyzeCurrentPage);
        document.getElementById('open-assistant').addEventListener('click', openAssistant);
        document.getElementById('health-check').addEventListener('click', checkAPIHealth);
        
        // Your Cuco button
        const cucoButton = document.getElementById('cuco-button');
        if (cucoButton) {
            cucoButton.addEventListener('click', openCucoWebApp);
            console.log('✅ Your Cuco button event listener added');
        } else {
            console.error('❌ Your Cuco button not found');
        }
        
        // Settings toggles
        document.getElementById('enable-assistant').addEventListener('change', handleSettingChange);
        document.getElementById('auto-analyze').addEventListener('change', handleSettingChange);
        document.getElementById('show-quick-actions').addEventListener('change', handleSettingChange);
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }
    
    // Footer links
    document.getElementById('view-docs').addEventListener('click', () => {
        chrome.tabs.create({ url: 'https://cucov2-production.up.railway.app/docs' });
    });
    
    document.getElementById('report-issue').addEventListener('click', () => {
        chrome.tabs.create({ url: 'https://github.com/cucobaby/cucoV2/issues/new' });
    });
    
    document.getElementById('about').addEventListener('click', showAbout);
}

async function loadSettings() {
    try {
        const settings = await new Promise((resolve) => {
            chrome.runtime.sendMessage({ action: 'get_settings' }, resolve);
        });
        
        // Update UI with current settings
        document.getElementById('enable-assistant').checked = settings.canvasAI_enabled !== false;
        document.getElementById('auto-analyze').checked = settings.auto_analyze === true;
        document.getElementById('show-quick-actions').checked = settings.show_quick_actions !== false;
        
        console.log('Settings loaded:', settings);
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

async function handleSettingChange(event) {
    const setting = event.target.id;
    const value = event.target.checked;
    
    const settingsMap = {
        'enable-assistant': 'canvasAI_enabled',
        'auto-analyze': 'auto_analyze',
        'show-quick-actions': 'show_quick_actions'
    };
    
    const settingKey = settingsMap[setting];
    if (!settingKey) return;
    
    try {
        const settings = { [settingKey]: value };
        
        await new Promise((resolve) => {
            chrome.runtime.sendMessage({ 
                action: 'save_settings', 
                settings: settings 
            }, resolve);
        });
        
        console.log(`Setting updated: ${settingKey} = ${value}`);
        
        // Show feedback
        showNotification(`${settingKey.replace('_', ' ')} ${value ? 'enabled' : 'disabled'}`, 'success');
        
    } catch (error) {
        console.error('Failed to save setting:', error);
        showNotification('Failed to save setting', 'error');
        
        // Revert checkbox
        event.target.checked = !value;
    }
}

async function checkAPIHealth() {
    const healthButton = document.getElementById('health-check');
    const statusIndicator = document.getElementById('status-indicator');
    const apiInfo = document.getElementById('api-info');
    
    // Show loading
    healthButton.classList.add('loading');
    statusIndicator.innerHTML = `
        <span class="status-dot"></span>
        <span class="status-text">Checking...</span>
    `;
    
    try {
        const health = await new Promise((resolve) => {
            chrome.runtime.sendMessage({ action: 'health_check' }, resolve);
        });
        
        // Update status indicator
        const isHealthy = health.status === 'healthy';
        const statusClass = isHealthy ? 'healthy' : 'error';
        const statusText = isHealthy ? 'Connected' : 'Disconnected';
        
        statusIndicator.innerHTML = `
            <span class="status-dot ${statusClass}"></span>
            <span class="status-text">${statusText}</span>
        `;
        
        // Update API info
        apiInfo.innerHTML = `
            <div class="api-row">
                <span class="api-label">Endpoint:</span>
                <span class="api-value">${health.api_url}</span>
            </div>
            <div class="api-row">
                <span class="api-label">Status:</span>
                <span class="api-value ${statusClass}">${health.status}</span>
            </div>
            <div class="api-row">
                <span class="api-label">Last Check:</span>
                <span class="api-value">${new Date(health.timestamp).toLocaleTimeString()}</span>
            </div>
        `;
        
        if (health.response) {
            apiInfo.innerHTML += `
                <div class="api-row">
                    <span class="api-label">Version:</span>
                    <span class="api-value">${health.response.version || 'Unknown'}</span>
                </div>
            `;
        }
        
        console.log('API Health Check:', health);
        
    } catch (error) {
        console.error('Health check failed:', error);
        
        statusIndicator.innerHTML = `
            <span class="status-dot error"></span>
            <span class="status-text">Error</span>
        `;
        
        apiInfo.innerHTML = `
            <div class="api-row">
                <span class="api-label">Error:</span>
                <span class="api-value error">${error.message}</span>
            </div>
        `;
    } finally {
        healthButton.classList.remove('loading');
    }
}

async function analyzeCurrentPage() {
    try {
        // Get current active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab.url || (!tab.url.includes('instructure.com') && !tab.url.includes('canvas.com'))) {
            showNotification('Please navigate to a Canvas page first', 'warning');
            return;
        }
        
        // Send message to content script
        chrome.tabs.sendMessage(tab.id, { action: 'analyze_current_page' });
        
        showNotification('Analysis started...', 'success');
        
        // Close popup after a delay
        setTimeout(() => window.close(), 1000);
        
    } catch (error) {
        console.error('Failed to analyze page:', error);
        showNotification('Failed to analyze page', 'error');
    }
}

async function openAssistant() {
    try {
        // Get current active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab.url || (!tab.url.includes('instructure.com') && !tab.url.includes('canvas.com'))) {
            showNotification('Please navigate to a Canvas page first', 'warning');
            return;
        }
        
        // Send message to content script
        chrome.tabs.sendMessage(tab.id, { action: 'toggle_assistant' });
        
        // Close popup
        window.close();
        
    } catch (error) {
        console.error('Failed to open assistant:', error);
        showNotification('Failed to open assistant', 'error');
    }
}

function openCucoWebApp() {
    console.log('🌐 Your Cuco button clicked!');
    try {
        // Open the Cuco web application in a new tab
        chrome.tabs.create({ 
            url: 'http://localhost:3002',
            active: true 
        });
        
        console.log('✅ Opening Cuco web app at http://localhost:3002');
        
        // Show success notification if function exists
        if (typeof showNotification === 'function') {
            showNotification('Opening Your Cuco web app...', 'success');
        }
        
        // Close popup after a short delay
        setTimeout(() => window.close(), 500);
        
    } catch (error) {
        console.error('❌ Failed to open Cuco web app:', error);
        if (typeof showNotification === 'function') {
            showNotification('Failed to open web app', 'error');
        }
    }
}

async function loadStats() {
    try {
        // Load stats from storage
        const stats = await new Promise((resolve) => {
            chrome.storage.local.get(['pages_analyzed', 'questions_answered'], resolve);
        });
        
        document.getElementById('pages-analyzed').textContent = stats.pages_analyzed || 0;
        document.getElementById('questions-answered').textContent = stats.questions_answered || 0;
        
    } catch (error) {
        console.error('Failed to load stats:', error);
        document.getElementById('pages-analyzed').textContent = '-';
        document.getElementById('questions-answered').textContent = '-';
    }
}

function showAbout() {
    const aboutContent = `
        <div style="text-align: center; padding: 20px;">
            <h2>🤖 Canvas AI Assistant</h2>
            <p style="margin: 16px 0; color: #666;">
                AI-powered educational assistant for Canvas LMS
            </p>
            <div style="background: #f8f9ff; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>API:</strong> Railway Deployed</p>
                <p><strong>Features:</strong> Content Analysis, Q&A, Study Help</p>
            </div>
            <p style="font-size: 12px; color: #999;">
                Built with ❤️ for enhanced learning
            </p>
        </div>
    `;
    
    // Create modal overlay
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        border-radius: 12px;
        max-width: 300px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    `;
    modalContent.innerHTML = aboutContent;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close on click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // Auto close after 5 seconds
    setTimeout(() => {
        if (document.body.contains(modal)) {
            document.body.removeChild(modal);
        }
    }, 5000);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : type === 'warning' ? '#FF9800' : '#2196F3'};
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
        max-width: 200px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
