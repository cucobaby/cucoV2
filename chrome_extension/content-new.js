// Canvas AI Assistant - Working Version
console.log('🤖 Canvas AI Assistant v3.0.0 - WORKING VERSION LOADED');

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

class CanvasAIAssistant {
    constructor() {
        this.init();
    }

    init() {
        console.log('🎯 Initializing Canvas AI Assistant...');
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.createUI());
        } else {
            this.createUI();
        }
    }

    createUI() {
        console.log('🎨 Creating UI elements...');
        this.createFloatingButton();
    }

    createFloatingButton() {
        // Remove any existing button
        const existing = document.getElementById('canvas-ai-btn');
        if (existing) existing.remove();

        const button = document.createElement('div');
        button.id = 'canvas-ai-btn';
        button.innerHTML = '🤖 AI Assistant';
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
        `;
        
        button.addEventListener('click', () => this.togglePanel());
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-3px)';
            button.style.boxShadow = '0 6px 25px rgba(0,0,0,0.4)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
        });
        
        document.body.appendChild(button);
        console.log('✅ Floating button created successfully');
    }

    togglePanel() {
        console.log('🔄 Toggling AI panel...');
        
        let panel = document.getElementById('ai-panel');
        if (panel) {
            panel.remove();
            return;
        }

        this.createPanel();
    }

    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'ai-panel';
        panel.style.cssText = `
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            width: 400px;
            max-height: 80vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 10001;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        `;
        
        panel.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; flex-shrink: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 18px;">🤖 Canvas AI Assistant</h3>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <button id="view-kb-btn" style="
                            background: rgba(255, 255, 255, 0.2);
                            border: 1px solid rgba(255, 255, 255, 0.3);
                            color: white;
                            padding: 6px 12px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 12px;
                            font-weight: 500;
                            transition: all 0.2s ease;
                        ">📚 View Knowledge Base</button>
                        <button id="close-panel" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer;">&times;</button>
                    </div>
                </div>
            </div>
            
            <!-- Knowledge Base Section (initially hidden) -->
            <div id="knowledge-base-section" style="
                background: #f8f9fa; 
                border-bottom: 1px solid #e9ecef; 
                padding: 0; 
                max-height: 0; 
                overflow: hidden; 
                transition: all 0.3s ease;
            ">
                <div style="padding: 15px;">
                    <h4 style="margin: 0 0 10px 0; color: #495057; font-size: 14px;">📚 Knowledge Base Documents</h4>
                    <div id="documents-list" style="font-size: 13px; color: #6c757d;">
                        Loading documents...
                    </div>
                </div>
            </div>
            
            <div style="padding: 20px; overflow-y: auto; flex: 1;">
                <!-- Upload Section -->
                <div style="margin-bottom: 30px;">
                    <h4 style="margin: 0 0 15px 0; color: #333;">📤 Upload Current Page</h4>
                    <p style="margin: 0 0 15px 0; font-size: 14px; color: #666;">
                        Extract and upload the content from this Canvas page to the AI knowledge base.
                    </p>
                    <button id="upload-btn" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        cursor: pointer;
                        font-weight: bold;
                        width: 100%;
                        transition: all 0.2s ease;
                    ">📤 Add Content</button>
                    <div id="upload-result" style="margin-top: 15px;"></div>
                </div>
                
                <!-- Ask Cuco Section -->
                <div style="border: 3px solid #ff4757; padding: 15px; border-radius: 8px; background: #fff5f5;">
                    <h4 style="margin: 0 0 15px 0; color: #ff4757; font-size: 16px;">🤖 Ask Cuco</h4>
                    <textarea id="question-input" placeholder="Ask Cuco a question about your uploaded content..." style="
                        width: 100%;
                        min-height: 80px;
                        padding: 12px;
                        border: 2px solid #ff4757;
                        border-radius: 8px;
                        resize: vertical;
                        font-family: inherit;
                        font-size: 14px;
                        margin-bottom: 10px;
                        box-sizing: border-box;
                    "></textarea>
                    <button id="ask-btn" style="
                        background: #ff4757;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        cursor: pointer;
                        font-weight: bold;
                        width: 100%;
                        transition: all 0.2s ease;
                    ">🤖 Ask Cuco</button>
                    <div id="question-result" style="margin-top: 15px; max-height: 300px; overflow-y: auto;"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Add event listeners
        panel.querySelector('#close-panel').addEventListener('click', () => panel.remove());
        panel.querySelector('#upload-btn').addEventListener('click', () => this.uploadContent());
        panel.querySelector('#ask-btn').addEventListener('click', () => this.askQuestion());
        panel.querySelector('#view-kb-btn').addEventListener('click', () => this.toggleKnowledgeBase());
        
        console.log('✅ Panel created with both sections visible');
    }

    async uploadContent() {
        console.log('📤 Starting content upload...');
        const resultDiv = document.getElementById('upload-result');
        resultDiv.innerHTML = '<div style="color: #667eea;">🔄 Extracting content...</div>';
        
        try {
            // Simple content extraction
            const content = this.extractContent();
            const title = document.title || 'Canvas Page';
            
            console.log(`📄 Extracted ${content.length} characters from "${title}"`);
            
            const response = await fetch(`${API_BASE_URL}/ingest-content`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    source: 'canvas_chrome_extension',
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div style="color: #4CAF50; font-weight: bold;">✅ Content Uploaded Successfully!</div>
                <div style="font-size: 12px; color: #666; margin-top: 5px;">
                    ${result.chunks_created || 1} chunks created • ${content.length} characters
                </div>
            `;
            
            console.log('✅ Upload successful:', result);
            
        } catch (error) {
            console.error('❌ Upload failed:', error);
            resultDiv.innerHTML = `<div style="color: #f44336;">❌ Upload failed: ${error.message}</div>`;
        }
    }

    async askQuestion() {
        console.log('❓ Processing question...');
        const questionInput = document.getElementById('question-input');
        const resultDiv = document.getElementById('question-result');
        const question = questionInput.value.trim();
        
        if (!question) {
            resultDiv.innerHTML = '<div style="color: #f44336;">Please enter a question</div>';
            return;
        }
        
        resultDiv.innerHTML = '<div style="color: #ff4757;">🤖 Cuco is thinking...</div>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/ask-question`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    source: 'canvas_chrome_extension'
                })
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #ff4757;">
                    <div style="color: #ff4757; font-weight: bold; margin-bottom: 8px;">🤖 Cuco's Answer:</div>
                    <div style="color: #333; line-height: 1.4;">${result.answer || result.response || 'No answer found'}</div>
                </div>
            `;
            
            questionInput.value = '';
            console.log('✅ Question answered:', result);
            
        } catch (error) {
            console.error('❌ Question failed:', error);
            resultDiv.innerHTML = `<div style="color: #f44336;">❌ Error: ${error.message}</div>`;
        }
    }

    extractContent() {
        // Simple but effective content extraction
        const selectors = [
            '.user_content',
            '.show-content',
            '.assignment-description',
            '.page-content',
            '.wiki-page-content',
            '.course-content'
        ];
        
        let content = '';
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                content += element.innerText + '\n\n';
            }
        }
        
        // Fallback to main content areas
        if (!content.trim()) {
            const main = document.querySelector('main') || document.querySelector('#content');
            if (main) {
                content = main.innerText;
            }
        }
        
        return content.trim() || document.title;
    }

    async toggleKnowledgeBase() {
        console.log('📚 Toggling knowledge base view...');
        const kbSection = document.getElementById('knowledge-base-section');
        const viewBtn = document.getElementById('view-kb-btn');
        
        if (!kbSection || !viewBtn) return;
        
        const isExpanded = kbSection.style.maxHeight !== '0px' && kbSection.style.maxHeight !== '';
        
        if (isExpanded) {
            // Collapse
            kbSection.style.maxHeight = '0px';
            kbSection.style.padding = '0';
            viewBtn.textContent = '📚 View Knowledge Base';
        } else {
            // Expand and load documents
            viewBtn.textContent = '📚 Hide Knowledge Base';
            kbSection.style.maxHeight = '300px';
            kbSection.style.padding = '0';
            await this.loadKnowledgeBaseDocuments();
        }
    }

    async loadKnowledgeBaseDocuments() {
        console.log('📚 Loading knowledge base documents...');
        const documentsList = document.getElementById('documents-list');
        
        if (!documentsList) return;
        
        documentsList.innerHTML = '<div style="color: #6c757d;">🔄 Loading documents...</div>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/list-documents`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const result = await response.json();
            
            console.log('📚 Documents loaded:', result);
            
            if (result.documents && result.documents.length > 0) {
                let documentsHtml = `
                    <div style="margin-bottom: 10px; font-weight: 500; color: #495057;">
                        📊 ${result.count} document${result.count !== 1 ? 's' : ''} in knowledge base:
                    </div>
                `;
                
                result.documents.forEach((doc, index) => {
                    const timestamp = doc.timestamp ? new Date(doc.timestamp).toLocaleDateString() : 'Unknown date';
                    documentsHtml += `
                        <div style="
                            padding: 8px 10px; 
                            margin: 5px 0; 
                            background: white; 
                            border-radius: 4px; 
                            border-left: 3px solid #667eea;
                            font-size: 12px;
                        ">
                            <div style="font-weight: 500; color: #495057; margin-bottom: 2px;">
                                📄 ${doc.title}
                            </div>
                            <div style="color: #6c757d; font-size: 11px;">
                                📅 ${timestamp} • 🔗 ${doc.content_type || 'page'}
                            </div>
                        </div>
                    `;
                });
                
                documentsList.innerHTML = documentsHtml;
            } else {
                documentsList.innerHTML = `
                    <div style="
                        text-align: center; 
                        padding: 20px; 
                        color: #6c757d; 
                        font-style: italic;
                    ">
                        📂 Knowledge base is empty<br>
                        <small>Upload some content to get started!</small>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('❌ Failed to load documents:', error);
            documentsList.innerHTML = `
                <div style="color: #dc3545; text-align: center; padding: 10px;">
                    ❌ Failed to load documents<br>
                    <small>${error.message}</small>
                </div>
            `;
        }
    }
}

// Initialize the assistant
console.log('🚀 Starting Canvas AI Assistant...');
window.canvasAI = new CanvasAIAssistant();
