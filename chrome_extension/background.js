// Canvas AI Assistant - Background Service Worker
// Handles extension lifecycle and API communication

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

// Extension installation
chrome.runtime.onInstalled.addListener((details) => {
    console.log('🤖 Canvas AI Assistant installed/updated');
    
    if (details.reason === 'install') {
        // Set default settings
        chrome.storage.sync.set({
            'canvasAI_enabled': true,
            'api_url': API_BASE_URL,
            'auto_analyze': false,
            'show_quick_actions': true
        });
        
        // Open welcome page
        chrome.tabs.create({
            url: chrome.runtime.getURL('popup.html')
        });
    }
    
    // Add context menu for selected text
    chrome.contextMenus.create({
        id: 'canvas-ai-analyze',
        title: '🤖 Analyze with Canvas AI',
        contexts: ['selection']
    });
    
    chrome.contextMenus.create({
        id: 'canvas-ai-question',
        title: '❓ Ask Canvas AI about this',
        contexts: ['selection']
    });
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
    // Check if we're on a Canvas page
    if (tab.url && (tab.url.includes('instructure.com') || tab.url.includes('canvas.com'))) {
        // Toggle AI assistant on Canvas pages
        chrome.tabs.sendMessage(tab.id, {
            action: 'toggle_assistant'
        });
    } else {
        // Open popup for non-Canvas pages
        chrome.action.openPopup();
    }
});

// Message handling
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'health_check') {
        healthCheck().then(result => sendResponse(result));
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'get_settings') {
        chrome.storage.sync.get([
            'canvasAI_enabled',
            'api_url',
            'auto_analyze',
            'show_quick_actions'
        ], (result) => {
            sendResponse(result);
        });
        return true;
    }
    
    if (request.action === 'save_settings') {
        chrome.storage.sync.set(request.settings, () => {
            sendResponse({ success: true });
        });
        return true;
    }
});

// API Health Check
async function healthCheck() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        return {
            status: 'healthy',
            api_url: API_BASE_URL,
            response: data,
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        return {
            status: 'error',
            api_url: API_BASE_URL,
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'canvas-ai-analyze') {
        chrome.tabs.sendMessage(tab.id, {
            action: 'analyze_selection',
            text: info.selectionText
        });
    }
    
    if (info.menuItemId === 'canvas-ai-question') {
        chrome.tabs.sendMessage(tab.id, {
            action: 'question_about_selection',
            text: info.selectionText
        });
    }
});

// Periodic health check
setInterval(async () => {
    const health = await healthCheck();
    
    // Update extension badge based on API status
    if (health.status === 'healthy') {
        chrome.action.setBadgeText({ text: '' });
        chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
    } else {
        chrome.action.setBadgeText({ text: '!' });
        chrome.action.setBadgeBackgroundColor({ color: '#F44336' });
    }
}, 300000); // Check every 5 minutes

// Tab navigation handling
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Check if it's a Canvas page
        if (tab.url.includes('instructure.com') || tab.url.includes('canvas.com')) {
            // Inject enhanced functionality
            chrome.tabs.sendMessage(tabId, {
                action: 'page_loaded',
                url: tab.url
            }).catch(() => {
                // Ignore errors for tabs that don't have the content script
            });
        }
    }
});
