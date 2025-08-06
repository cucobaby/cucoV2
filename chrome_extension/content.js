// Canvas AI Assistant - Clean Version v4.0.0
console.log('🤖 Canvas AI Assistant v4.0.0 - CLEAN VERSION LOADED');

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

// Kill any existing instances
if (window.canvasAIAssistant) {
    console.log('🗑️ Destroying existing assistant instance');
    delete window.canvasAIAssistant;
}

class CanvasAIAssistant {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🤖 Canvas AI Assistant initializing...');
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupUI());
        } else {
            this.setupUI();
        }
        
        this.isInitialized = true;
    }

    setupUI() {
        console.log('🎯 Setting up Canvas AI Assistant...');
        this.createFloatingButton();
    }

    createFloatingButton() {
        // Remove existing button if present
        const existingButton = document.getElementById('canvas-ai-assistant-btn');
        if (existingButton) existingButton.remove();

        const button = document.createElement('div');
        button.id = 'canvas-ai-assistant-btn';
        button.innerHTML = `
            <div class="ai-assistant-icon">🤖</div>
            <span>AI Assistant</span>
        `;
        button.className = 'canvas-ai-floating-btn';
        
        // Add styles
        button.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 50px;
            cursor: pointer;
            z-index: 10000;
            font-family: Arial, sans-serif;
            font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        `;
        
        button.addEventListener('click', () => this.toggleAssistantPanel());
        
        document.body.appendChild(button);
        console.log('✅ Floating button created');
    }

    toggleAssistantPanel() {
        console.log('🔄 Toggling assistant panel...');
        let panel = document.getElementById('canvas-ai-panel');
        
        if (panel) {
            console.log('📱 Panel exists, removing it');
            panel.remove();
        } else {
            console.log('📱 Panel does not exist, creating new one');
            this.createAssistantPanel();
        }
    }

    createAssistantPanel() {
        console.log('🎨 Creating assistant panel...');
        
        const panel = document.createElement('div');
        panel.id = 'canvas-ai-panel';
        panel.className = 'canvas-ai-panel';
        
        panel.innerHTML = `
            <div class="ai-panel-header">
                <h3>🤖 Canvas AI Assistant</h3>
                <button class="ai-panel-close">&times;</button>
            </div>
            <div class="ai-panel-content">
                <div class="ai-feature-section">
                    <h4>📤 Upload Current Page</h4>
                    <p>Extract and upload this Canvas page content to the AI knowledge base.</p>
                    <button id="analyze-page-btn" class="ai-feature-btn primary">
                        📄 Add Page to Knowledge Base
                    </button>
                    <div id="analysis-result" class="ai-result-area"></div>
                </div>
                
                <div class="ai-feature-section">
                    <h4>🤖 Ask Cuco</h4>
                    <div class="ai-question-input">
                        <textarea id="question-input" placeholder="Ask Cuco a question about your uploaded content..."></textarea>
                        <button id="ask-cuco-btn" class="ai-feature-btn cuco-btn">Ask Cuco</button>
                    </div>
                    <div id="question-result" class="ai-result-area"></div>
                </div>
            </div>
        `;
        
        // Force inline styles to override Canvas CSS
        panel.style.cssText = `
            position: fixed !important;
            top: 50px !important;
            right: 20px !important;
            width: 420px !important;
            max-height: 80vh !important;
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
            z-index: 999999 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            border: 2px solid #667eea !important;
            overflow: hidden !important;
            display: block !important;
            visibility: visible !important;
        `;
        
        // Add comprehensive styles with !important to override Canvas
        const style = document.createElement('style');
        style.id = 'canvas-ai-styles-enhanced';
        style.textContent = `
            #canvas-ai-panel {
                position: fixed !important;
                top: 50px !important;
                right: 20px !important;
                width: 420px !important;
                max-height: 80vh !important;
                background: white !important;
                border-radius: 12px !important;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3) !important;
                z-index: 999999 !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                border: 2px solid #667eea !important;
                overflow: visible !important;
                display: block !important;
                visibility: visible !important;
            }
            
            #canvas-ai-panel .ai-panel-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                padding: 16px 20px !important;
                border-radius: 12px 12px 0 0 !important;
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                margin: 0 !important;
                min-height: 60px !important;
                box-sizing: border-box !important;
            }
            
            #canvas-ai-panel .ai-panel-header h3 {
                margin: 0 !important;
                padding: 0 !important;
                font-size: 18px !important;
                font-weight: 600 !important;
                color: white !important;
                line-height: 1.2 !important;
            }
            
            #canvas-ai-panel .ai-panel-close {
                background: none !important;
                border: none !important;
                color: white !important;
                font-size: 24px !important;
                cursor: pointer !important;
                padding: 0 !important;
                width: 30px !important;
                height: 30px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border-radius: 50% !important;
                transition: background 0.2s !important;
                margin: 0 !important;
                line-height: 1 !important;
            }
            
            #canvas-ai-panel .ai-panel-close:hover {
                background: rgba(255,255,255,0.2) !important;
            }
            
            #canvas-ai-panel .ai-panel-content {
                padding: 20px !important;
                max-height: 60vh !important;
                overflow-y: auto !important;
                background: white !important;
                margin: 0 !important;
            }
            
            #canvas-ai-panel .ai-feature-section {
                margin-bottom: 24px !important;
                padding-bottom: 20px !important;
                border-bottom: 1px solid #f0f0f0 !important;
            }
            
            #canvas-ai-panel .ai-feature-section:last-child {
                border-bottom: none !important;
                margin-bottom: 0 !important;
            }
            
            #canvas-ai-panel .ai-feature-section h4 {
                margin: 0 0 12px 0 !important;
                padding: 0 !important;
                color: #333 !important;
                font-size: 16px !important;
                font-weight: 600 !important;
                line-height: 1.2 !important;
            }
            
            #canvas-ai-panel .ai-feature-section p {
                margin: 0 0 16px 0 !important;
                padding: 0 !important;
                color: #666 !important;
                font-size: 14px !important;
                line-height: 1.4 !important;
            }
            
            #canvas-ai-panel .ai-feature-btn {
                background: #667eea !important;
                color: white !important;
                border: none !important;
                padding: 12px 20px !important;
                border-radius: 8px !important;
                cursor: pointer !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                transition: all 0.2s !important;
                width: 100% !important;
                margin-bottom: 12px !important;
                box-sizing: border-box !important;
                display: block !important;
            }
            
            #canvas-ai-panel .ai-feature-btn:hover {
                background: #5a67d8 !important;
                transform: translateY(-1px) !important;
            }
            
            #canvas-ai-panel .ai-feature-btn.cuco-btn {
                background: #ff4757 !important;
            }
            
            #canvas-ai-panel .ai-feature-btn.cuco-btn:hover {
                background: #ff3742 !important;
            }
            
            #canvas-ai-panel .ai-question-input textarea {
                width: 100% !important;
                padding: 12px !important;
                border: 2px solid #e0e0e0 !important;
                border-radius: 8px !important;
                font-size: 14px !important;
                resize: vertical !important;
                min-height: 80px !important;
                margin-bottom: 12px !important;
                font-family: inherit !important;
                box-sizing: border-box !important;
            }
            
            #canvas-ai-panel .ai-question-input textarea:focus {
                outline: none !important;
                border-color: #667eea !important;
            }
            
            #canvas-ai-panel .ai-result-area {
                margin-top: 12px !important;
                padding: 12px !important;
                border-radius: 8px !important;
                background: #f8f9fa !important;
                border: 1px solid #e9ecef !important;
                font-size: 14px !important;
                line-height: 1.4 !important;
                min-height: 20px !important;
            }
            
            #canvas-ai-panel .ai-loading {
                color: #667eea !important;
                font-style: italic !important;
            }
        `;
        
        // Remove any existing styles and add new ones
        const existingStyle = document.getElementById('canvas-ai-styles-enhanced');
        if (existingStyle) existingStyle.remove();
        
        document.head.appendChild(style);
        document.body.appendChild(panel);
        
        // Debug: Log panel structure
        console.log('📋 Panel HTML structure:', panel.outerHTML.substring(0, 500));
        console.log('📐 Panel computed styles:', getComputedStyle(panel));
        
        // Verify header is present
        const header = panel.querySelector('.ai-panel-header');
        if (header) {
            console.log('✅ Header found:', header.outerHTML);
            console.log('📐 Header styles:', getComputedStyle(header));
        } else {
            console.error('❌ Header not found!');
        }
        
        // Add event listeners
        panel.querySelector('.ai-panel-close').addEventListener('click', () => {
            console.log('🗑️ Closing panel');
            panel.remove();
        });
        panel.querySelector('#analyze-page-btn').addEventListener('click', () => this.analyzeCurrentPage());
        panel.querySelector('#ask-cuco-btn').addEventListener('click', () => this.askCuco());
        
        console.log('✅ Assistant panel created with enhanced styling');
    }

    async analyzeCurrentPage() {
        const resultDiv = document.getElementById('analysis-result');
        resultDiv.innerHTML = '<div class="ai-loading">🔄 Extracting and uploading content...</div>';
        
        try {
            console.log('🤖 Starting content upload...');
            
            // Extract page content
            const content = this.extractPageContent();
            
            if (!content || content.trim().length < 50) {
                throw new Error('No significant content found on this page');
            }
            
            // Get page details
            const pageTitle = document.title || 'Canvas Page';
            const contentType = this.detectContentType();
            
            console.log(`📤 Uploading: "${pageTitle}" (${content.length} chars)`);
            console.log(`🔍 Content preview: "${content.substring(0, 200)}..."`);
            
            // Upload to API - DEBUGGING THE REQUEST
            const requestData = {
                title: pageTitle,
                content: content,
                source: 'canvas_chrome_extension',
                url: window.location.href,
                content_type: contentType,
                timestamp: new Date().toISOString()
            };
            
            console.log('📋 Request data:', requestData);
            
            const response = await fetch(`${API_BASE_URL}/upload-content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            console.log(`📊 Response status: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Response error:', errorText);
                
                if (response.status === 422) {
                    let errorDetails;
                    try {
                        errorDetails = JSON.parse(errorText);
                        console.error('🚨 Validation error details:', errorDetails);
                    } catch (e) {
                        console.error('Could not parse error JSON:', errorText);
                    }
                    throw new Error(`Validation Error (422): ${errorText}`);
                } else {
                    throw new Error(`Upload failed: HTTP ${response.status} - ${errorText}`);
                }
            }
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div style="color: #28a745; font-weight: 600;">✅ Content Successfully Uploaded</div>
                <div style="margin-top: 8px; font-size: 13px; color: #6c757d;">
                    <div>📄 Title: ${pageTitle}</div>
                    <div>📊 Chunks Created: ${result.chunks_created || 1}</div>
                    <div>🆔 Content ID: ${result.content_id || 'N/A'}</div>
                    <div>📏 Content Length: ${content.length.toLocaleString()} characters</div>
                </div>
            `;
            
            console.log('✅ Upload successful:', result);
            
        } catch (error) {
            console.error('❌ Upload failed:', error);
            resultDiv.innerHTML = `
                <div style="color: #dc3545; font-weight: 600;">❌ Upload Failed</div>
                <div style="margin-top: 8px; font-size: 13px; color: #6c757d;">
                    Error: ${error.message}
                </div>
            `;
        }
    }

    async askCuco() {
        const questionInput = document.getElementById('question-input');
        const resultDiv = document.getElementById('question-result');
        const question = questionInput.value.trim();
        
        if (!question) {
            resultDiv.innerHTML = '<div style="color: #dc3545;">Please enter a question</div>';
            return;
        }
        
        resultDiv.innerHTML = '<div class="ai-loading">🤖 Cuco is thinking...</div>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    source: 'canvas_chrome_extension'
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Query failed: HTTP ${response.status} - ${errorText}`);
            }
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div style="border-left: 4px solid #ff4757; padding-left: 12px; margin-left: 4px;">
                    <div style="color: #ff4757; font-weight: 600; margin-bottom: 8px;">🤖 Cuco's Answer:</div>
                    <div style="color: #333; line-height: 1.5;">${result.answer || 'No answer found'}</div>
                    ${result.sources && result.sources.length > 0 ? `
                        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d;">
                            Sources: ${result.sources.join(', ')}
                        </div>
                    ` : ''}
                </div>
            `;
            
            questionInput.value = '';
            console.log('✅ Question answered:', result);
            
        } catch (error) {
            console.error('❌ Query failed:', error);
            resultDiv.innerHTML = `
                <div style="color: #dc3545; font-weight: 600;">❌ Query Failed</div>
                <div style="margin-top: 8px; font-size: 13px; color: #6c757d;">
                    Error: ${error.message}
                </div>
            `;
        }
    }

    extractPageContent() {
        // Canvas-specific content selectors
        const selectors = [
            '.user_content',           // Canvas rich content areas
            '.show-content',           // Assignment descriptions
            '.assignment-description', // Assignment text
            '.page-content',           // Canvas pages
            '.wiki-page-content',      // Wiki pages
            '.discussion-entry',       // Discussion posts
            '.quiz-questions',         // Quiz content
            '.module-item-details',    // Module descriptions
            '.course-content'          // General course content
        ];
        
        let content = '';
        
        // Try each selector
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const element of elements) {
                const text = element.innerText || element.textContent;
                if (text && text.trim().length > 20) {
                    content += text.trim() + '\n\n';
                }
            }
        }
        
        // Fallback to main content areas if nothing found
        if (!content.trim()) {
            const fallbackSelectors = ['main', '#content', '.content', '#main-content'];
            for (const selector of fallbackSelectors) {
                const element = document.querySelector(selector);
                if (element) {
                    const text = element.innerText || element.textContent;
                    if (text && text.trim().length > 50) {
                        content = text.trim();
                        break;
                    }
                }
            }
        }
        
        // Final fallback to document title if nothing else
        if (!content.trim()) {
            content = document.title || 'No content found';
        }
        
        // Clean up the content
        content = content
            .replace(/\s+/g, ' ')           // Normalize whitespace
            .replace(/\n\s*\n/g, '\n')     // Remove extra line breaks
            .trim();
        
        return content;
    }

    detectContentType() {
        const url = window.location.href;
        
        if (url.includes('/assignments/')) return 'assignment';
        if (url.includes('/quizzes/')) return 'quiz';
        if (url.includes('/discussion_topics/')) return 'discussion';
        if (url.includes('/pages/')) return 'page';
        if (url.includes('/modules/')) return 'module';
        if (url.includes('/announcements/')) return 'announcement';
        if (url.includes('/syllabus')) return 'syllabus';
        if (url.includes('/grades')) return 'gradebook';
        if (url.includes('/files/')) return 'file';
        
        return 'page'; // Default
    }
}

// Initialize the assistant
console.log('🚀 Initializing Canvas AI Assistant...');
window.canvasAIAssistant = new CanvasAIAssistant();

// Log current URL for debugging
console.log('🌐 Current URL:', window.location.href);
console.log('✅ Canvas AI Assistant v4.0.0 loaded successfully');