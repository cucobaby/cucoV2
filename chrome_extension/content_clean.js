// Canvas AI Assistant - Clean Version
console.log('🤖 Canvas AI Assistant v4.0.0 - CLEAN VERSION LOADED');

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

// Function to format educational response with proper HTML
function formatEducationalResponse(text) {
    if (!text) return 'No content available';
    
    // Convert the markdown-style formatting to HTML
    let formatted = text
        // Convert headers
        .replace(/^# (.*$)/gm, '<h2 style="color: #ff4757; font-size: 18px; font-weight: bold; margin: 16px 0 8px 0; border-bottom: 2px solid #ff4757; padding-bottom: 4px;">$1</h2>')
        .replace(/^## (.*$)/gm, '<h3 style="color: #2c3e50; font-size: 16px; font-weight: 600; margin: 14px 0 6px 0;">$1</h3>')
        .replace(/^### (.*$)/gm, '<h4 style="color: #34495e; font-size: 14px; font-weight: 600; margin: 10px 0 4px 0;">$1</h4>')
        
        // Convert learning objectives (special blockquote style)
        .replace(/^> \*\*(.*?)\*\*/gm, '<div style="background: #e8f4fd; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; border-radius: 4px; color: #2c3e50; font-weight: 500;">$1</div>')
        
        // Convert bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600; color: #2c3e50;">$1</strong>')
        
        // Convert bullet points
        .replace(/^- (.*$)/gm, '<li style="margin: 4px 0; padding-left: 4px;">$1</li>')
        
        // Wrap consecutive list items in ul tags
        .replace(/(<li[^>]*>.*<\/li>\s*)+/g, '<ul style="margin: 8px 0; padding-left: 20px;">$&</ul>')
        
        // Convert horizontal rules
        .replace(/^---$/gm, '<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 16px 0;">')
        
        // Convert table rows (basic support)
        .replace(/^\|(.+)\|$/gm, function(match, content) {
            const cells = content.split('|').map(cell => cell.trim());
            if (cells[0] === 'Term' || cells[0] === '---') return ''; // Skip header separators
            return `<tr><td style="padding: 6px; border: 1px solid #ddd; font-weight: 500;">${cells[0] || ''}</td><td style="padding: 6px; border: 1px solid #ddd;">${cells[1] || ''}</td><td style="padding: 6px; border: 1px solid #ddd; font-size: 12px; color: #666;">${cells[2] || ''}</td></tr>`;
        })
        
        // Wrap table rows in table
        .replace(/(<tr>.*<\/tr>\s*)+/g, '<table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px;"><thead><tr><th style="background: #f8f9fa; padding: 8px; border: 1px solid #ddd; font-weight: 600;">Term</th><th style="background: #f8f9fa; padding: 8px; border: 1px solid #ddd; font-weight: 600;">Definition</th><th style="background: #f8f9fa; padding: 8px; border: 1px solid #ddd; font-weight: 600;">Why Important</th></tr></thead><tbody>$&</tbody></table>')
        
        // Convert line breaks to HTML
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    
    return formatted;
}

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
        let panel = document.getElementById('canvas-ai-panel');
        
        if (panel) {
            panel.remove();
        } else {
            this.createAssistantPanel();
        }
    }

    createAssistantPanel() {
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
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .canvas-ai-panel {
                position: fixed;
                top: 50px;
                right: 20px;
                width: 420px;
                max-height: 80vh;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                z-index: 10001;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                border: 1px solid #e0e0e0;
                overflow: hidden;
            }
            .ai-panel-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 16px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .ai-panel-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }
            .ai-panel-close {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
            }
            .ai-panel-close:hover {
                background: rgba(255,255,255,0.2);
            }
            .ai-panel-content {
                padding: 20px;
                max-height: 60vh;
                overflow-y: auto;
            }
            .ai-feature-section {
                margin-bottom: 24px;
                padding-bottom: 20px;
                border-bottom: 1px solid #f0f0f0;
            }
            .ai-feature-section:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }
            .ai-feature-section h4 {
                margin: 0 0 12px 0;
                color: #333;
                font-size: 16px;
                font-weight: 600;
            }
            .ai-feature-section p {
                margin: 0 0 16px 0;
                color: #666;
                font-size: 14px;
                line-height: 1.4;
            }
            .ai-feature-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
                width: 100%;
                margin-bottom: 12px;
            }
            .ai-feature-btn:hover {
                background: #5a67d8;
                transform: translateY(-1px);
            }
            .ai-feature-btn.cuco-btn {
                background: #ff4757;
            }
            .ai-feature-btn.cuco-btn:hover {
                background: #ff3742;
            }
            .ai-question-input textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                resize: vertical;
                min-height: 80px;
                margin-bottom: 12px;
                font-family: inherit;
                box-sizing: border-box;
            }
            .ai-question-input textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .ai-result-area {
                margin-top: 12px;
                padding: 12px;
                border-radius: 8px;
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                font-size: 14px;
                line-height: 1.4;
                min-height: 20px;
            }
            .ai-loading {
                color: #667eea;
                font-style: italic;
            }
        `;
        
        if (!document.getElementById('canvas-ai-styles')) {
            style.id = 'canvas-ai-styles';
            document.head.appendChild(style);
        }
        
        document.body.appendChild(panel);
        
        // Add event listeners
        panel.querySelector('.ai-panel-close').addEventListener('click', () => panel.remove());
        panel.querySelector('#analyze-page-btn').addEventListener('click', () => this.analyzeCurrentPage());
        panel.querySelector('#ask-cuco-btn').addEventListener('click', () => this.askCuco());
        
        console.log('✅ Assistant panel created');
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
            
            // Upload to API
            const response = await fetch(`${API_BASE_URL}/upload-content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: pageTitle,
                    content: content,
                    source: 'canvas_chrome_extension',
                    url: window.location.href,
                    content_type: contentType,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Upload failed: HTTP ${response.status} - ${errorText}`);
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
            
            // Format the educational response properly
            const formattedAnswer = formatEducationalResponse(result.answer || 'No answer found');
            
            resultDiv.innerHTML = `
                <div style="border-left: 4px solid #ff4757; padding-left: 12px; margin-left: 4px;">
                    <div style="color: #ff4757; font-weight: 600; margin-bottom: 12px; font-size: 16px;">🤖 Cuco's Answer:</div>
                    <div style="color: #333; line-height: 1.6; font-size: 14px;">${formattedAnswer}</div>
                    ${result.sources && result.sources.length > 0 ? `
                        <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d;">
                            <strong>📚 Sources:</strong> ${result.sources.join(', ')}
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
