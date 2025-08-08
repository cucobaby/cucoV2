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
            const response = await fetch(`${API_BASE_URL}/query-fast`, {
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
            
            // Check if this is an interactive quiz configuration
            if (result.sections && result.sections.quiz_mode && result.sections.quiz_type === 'interactive_config') {
                this.renderInteractiveQuizConfig(result, resultDiv);
            } else {
                // Regular response rendering
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
            }
            
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

    renderInteractiveQuizConfig(result, resultDiv) {
        const config = result.sections.quiz_data.interactive_config;
        const sessionId = result.sections.quiz_data.session_id;
        const detectedTopic = result.sections.quiz_data.detected_topic;
        
        resultDiv.innerHTML = `
            <div style="border-left: 4px solid #ff4757; padding: 16px; margin-left: 4px; background: #f8f9fa; border-radius: 8px;">
                <div style="color: #ff4757; font-weight: 600; margin-bottom: 16px; font-size: 18px;">
                    🎯 Quiz Configuration
                </div>
                
                <!-- Quiz Type Selection -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #333;">
                        📝 Quiz Type:
                    </label>
                    <div id="quiz-type-buttons" style="display: flex; gap: 8px; flex-wrap: wrap;">
                        ${config.quiz_types.map(type => `
                            <button class="quiz-option-btn" data-type="quiz_type" data-value="${type.id}" 
                                style="padding: 8px 16px; border: 2px solid #e9ecef; background: white; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.2s;">
                                ${type.label}
                            </button>
                        `).join('')}
                    </div>
                </div>

                <!-- Quiz Length Slider -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #333;">
                        📊 Quiz Length: <span id="length-display">10</span> questions
                    </label>
                    <input type="range" id="quiz-length-slider" min="5" max="20" step="5" value="10"
                        style="width: 100%; height: 6px; background: #e9ecef; border-radius: 3px; outline: none;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #6c757d; margin-top: 4px;">
                        <span>5</span><span>10</span><span>15</span><span>20</span>
                    </div>
                </div>

                <!-- Quiz Format Selection -->
                <div style="margin-bottom: 20px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #333;">
                        🎴 Quiz Format:
                    </label>
                    <div id="quiz-format-buttons" style="display: flex; gap: 8px;">
                        ${config.quiz_formats.map(format => `
                            <button class="quiz-option-btn" data-type="quiz_format" data-value="${format.id}"
                                style="padding: 8px 16px; border: 2px solid #e9ecef; background: white; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.2s;">
                                ${format.label}
                            </button>
                        `).join('')}
                    </div>
                </div>

                <!-- Topic Selection -->
                <div style="margin-bottom: 24px;">
                    <label style="display: block; font-weight: 600; margin-bottom: 8px; color: #333;">
                        🔬 Topic Focus:
                    </label>
                    <select id="quiz-topic-select" style="width: 100%; padding: 8px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px;">
                        ${detectedTopic ? `<option value="${detectedTopic}" selected>📍 ${detectedTopic} (detected)</option>` : ''}
                        ${config.topics.available.map(topic => 
                            topic !== detectedTopic ? `<option value="${topic}">${topic}</option>` : ''
                        ).join('')}
                        ${config.topics.custom_option ? '<option value="custom">✏️ Custom topic...</option>' : ''}
                    </select>
                </div>

                <!-- Start Quiz Button -->
                <button id="start-quiz-btn" 
                    style="width: 100%; padding: 12px; background: linear-gradient(135deg, #ff4757, #ff3742); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    🚀 Start Quiz
                </button>
                
                <input type="hidden" id="quiz-session-id" value="${sessionId}">
            </div>
        `;

        // Add event listeners for interactive elements
        this.setupQuizConfigListeners();
    }

    setupQuizConfigListeners() {
        // Quiz option buttons (type and format)
        document.querySelectorAll('.quiz-option-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const button = e.target;
                const type = button.dataset.type;
                
                // Remove selected state from siblings
                document.querySelectorAll(`[data-type="${type}"]`).forEach(sibling => {
                    sibling.style.background = 'white';
                    sibling.style.borderColor = '#e9ecef';
                    sibling.style.color = '#333';
                });
                
                // Add selected state
                button.style.background = '#ff4757';
                button.style.borderColor = '#ff4757';
                button.style.color = 'white';
            });
        });

        // Quiz length slider
        const lengthSlider = document.getElementById('quiz-length-slider');
        const lengthDisplay = document.getElementById('length-display');
        
        lengthSlider.addEventListener('input', (e) => {
            lengthDisplay.textContent = e.target.value;
        });

        // Start quiz button
        document.getElementById('start-quiz-btn').addEventListener('click', () => {
            this.startQuizWithConfig();
        });

        // Set default selections
        document.querySelector('[data-value="mixed"]').click(); // Default quiz type
        document.querySelector('[data-value="standard"]').click(); // Default format
    }

    startQuizWithConfig() {
        const sessionId = document.getElementById('quiz-session-id').value;
        const selectedType = document.querySelector('[data-type="quiz_type"][style*="rgb(255, 71, 87)"]')?.dataset.value || 'mixed';
        const selectedFormat = document.querySelector('[data-type="quiz_format"][style*="rgb(255, 71, 87)"]')?.dataset.value || 'standard';
        const selectedLength = document.getElementById('quiz-length-slider').value;
        const selectedTopic = document.getElementById('quiz-topic-select').value;

        // Show loading state
        const startBtn = document.getElementById('start-quiz-btn');
        startBtn.textContent = '🔄 Creating Quiz...';
        startBtn.disabled = true;

        // Send configuration to start quiz
        this.sendQuizConfiguration({
            session_id: sessionId,
            quiz_type: selectedType,
            quiz_format: selectedFormat,
            quiz_length: parseInt(selectedLength),
            topic: selectedTopic
        });
    }

    async sendQuizConfiguration(config) {
        try {
            const response = await fetch(`${API_BASE_URL}/quiz-config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    config_input: JSON.stringify(config),
                    available_topics: []
                })
            });

            if (!response.ok) {
                throw new Error(`Quiz configuration failed: HTTP ${response.status}`);
            }

            const result = await response.json();
            
            // Replace the configuration with the first quiz question
            const resultDiv = document.querySelector('.ai-result');
            resultDiv.innerHTML = `
                <div style="border-left: 4px solid #ff4757; padding: 16px; margin-left: 4px; background: #f8f9fa; border-radius: 8px;">
                    <div style="color: #ff4757; font-weight: 600; margin-bottom: 16px;">
                        🎯 Quiz Started!
                    </div>
                    <div style="color: #333; line-height: 1.5;">${result.answer || 'Quiz is starting...'}</div>
                </div>
            `;

        } catch (error) {
            console.error('❌ Quiz configuration failed:', error);
            const startBtn = document.getElementById('start-quiz-btn');
            startBtn.textContent = '❌ Error - Try Again';
            startBtn.disabled = false;
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