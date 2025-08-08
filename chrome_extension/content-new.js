// Canvas AI Assistant - Working Version
console.log('🤖 Canvas AI Assistant v3.5.4 - ENHANCED UI WITH YOUR CUCO BUTTON LOADED');

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

class CanvasAIAssistant {
    constructor() {
        this.debugMode = localStorage.getItem('cucoDebugMode') === 'true';
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
        
        // Apply aggressive CSS to override Canvas styling
        panel.style.cssText = `
            position: fixed !important;
            top: 50% !important;
            right: 20px !important;
            transform: translateY(-50%) !important;
            width: 650px !important;
            max-width: 650px !important;
            min-width: 650px !important;
            max-height: 85vh !important;
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
            z-index: 999999 !important;
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            border: none !important;
            outline: none !important;
            margin: 0 !important;
            padding: 0 !important;
            font-family: Arial, sans-serif !important;
            font-size: 14px !important;
            line-height: 1.4 !important;
            color: #333 !important;
            text-align: left !important;
            box-sizing: border-box !important;
        `;
        
        console.log('🎨 Creating panel with enhanced Canvas-override styling...');
        
        panel.innerHTML = `
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; flex-shrink: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 18px;">🤖 Canvas AI Assistant</h3>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <button id="your-cuco-btn" style="
                            background: rgba(255, 255, 255, 0.2);
                            border: 1px solid rgba(255, 255, 255, 0.3);
                            color: white;
                            padding: 6px 12px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-size: 12px;
                            font-weight: 500;
                            transition: all 0.2s ease;
                        ">🌐 Your Cuco</button>
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
                    <div id="documents-list" style="
                        font-size: 13px; 
                        color: #6c757d;
                        max-height: 200px;
                        overflow-y: auto;
                        scrollbar-width: thin;
                        scrollbar-color: #cbd5e0 #f7fafc;
                        border-radius: 4px;
                    ">
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
        
        // Add custom scrollbar styles for the documents list
        if (!document.getElementById('ai-panel-scrollbar-styles')) {
            const style = document.createElement('style');
            style.id = 'ai-panel-scrollbar-styles';
            style.textContent = `
                #your-cuco-btn:hover {
                    background: rgba(255, 255, 255, 0.3) !important;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }
                #documents-list::-webkit-scrollbar {
                    width: 6px;
                }
                #documents-list::-webkit-scrollbar-track {
                    background: #f7fafc;
                    border-radius: 3px;
                }
                #documents-list::-webkit-scrollbar-thumb {
                    background: #cbd5e0;
                    border-radius: 3px;
                }
                #documents-list::-webkit-scrollbar-thumb:hover {
                    background: #a0aec0;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add event listeners
        panel.querySelector('#close-panel').addEventListener('click', () => panel.remove());
        panel.querySelector('#upload-btn').addEventListener('click', () => this.uploadContent());
        panel.querySelector('#ask-btn').addEventListener('click', () => this.askQuestion());
        panel.querySelector('#view-kb-btn').addEventListener('click', () => this.toggleKnowledgeBase());
        panel.querySelector('#your-cuco-btn').addEventListener('click', () => this.openCucoWebApp());
        
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
            
            const response = await fetch(`${API_BASE_URL}/upload-content`, {
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
            
            // Auto-refresh knowledge base if it's currently expanded
            const kbSection = document.getElementById('knowledge-base-section');
            if (kbSection && kbSection.style.maxHeight !== '0px' && kbSection.style.maxHeight !== '') {
                console.log('🔄 Auto-refreshing knowledge base...');
                await this.loadKnowledgeBaseDocuments();
            }
            
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
        
        console.log(`🤖 Asking question: "${question}"`);
        console.log(`🌐 API URL: ${API_BASE_URL}/query`);
        
        resultDiv.innerHTML = '<div style="color: #ff4757;">🤖 Cuco is thinking...</div>';
        
        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question
                })
            });
            
            console.log(`🌐 Response status: ${response.status}`);
            console.log(`🌐 Response headers:`, [...response.headers.entries()]);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ HTTP ${response.status}: ${errorText}`);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            
            console.log('✅ Question response:', result);
            
            // Format the educational response properly
            const formattedAnswer = formatEducationalResponse(result.answer || result.response || 'No answer provided');
            
            resultDiv.innerHTML = `
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #ff4757;">
                    <div style="color: #ff4757; font-weight: bold; margin-bottom: 8px;">🤖 Cuco's Answer:</div>
                    <div style="color: #333; line-height: 1.6; margin-bottom: 8px;">${formattedAnswer}</div>
                    ${result.sources && result.sources.length > 0 ? `
                        <div style="border-top: 1px solid #e9ecef; padding-top: 8px; margin-top: 8px;">
                            <div style="color: #6c757d; font-size: 12px; font-weight: 500; margin-bottom: 4px;">📚 Sources:</div>
                            <div style="color: #6c757d; font-size: 11px;">
                                ${result.sources.map(source => `• ${source}`).join('<br>')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
            
            questionInput.value = '';
            console.log('✅ Question answered successfully');
            
        } catch (error) {
            console.error('❌ Question failed:', error);
            resultDiv.innerHTML = `
                <div style="color: #f44336; padding: 10px; border-radius: 4px; background: #ffebee;">
                    <div style="font-weight: bold;">❌ Error:</div>
                    <div style="margin-top: 5px;">${error.message}</div>
                    <div style="margin-top: 5px; font-size: 12px; opacity: 0.8;">
                        Check the browser console for more details.
                    </div>
                </div>
            `;
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
            kbSection.style.maxHeight = '280px';
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
            
            if (!response.ok) {
                // If endpoint doesn't exist yet, show a helpful temporary message
                if (response.status === 404) {
                    documentsList.innerHTML = `
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 15px;
                            border-radius: 8px;
                            text-align: center;
                            margin: 10px 0;
                        ">
                            <div style="font-size: 24px; margin-bottom: 8px;">🚀</div>
                            <div style="font-weight: bold; margin-bottom: 5px;">Knowledge Base Viewer</div>
                            <div style="font-size: 12px; opacity: 0.9; margin-bottom: 10px;">
                                Track and manage your uploaded content
                            </div>
                            <div style="font-size: 11px; opacity: 0.8; line-height: 1.4;">
                                This feature is currently deploying to our servers.<br>
                                For now, you can still upload content and ask questions!<br>
                                The viewer will be available shortly.
                            </div>
                        </div>
                        <div style="
                            background: #f8f9fa;
                            border: 1px solid #e9ecef;
                            border-radius: 6px;
                            padding: 12px;
                            margin-top: 10px;
                        ">
                            <div style="font-weight: 500; color: #495057; margin-bottom: 5px; font-size: 12px;">
                                💡 How it works:
                            </div>
                            <ul style="margin: 0; padding-left: 15px; font-size: 11px; color: #6c757d; line-height: 1.4;">
                                <li>Upload content using the "📤 Add Content" button above</li>
                                <li>Ask questions using the "🤖 Ask Cuco" section</li>
                                <li>Soon: View all uploaded documents here with details</li>
                            </ul>
                        </div>
                    `;
                    return;
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
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
                    const chunkInfo = doc.chunk_count > 1 ? ` • 📦 ${doc.chunk_count} chunks` : '';
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
                                📅 ${timestamp} • 🔗 ${doc.content_type || 'page'}${chunkInfo}
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
            
            // Handle 404 (endpoint not deployed yet) vs other errors
            if (error.message.includes('404')) {
                documentsList.innerHTML = `
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 10px 0;
                    ">
                        <div style="font-size: 24px; margin-bottom: 8px;">🚀</div>
                        <div style="font-weight: bold; margin-bottom: 5px;">Knowledge Base Viewer</div>
                        <div style="font-size: 12px; opacity: 0.9; margin-bottom: 10px;">
                            Track and manage your uploaded content
                        </div>
                        <div style="font-size: 11px; opacity: 0.8; line-height: 1.4;">
                            This feature is currently deploying to our servers.<br>
                            For now, you can still upload content and ask questions!<br>
                            The viewer will be available shortly.
                        </div>
                    </div>
                    <div style="
                        background: #f8f9fa;
                        border: 1px solid #e9ecef;
                        border-radius: 6px;
                        padding: 12px;
                        margin-top: 10px;
                    ">
                        <div style="font-weight: 500; color: #495057; margin-bottom: 5px; font-size: 12px;">
                            💡 How it works:
                        </div>
                        <ul style="margin: 0; padding-left: 15px; font-size: 11px; color: #6c757d; line-height: 1.4;">
                            <li>Upload content using the "� Add Content" button above</li>
                            <li>Ask questions using the "🤖 Ask Cuco" section</li>
                            <li>Soon: View all uploaded documents here with details</li>
                        </ul>
                    </div>
                `;
            } else {
                documentsList.innerHTML = `
                    <div style="color: #dc3545; text-align: center; padding: 10px;">
                        ❌ Failed to load documents<br>
                        <small>${error.message}</small>
                    </div>
                `;
            }
        }
    }

    openCucoWebApp() {
        console.log('🌐 Opening Your Cuco web application...');
        try {
            // Open the Cuco web application in a new tab
            window.open('http://localhost:3002', '_blank');
            console.log('✅ Opened Cuco web app at http://localhost:3002');
        } catch (error) {
            console.error('❌ Failed to open Cuco web app:', error);
            alert('Failed to open Your Cuco web app. Please make sure it\'s running at http://localhost:3002');
        }
    }
}

// Initialize the assistant
console.log('🚀 Starting Canvas AI Assistant...');
window.canvasAI = new CanvasAIAssistant();
