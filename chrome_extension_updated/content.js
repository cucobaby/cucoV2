// Canvas AI Assistant - Content Script
// This script runs on Canvas pages to add AI assistance functionality

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

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
        // Create floating AI assistant button
        this.createFloatingButton();
        
        // Add AI features to Canvas content areas
        this.enhanceCanvasPages();
        
        // Set up observers for dynamic content
        this.setupDynamicContentObserver();
        
        // Also run enhancement after a delay to catch any delayed content
        setTimeout(() => this.enhanceCanvasPages(), 2000);
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
        
        button.addEventListener('click', () => this.toggleAssistantPanel());
        
        document.body.appendChild(button);
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
                    <h4>🎯 Choose Content to Analyze</h4>
                    <div class="content-selection-options">
                        <button id="select-content-btn" class="ai-feature-btn secondary">
                            📍 Select Specific Content
                        </button>
                        <button id="detect-content-btn" class="ai-feature-btn secondary">
                            🔍 Auto-Detect Content Types
                        </button>
                        <button id="analyze-page-btn" class="ai-feature-btn">
                            � Upload Page to Knowledge Base
                        </button>
                    </div>
                    <div id="content-selection-area" class="content-selection-area"></div>
                    <div id="analysis-result" class="ai-result-area"></div>
                </div>
                
                <div class="ai-feature-section">
                    <h4>❓ Ask Questions</h4>
                    <div class="ai-question-input">
                        <textarea id="question-input" placeholder="Ask a question about the content..."></textarea>
                        <button id="ask-question-btn" class="ai-feature-btn">Ask AI</button>
                    </div>
                    <div id="question-result" class="ai-result-area"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Add event listeners
        panel.querySelector('.ai-panel-close').addEventListener('click', () => panel.remove());
        panel.querySelector('#select-content-btn').addEventListener('click', () => this.startContentSelection());
        panel.querySelector('#detect-content-btn').addEventListener('click', () => this.detectAndShowContentTypes());
        panel.querySelector('#analyze-page-btn').addEventListener('click', () => this.analyzeCurrentPage());
        panel.querySelector('#ask-question-btn').addEventListener('click', () => this.askQuestion());
    }

    async analyzeCurrentPage() {
        const resultDiv = document.getElementById('analysis-result');
        resultDiv.innerHTML = '<div class="ai-loading">🔄 Extracting and uploading content...</div>';
        
        try {
            console.log('🤖 Starting comprehensive content upload...');
            
            // Extract comprehensive page content using our enhanced method
            const content = this.extractPageContent();
            
            if (!content || content.trim().length < 50) {
                throw new Error('No significant content found on this page');
            }
            
            // Get page title for the upload
            const pageTitle = document.title || 'Canvas Page';
            const contentType = this.detectContentType();
            
            console.log(`📤 Uploading content: "${pageTitle}" (${content.length} characters)`);
            
            // Upload to knowledge base using ingest-content endpoint
            const response = await fetch(`${API_BASE_URL}/ingest-content`, {
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
                    course_id: this.extractCourseId(),
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('API endpoint not found - service may be starting up. Please try again in a moment.');
                } else {
                    const errorText = await response.text();
                    throw new Error(`Upload failed: ${response.status} - ${errorText}`);
                }
            }
            
            const result = await response.json();
            
            console.log('✅ Content uploaded successfully:', result);
            
            // Show success with detailed information
            resultDiv.innerHTML = `
                <div class="ai-analysis-result">
                    <h5>✅ Content Successfully Uploaded</h5>
                    <div class="upload-details">
                        <p><strong>📄 Title:</strong> ${pageTitle}</p>
                        <p><strong>📊 Chunks Created:</strong> ${result.chunks_created || 1}</p>
                        <p><strong>📚 Total Documents:</strong> ${result.total_content_items || 'N/A'}</p>
                        <p><strong>⏱️ Processing Time:</strong> ${result.processing_time ? (result.processing_time * 1000).toFixed(0) + 'ms' : 'N/A'}</p>
                        <p><strong>� Content Length:</strong> ${content.length.toLocaleString()} characters</p>
                        <p><strong>🔗 Content Type:</strong> ${contentType}</p>
                    </div>
                    
                    <div class="upload-success-actions">
                        <p><em>Your content is now available for AI questions!</em></p>
                        <small>Use the "Ask AI" feature below to test questions about this content.</small>
                    </div>
                </div>
            `;
            
            // Show notification
            this.showNotification(
                `✅ "${pageTitle}" added to knowledge base (${result.chunks_created || 1} chunks)`, 
                'success'
            );
            
        } catch (error) {
            console.error('❌ Content upload error:', error);
            resultDiv.innerHTML = `
                <div class="ai-error">
                    <h5>❌ Upload Failed</h5>
                    <p>${error.message}</p>
                    <details>
                        <summary>Troubleshooting Tips</summary>
                        <ul>
                            <li>Make sure you're on a Canvas page with content</li>
                            <li>Check that the API service is running</li>
                            <li>Try refreshing the page and trying again</li>
                            <li>Ensure the page has loaded completely</li>
                        </ul>
                    </details>
                    <small>Check browser console for technical details</small>
                </div>
            `;
        }
    }

    async askQuestion() {
        const questionInput = document.getElementById('question-input');
        const resultDiv = document.getElementById('question-result');
        const question = questionInput.value.trim();
        
        if (!question) {
            resultDiv.innerHTML = '<div class="ai-error">Please enter a question</div>';
            return;
        }
        
        resultDiv.innerHTML = '<div class="ai-loading">🤔 Thinking...</div>';
        
        try {
            const content = this.extractPageContent();
            
            const response = await fetch(`${API_BASE_URL}/ask-question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    context: content,
                    source: 'canvas_page'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div class="ai-answer-result">
                    <h5>💡 AI Answer</h5>
                    <p>${result.answer || result.response || 'No answer provided'}</p>
                    
                    ${result.confidence ? `
                        <p><small>Confidence: ${result.confidence}</small></p>
                    ` : ''}
                </div>
            `;
            
            questionInput.value = '';
        } catch (error) {
            console.error('Question error:', error);
            resultDiv.innerHTML = `
                <div class="ai-error">
                    ❌ Failed to get answer: ${error.message}
                    <br><small>Check console for details</small>
                </div>
            `;
        }
    }

    extractPageContent() {
        console.log('🔍 Extracting comprehensive page content...');
        
        let extractedContent = {
            title: '',
            headers: [],
            mainContent: '',
            metadata: {}
        };
        
        // 1. Extract page title and main heading
        extractedContent.title = document.title || '';
        
        // Find the main page heading
        const mainHeadings = document.querySelectorAll('h1, .page-title, .assignment-title, .quiz-header h1, .discussion-title h1');
        if (mainHeadings.length > 0) {
            extractedContent.title = mainHeadings[0].innerText.trim() || extractedContent.title;
        }
        
        // 2. Extract all headers (h1-h6) for structure
        const allHeaders = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        extractedContent.headers = Array.from(allHeaders).map(h => ({
            level: h.tagName.toLowerCase(),
            text: h.innerText.trim()
        })).filter(h => h.text.length > 0);
        
        // 3. Comprehensive content extraction with priority-based approach
        const contentSelectors = [
            // PRIMARY CONTENT AREAS (highest priority)
            {
                selector: '.user_content',
                priority: 1,
                description: 'Main Canvas user content'
            },
            {
                selector: '.show-content',
                priority: 1,
                description: 'Canvas show content area'
            },
            {
                selector: '.assignment-description .user_content',
                priority: 1,
                description: 'Assignment descriptions'
            },
            {
                selector: '.quiz-description .user_content',
                priority: 1,
                description: 'Quiz descriptions'
            },
            {
                selector: '.discussion-section .user_content',
                priority: 1,
                description: 'Discussion content'
            },
            
            // SECONDARY CONTENT AREAS
            {
                selector: '.content-wrap',
                priority: 2,
                description: 'Canvas content wrapper'
            },
            {
                selector: '.ic-Layout-contentMain',
                priority: 2,
                description: 'Canvas main layout content'
            },
            {
                selector: '.course-content',
                priority: 2,
                description: 'Course content area'
            },
            {
                selector: 'main[role="main"]',
                priority: 2,
                description: 'Main content area'
            },
            {
                selector: '.page-content',
                priority: 2,
                description: 'Page content area'
            },
            
            // SPECIFIC CANVAS CONTENT TYPES
            {
                selector: '.wiki-page-content',
                priority: 1,
                description: 'Wiki page content'
            },
            {
                selector: '.module-sequence-footer-content',
                priority: 3,
                description: 'Module sequence content'
            },
            {
                selector: '.announcement-content',
                priority: 1,
                description: 'Announcement content'
            },
            {
                selector: '.syllabus-content',
                priority: 1,
                description: 'Syllabus content'
            }
        ];
        
        let contentParts = [];
        let foundPrimaryContent = false;
        
        // Extract content in priority order
        for (const {selector, priority, description} of contentSelectors.sort((a, b) => a.priority - b.priority)) {
            const elements = document.querySelectorAll(selector);
            
            for (const element of elements) {
                if (element && element.innerText && element.innerText.trim().length > 50) {
                    const text = element.innerText.trim();
                    
                    // Avoid duplicate content
                    const isDuplicate = contentParts.some(part => 
                        part.text.includes(text.substring(0, 100)) || 
                        text.includes(part.text.substring(0, 100))
                    );
                    
                    if (!isDuplicate) {
                        contentParts.push({
                            source: description,
                            text: text,
                            priority: priority,
                            length: text.length
                        });
                        
                        if (priority === 1) foundPrimaryContent = true;
                        
                        console.log(`✅ Found content from: ${description} (${text.length} chars)`);
                    }
                }
            }
        }
        
        // 4. Fallback: comprehensive page scan if no primary content found
        if (!foundPrimaryContent || contentParts.length === 0) {
            console.log('⚠️ No primary content found, using comprehensive scan...');
            
            // Remove scripts, styles, and navigation elements
            const elementsToIgnore = document.querySelectorAll('script, style, nav, .navigation, .breadcrumb, .header, .footer, .sidebar');
            const ignoredElements = new Set(elementsToIgnore);
            
            // Get all text from body, excluding ignored elements
            const allTextElements = document.querySelectorAll('p, div, span, td, li, dd, dt');
            
            for (const element of allTextElements) {
                // Skip if element or its parent is in ignored list
                let isIgnored = false;
                let parent = element;
                while (parent && !isIgnored) {
                    if (ignoredElements.has(parent)) {
                        isIgnored = true;
                    }
                    parent = parent.parentElement;
                }
                
                if (!isIgnored && element.innerText && element.innerText.trim().length > 20) {
                    const text = element.innerText.trim();
                    
                    // Check if this text is not already included
                    const isDuplicate = contentParts.some(part => 
                        part.text.includes(text) || text.includes(part.text.substring(0, 100))
                    );
                    
                    if (!isDuplicate) {
                        contentParts.push({
                            source: 'comprehensive scan',
                            text: text,
                            priority: 4,
                            length: text.length
                        });
                    }
                }
            }
        }
        
        // 5. Combine all content
        extractedContent.mainContent = contentParts
            .sort((a, b) => a.priority - b.priority) // Sort by priority
            .map(part => part.text)
            .join('\n\n');
        
        // 6. Extract metadata
        extractedContent.metadata = {
            url: window.location.href,
            courseId: this.extractCourseId(),
            contentType: this.detectContentType(),
            wordCount: extractedContent.mainContent.split(/\s+/).length,
            characterCount: extractedContent.mainContent.length,
            extractedSources: contentParts.map(p => p.source),
            timestamp: new Date().toISOString()
        };
        
        // 7. Build final content string with structure
        let finalContent = '';
        
        // Add title
        if (extractedContent.title) {
            finalContent += `TITLE: ${extractedContent.title}\n\n`;
        }
        
        // Add headers outline
        if (extractedContent.headers.length > 0) {
            finalContent += 'CONTENT STRUCTURE:\n';
            extractedContent.headers.forEach(header => {
                const indent = '  '.repeat(parseInt(header.level.charAt(1)) - 1);
                finalContent += `${indent}${header.text}\n`;
            });
            finalContent += '\n';
        }
        
        // Add main content
        finalContent += 'MAIN CONTENT:\n';
        finalContent += extractedContent.mainContent;
        
        console.log(`📊 Content extraction complete:
        - Title: ${extractedContent.title}
        - Headers: ${extractedContent.headers.length}
        - Content sources: ${extractedContent.metadata.extractedSources.length}
        - Word count: ${extractedContent.metadata.wordCount}
        - Character count: ${extractedContent.metadata.characterCount}`);
        
        return finalContent;
    }
    
    extractCourseId() {
        const urlMatch = window.location.href.match(/\/courses\/(\d+)/);
        return urlMatch ? urlMatch[1] : null;
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
        
        return 'page';
    }

    enhanceCanvasPages() {
        // Add AI buttons next to every linked item in Canvas
        this.addAIButtonsToLinks();
        
        // Also enhance general content areas
        this.addQuickActionsToContent();
    }

    addAIButtonsToLinks() {
        // Canvas link selectors for different types of content
        const linkSelectors = [
            // Course modules and items - MORE SPECIFIC SELECTORS
            '.ig-list .ig-row .ig-title a',              // Module items in expanded view
            '.context_module_item .item_name a',        // Module item links
            '.context_module_item .title a',            // Alternative module item titles
            '.module-item-title a',                     // Module titles
            '.content-summary a',                       // Content summary links
            '.module_item a',                           // Generic module items
            
            // Week/Module folders
            '.context_module .header .name a',          // Module header names
            '.module-header a',                         // Module headers
            '.collapsible-header a',                    // Collapsible module headers
            
            // Assignments and submissions
            '.assignment-list .assignment a',           // Assignment list
            '.assignment_title a',                      // Assignment titles
            '.assignment-name a',                       // Assignment names
            '.submission_details a',                    // Submission links
            
            // Pages and content
            '.pages .page a',                           // Course pages
            '.wiki-page-header a',                      // Page headers
            '.page-title a',                            // Page titles
            '.page-list .page a',                       // Page list items
            
            // Discussions
            '.discussion-title a',                      // Discussion topics
            '.discussion_topic .title a',              // Discussion links
            '.entry-content a[href*="discussion"]',    // Discussion references
            '.discussion-list .discussion a',          // Discussion list
            
            // Files and media
            '.file-list .file a',                       // File browser
            '.attachment a',                            // File attachments
            '.media_object_iframe a',                   // Media links
            '.file-name a',                             // File names
            '.ef-item-row .ef-name-col a',             // Enhanced file browser
            
            // Quizzes and tests
            '.quiz-list .quiz a',                       // Quiz list
            '.quiz_title a',                            // Quiz titles
            '.quiz-submission a',                       // Quiz submissions
            '.quiz-name a',                             // Quiz names
            
            // Announcements
            '.announcement .title a',                   // Announcement titles
            '.discussion-summary .title a',            // Announcement summaries
            
            // Gradebook and grades
            '.gradebook .assignment a',                 // Gradebook items
            '.grade-summary a',                         // Grade details
            
            // Calendar and events
            '.calendar-event a',                        // Calendar events
            '.event-details a',                         // Event links
            
            // Navigation and course links
            '.course-menu a[href*="/courses/"]',        // Course navigation
            '.modules .module a',                       // Module navigation
            '.navigation a[href*="instructure"]',      // General Canvas links
            
            // Additional Canvas-specific selectors
            'a[href*="/courses/"][href*="/assignments/"]',  // Assignment URLs
            'a[href*="/courses/"][href*="/pages/"]',        // Page URLs  
            'a[href*="/courses/"][href*="/quizzes/"]',      // Quiz URLs
            'a[href*="/courses/"][href*="/discussion_topics/"]', // Discussion URLs
            'a[href*="/courses/"][href*="/files/"]',        // File URLs
            'a[href*="/courses/"][href*="/modules/"]'       // Module URLs
        ];
        
        let buttonsAdded = 0;
        
        linkSelectors.forEach(selector => {
            const links = document.querySelectorAll(selector);
            links.forEach(link => {
                if (this.addAIButtonToLink(link)) {
                    buttonsAdded++;
                }
            });
        });
        
        console.log(`🤖 Added ${buttonsAdded} AI buttons to Canvas links`);
        return buttonsAdded;
    }

    addAIButtonToLink(link) {
        // Skip if button already exists
        if (link.parentElement.querySelector('.ai-link-button')) return false;
        
        // Skip external links (keep only Canvas internal links)
        const href = link.getAttribute('href');
        if (!href || (href.startsWith('http') && !href.includes('instructure.com') && !href.includes('canvas.com'))) {
            return false;
        }
        
        // Skip if link text is too short or generic
        const linkText = link.textContent.trim();
        if (linkText.length < 3 || linkText.toLowerCase() === 'home' || linkText.toLowerCase() === 'back') {
            return false;
        }
        
        // Create AI button
        const aiButton = document.createElement('button');
        aiButton.className = 'ai-link-button';
        aiButton.innerHTML = '🤖';
        aiButton.title = 'Analyze with AI Assistant';
        
        // Style the button to be compact and unobtrusive
        aiButton.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            padding: 2px 6px;
            margin-left: 8px;
            cursor: pointer;
            opacity: 0.7;
            transition: all 0.2s ease;
            vertical-align: middle;
            display: inline-block;
        `;
        
        // Add hover effects
        aiButton.addEventListener('mouseenter', () => {
            aiButton.style.opacity = '1';
            aiButton.style.transform = 'scale(1.1)';
        });
        
        aiButton.addEventListener('mouseleave', () => {
            aiButton.style.opacity = '0.7';
            aiButton.style.transform = 'scale(1)';
        });
        
        // Add click handler
        aiButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.handleLinkAnalysis(link, aiButton);
        });
        
        // Insert button after the link
        if (link.parentElement) {
            link.parentElement.insertBefore(aiButton, link.nextSibling);
            return true;
        }
        return false;
    }

    setupDynamicContentObserver() {
        // Observer for dynamically loaded content (Canvas modules, etc.)
        const observer = new MutationObserver((mutations) => {
            let shouldRerun = false;
            
            mutations.forEach((mutation) => {
                // Check if new nodes were added
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        // Check if the added node contains Canvas content
                        if (node.nodeType === 1) { // Element node
                            const hasCanvasContent = node.querySelector && (
                                node.querySelector('.context_module_item') ||
                                node.querySelector('.ig-row') ||
                                node.querySelector('.assignment') ||
                                node.querySelector('.discussion') ||
                                node.querySelector('.quiz') ||
                                node.querySelector('.page') ||
                                node.matches && (
                                    node.matches('.context_module_item') ||
                                    node.matches('.ig-row') ||
                                    node.matches('.assignment') ||
                                    node.matches('.discussion') ||
                                    node.matches('.quiz') ||
                                    node.matches('.page')
                                )
                            );
                            
                            if (hasCanvasContent) {
                                shouldRerun = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldRerun) {
                console.log('🔄 Canvas content changed, re-adding AI buttons...');
                // Delay slightly to let Canvas finish rendering
                setTimeout(() => {
                    this.enhanceCanvasPages();
                }, 500);
            }
        });
        
        // Observe the main content area for changes
        const targetSelectors = [
            '#content',
            '.ic-Layout-contentMain',
            '#main',
            '.course-content',
            '.modules',
            '.context_modules'
        ];
        
        targetSelectors.forEach(selector => {
            const target = document.querySelector(selector);
            if (target) {
                observer.observe(target, {
                    childList: true,
                    subtree: true,
                    attributes: false
                });
                console.log(`📡 Observing ${selector} for dynamic content changes`);
            }
        });
        
        // Store observer reference for cleanup if needed
        this.contentObserver = observer;
    }

    async handleLinkAnalysis(link, button) {
        const originalText = button.innerHTML;
        button.innerHTML = '⏳';
        button.disabled = true;
        
        try {
            // Get link information
            const linkText = link.textContent.trim();
            const linkHref = link.getAttribute('href');
            const linkContext = this.getLinkContext(link);
            const contentType = this.detectContentType(linkHref, linkText);
            
            // Show brief processing notification
            this.showNotification(`Processing: ${linkText}`, 'info');
            
            // Directly ingest the content into the AI knowledge base
            await this.ingestContentToKnowledgeBase(link, linkText, linkHref, contentType, linkContext);
            
        } catch (error) {
            console.error('Content ingestion error:', error);
            // Show more specific error message
            if (error.message.includes('not found') || error.message.includes('404')) {
                this.showNotification('API is updating - please try again in 1-2 minutes', 'error');
            } else if (error.message.includes('fetch')) {
                this.showNotification('Network error - check internet connection', 'error');
            } else {
                this.showNotification('Failed to process content - check console for details', 'error');
            }
        } finally {
            button.innerHTML = '✅'; // Show success
            button.disabled = false;
            
            // Revert to original after delay
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        }
    }

    async ingestContentToKnowledgeBase(link, linkText, linkHref, contentType, context) {
        try {
            // Attempt to fetch content from the Canvas page
            let content = '';
            
            // If it's a relative URL, make it absolute
            let fullUrl = linkHref;
            if (linkHref.startsWith('/')) {
                fullUrl = window.location.origin + linkHref;
            }
            
            console.log(`Attempting to extract content for: ${linkText} (${contentType})`);
            
            // For Canvas pages, try to extract content directly if possible
            if (linkHref.includes('/pages/') || linkHref.includes('/assignments/') || linkHref.includes('/discussion_topics/')) {
                content = await this.fetchCanvasContent(fullUrl, linkText, contentType);
                
                // If extraction returned null (invalid content), try fallback
                if (!content) {
                    console.log('Direct content extraction failed, trying alternative method');
                    content = this.buildContentFromMetadata(linkText, linkHref, contentType, context);
                }
            } else {
                // For other content types, use metadata and context
                content = this.buildContentFromMetadata(linkText, linkHref, contentType, context);
            }
            
            // Final validation before sending
            if (!this.isValidContent(content)) {
                console.warn('Content validation failed, enhancing with current page context');
                const pageContext = this.extractCurrentPageContext();
                content = `${content}\n\nPage Context:\n${pageContext}`;
            }
            
            console.log(`Sending content to API (${content.length} characters):`, content.substring(0, 200) + '...');
            
            // Send to knowledge base ingestion endpoint
            const response = await fetch(`${API_BASE_URL}/ingest-content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: linkText,
                    content: content,
                    source: 'canvas_chrome_extension',  // Clear source identifier
                    url: fullUrl,
                    content_type: contentType,
                    context: context,
                    course_id: this.extractCourseId(),
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error(`Endpoint not found - API may still be deploying. Please try again in a minute.`);
                } else {
                    throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
                }
            }
            
            const result = await response.json();
            
            // Show success with brief summary
            this.showNotification(
                `✅ Added "${linkText}" to knowledge base (${result.chunks_created || 1} chunks)`, 
                'success'
            );
            
            console.log(`📚 Successfully ingested content: ${linkText}`, result);
            
        } catch (error) {
            console.error('Knowledge base ingestion failed:', error);
            
            // Show user-friendly error
            this.showNotification(
                `❌ Failed to add "${linkText}": ${error.message}`, 
                'error'
            );
            
            throw error;
        }
    }

    // Helper method to extract current page context as fallback
    extractCurrentPageContext() {
        const title = document.title;
        const headings = Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent.trim()).slice(0, 5);
        const courseInfo = this.extractCourseInfo();
        
        return `Page: ${title}\nHeadings: ${headings.join(', ')}\nCourse: ${courseInfo}`;
    }

    extractCourseInfo() {
        // Try to get course name from various Canvas elements
        const courseSelectors = [
            '.ic-app-header__main-navigation .ic-app-header__menu-list-item.ic-app-header__menu-list-item--active',
            '.course-title',
            '[data-testid="course-name"]',
            '.course_name'
        ];
        
        for (const selector of courseSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                return this.cleanTextContent(element.textContent);
            }
        }
        
        return `Course ID: ${this.extractCourseId()}`;
    }

    async fetchCanvasContent(url, linkText, contentType) {
        try {
            // Wait for Canvas page to fully load before attempting content extraction
            await this.waitForCanvasContentLoad();
            
            // For same-origin Canvas content, try to fetch directly
            if (url.includes(window.location.hostname)) {
                const response = await fetch(url, {
                    credentials: 'same-origin',  // Include Canvas session cookies
                    headers: {
                        'Accept': 'text/html,application/xhtml+xml',
                        'X-Requested-With': 'XMLHttpRequest'  // Canvas AJAX header
                    }
                });
                
                if (response.ok) {
                    const html = await response.text();
                    const extractedContent = this.extractContentFromHTML(html, contentType);
                    
                    // Validate content quality - don't return JavaScript errors
                    if (this.isValidContent(extractedContent)) {
                        return extractedContent;
                    } else {
                        console.log('Fetched content appears to be error page, using fallback');
                    }
                }
            }
            
            // Fallback: Use current page context if we can't fetch valid content
            return this.buildContentFromCurrentPage(linkText, contentType);
            
        } catch (error) {
            console.log('Direct fetch failed, using fallback content extraction:', error.message);
            return this.buildContentFromCurrentPage(linkText, contentType);
        }
    }

    // New method to wait for Canvas content to load
    async waitForCanvasContentLoad() {
        return new Promise((resolve) => {
            // Check if Canvas content indicators are present
            const checkCanvasLoaded = () => {
                const canvasIndicators = [
                    '.ic-Layout-contentMain',
                    '.show-content',
                    '.user_content',
                    '#main',
                    '[data-testid]'  // Canvas often uses test IDs
                ];
                
                const hasCanvasContent = canvasIndicators.some(selector => 
                    document.querySelector(selector)
                );
                
                // Also check that we're not seeing error messages
                const hasJSError = document.body.textContent.includes('You need to have JavaScript enabled');
                
                if (hasCanvasContent && !hasJSError) {
                    resolve();
                } else {
                    setTimeout(checkCanvasLoaded, 500);  // Check again in 500ms
                }
            };
            
            // Start checking immediately, but timeout after 5 seconds
            checkCanvasLoaded();
            setTimeout(resolve, 5000);  // Don't wait forever
        });
    }

    // New method to validate content quality
    isValidContent(content) {
        if (!content || typeof content !== 'string' || content.trim().length < 50) {
            return false;
        }
        
        // Check for JavaScript or error-related content that should be filtered out
        const errorPatterns = [
            /you need to have javascript enabled/i,
            /javascript is disabled/i,
            /enable javascript/i,
            /javascript required/i,
            /javascript must be enabled/i,
            /browser does not support javascript/i,
            /this page requires javascript/i,
            /please enable javascript/i,
            /error.*occurred/i,
            /page not found/i,
            /access denied/i,
            /unauthorized/i,
            /loading\.\.\./i,
            /please wait/i,
            /^[\s\n]*$/, // Only whitespace
            /^[\s\n]*loading[\s\n]*$/i,
            /^[\s\n]*error[\s\n]*$/i,
            /content could not be extracted/i
        ];
        
        const contentLower = content.toLowerCase();
        for (const pattern of errorPatterns) {
            if (pattern.test(contentLower)) {
                console.warn('Invalid content detected:', pattern.toString());
                return false;
            }
        }
        
        // Check for meaningful Canvas/educational content indicators
        const goodContentPatterns = [
            /assignment/i,
            /discussion/i,
            /reading/i,
            /course/i,
            /lesson/i,
            /chapter/i,
            /quiz/i,
            /exam/i,
            /homework/i,
            /project/i,
            /syllabus/i,
            /instructions/i,
            /requirements/i,
            /objective/i,
            /learning/i,
            /submit/i,
            /due date/i,
            /points/i,
            /grade/i,
            /description/i,
            /module/i,
            /lecture/i,
            /tutorial/i
        ];
        
        // Content should have some educational indicators
        const hasEducationalContent = goodContentPatterns.some(pattern => pattern.test(contentLower));
        
        // Content should have reasonable text density (not just navigation)
        const words = content.split(/\s+/).filter(word => word.length > 2);
        const hasGoodTextDensity = words.length >= 20;
        
        // Either substantial content OR educational keywords
        return hasEducationalContent || (hasGoodTextDensity && content.length > 200);
    }

    extractContentFromHTML(html, contentType) {
        // Create a temporary DOM to parse the fetched content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Check for error pages first
        const bodyText = doc.body.textContent.toLowerCase();
        if (bodyText.includes('you need to have javascript enabled') || 
            bodyText.includes('javascript is not enabled') ||
            bodyText.includes('access denied') ||
            bodyText.includes('unauthorized')) {
            return null;  // Signal that this is an error page
        }
        
        // Extract main content based on Canvas structure - more comprehensive selectors
        const contentSelectors = [
            // Primary content areas
            '.show-content .user_content',        // Main page content
            '.assignment-description .user_content',  // Assignment descriptions
            '.discussion-entry .message .user_content',  // Discussion content
            '.quiz-description .user_content',    // Quiz descriptions
            
            // Fallback selectors
            '.show-content',
            '.user_content',
            '.assignment-description', 
            '.discussion-entry',
            '.quiz-description',
            '.page-content',
            '.content-wrap',
            '.ic-Layout-contentMain .content',
            
            // Course-specific content
            '.course-syllabus',
            '.module-content',
            '.lesson-content'
        ];
        
        let extractedContent = '';
        let title = '';
        
        // Get title
        const titleElement = doc.querySelector('h1, .page-title, .assignment-title, .discussion-title');
        if (titleElement) {
            title = titleElement.textContent.trim() + '\n\n';
        }
        
        // Try each selector until we find substantial content
        for (const selector of contentSelectors) {
            const element = doc.querySelector(selector);
            if (element) {
                const content = this.cleanTextContent(element.textContent);
                if (content.length > 100) {  // Only use if substantial
                    extractedContent = content;
                    break;
                }
            }
        }
        
        // If no specific content found, try to get structured information
        if (!extractedContent.trim()) {
            // Get any headings and paragraphs
            const headings = doc.querySelectorAll('h1, h2, h3, h4, h5, h6');
            const paragraphs = doc.querySelectorAll('p, li, .content p');
            
            let structuredContent = '';
            headings.forEach(h => {
                const text = this.cleanTextContent(h.textContent);
                if (text.length > 0) {
                    structuredContent += `${text}\n`;
                }
            });
            
            paragraphs.forEach(p => {
                const text = this.cleanTextContent(p.textContent);
                if (text.length > 20) {  // Only meaningful paragraphs
                    structuredContent += `${text}\n\n`;
                }
            });
            
            extractedContent = structuredContent;
        }
        
        const fullContent = title + extractedContent;
        
        // Final validation
        if (this.isValidContent(fullContent)) {
            return fullContent.trim();
        }
        
        return null;  // Signal extraction failed
    }

    // Helper method to clean and normalize text content
    cleanTextContent(text) {
        if (!text) return '';
        
        return text
            .replace(/\s+/g, ' ')        // Normalize whitespace
            .replace(/\n\s*\n/g, '\n')   // Remove excessive line breaks
            .trim();
    }

    // Filter out navigation and UI content that shouldn't be in the knowledge base
    filterNavigationContent(content) {
        const navigationPatterns = [
            /skip to (?:main )?content/gi,
            /main navigation/gi,
            /course navigation/gi,
            /breadcrumb/gi,
            /menu/gi,
            /toggle.*navigation/gi,
            /^home\s*$/gim,
            /^dashboard\s*$/gim,
            /^modules\s*$/gim,
            /^assignments\s*$/gim,
            /^discussions\s*$/gim,
            /^grades\s*$/gim,
            /^calendar\s*$/gim,
            /^inbox\s*$/gim,
            /^help\s*$/gim,
            /^logout\s*$/gim,
            /^profile\s*$/gim,
            /^settings\s*$/gim
        ];
        
        let filtered = content;
        for (const pattern of navigationPatterns) {
            filtered = filtered.replace(pattern, '');
        }
        
        return filtered.trim();
    }

    buildContentFromCurrentPage(linkText, contentType) {
        // Build content from available context on current page
        console.log('Building content from current page for:', linkText);
        
        // First, try to find the actual content area
        const contentSelectors = [
            '.show-content',
            '.user_content', 
            '.ic-Layout-contentMain',
            '.content-wrap',
            'main',
            '#content'
        ];
        
        let pageContent = '';
        
        // Try to get meaningful content from specific areas
        for (const selector of contentSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                const content = this.cleanTextContent(element.textContent);
                if (this.isValidContent(content)) {
                    pageContent = content;
                    break;
                }
            }
        }
        
        // If no good content area found, be more selective about body content
        if (!pageContent) {
            // Avoid using full body content which often contains navigation and errors
            const contentArea = document.querySelector('.ic-app-main-content, .ic-Layout-wrapper');
            if (contentArea) {
                pageContent = this.cleanTextContent(contentArea.textContent);
            } else {
                // Last resort: use body but filter out common navigation text
                const bodyText = document.body.textContent;
                const filtered = this.filterNavigationContent(bodyText);
                pageContent = this.cleanTextContent(filtered);
            }
        }
        
        // Validate the content before using it
        if (!this.isValidContent(pageContent)) {
            console.warn('Current page content appears to be invalid, using metadata only');
            return `Title: ${linkText}\nType: ${contentType}\nNote: Content extraction failed - page may require JavaScript or special permissions`;
        }
        
        // Find context around the link
        const linkIndex = pageContent.indexOf(linkText);
        let contextContent = '';
        
        if (linkIndex !== -1) {
            const start = Math.max(0, linkIndex - 500);
            const end = Math.min(pageContent.length, linkIndex + linkText.length + 500);
            contextContent = pageContent.substring(start, end);
        } else {
            // Use first part of page content as context
            contextContent = pageContent.substring(0, 1000);
        }
        
        return `Title: ${linkText}\nType: ${contentType}\nContent: ${contextContent}`;
    }

    // Helper method to filter out navigation and header/footer content
    filterNavigationContent(text) {
        const navigationPatterns = [
            /dashboard.*?courses/gi,
            /navigation.*?menu/gi,
            /skip to.*?content/gi,
            /canvas.*?logo/gi,
            /help.*?support/gi,
            /logout.*?profile/gi
        ];
        
        let filtered = text;
        navigationPatterns.forEach(pattern => {
            filtered = filtered.replace(pattern, '');
        });
        
        return filtered;
    }

    buildContentFromMetadata(linkText, linkHref, contentType, context) {
        // Build structured content from available metadata
        let content = `Title: ${linkText}\n`;
        content += `Type: ${contentType}\n`;
        content += `URL: ${linkHref}\n`;
        
        if (context) {
            content += `Module: ${context.title || 'Unknown'}\n`;
            content += `Description: ${context.description || 'No description available'}\n`;
        }
        
        // Add any visible content near the link
        const linkElement = document.querySelector(`a[href="${linkHref}"]`);
        if (linkElement) {
            const parent = linkElement.closest('.context_module_item, .assignment, .discussion, .quiz');
            if (parent) {
                const description = parent.querySelector('.description, .summary, .points_possible');
                if (description) {
                    content += `Additional Info: ${description.textContent.trim()}\n`;
                }
            }
        }
        
        return content;
    }

    extractCourseId() {
        // Extract Canvas course ID from URL
        const match = window.location.pathname.match(/\/courses\/(\d+)/);
        return match ? match[1] : 'unknown';
    }

    getLinkContext(link) {
        // Get surrounding context to understand what this link is about
        const parent = link.closest('.context_module_item, .assignment, .discussion, .page, .quiz, .announcement');
        if (parent) {
            return {
                type: this.getElementType(parent),
                title: parent.querySelector('.title, .name, h1, h2, h3')?.textContent?.trim() || '',
                description: parent.querySelector('.description, .summary')?.textContent?.trim() || ''
            };
        }
        return null;
    }

    getElementType(element) {
        const classNames = element.className;
        if (classNames.includes('assignment')) return 'assignment';
        if (classNames.includes('discussion')) return 'discussion';
        if (classNames.includes('quiz')) return 'quiz';
        if (classNames.includes('page')) return 'page';
        if (classNames.includes('announcement')) return 'announcement';
        if (classNames.includes('module')) return 'module';
        return 'content';
    }

    detectContentType(href, text) {
        if (!href) return 'unknown';
        
        if (href.includes('/assignments/')) return 'assignment';
        if (href.includes('/discussion_topics/')) return 'discussion';
        if (href.includes('/quizzes/')) return 'quiz';
        if (href.includes('/pages/')) return 'page';
        if (href.includes('/announcements/')) return 'announcement';
        if (href.includes('/files/')) return 'file';
        if (href.includes('/modules/')) return 'module';
        if (href.includes('/grades')) return 'grades';
        
        // Text-based detection
        const lowerText = text.toLowerCase();
        if (lowerText.includes('assignment') || lowerText.includes('homework')) return 'assignment';
        if (lowerText.includes('discussion') || lowerText.includes('forum')) return 'discussion';
        if (lowerText.includes('quiz') || lowerText.includes('test') || lowerText.includes('exam')) return 'quiz';
        if (lowerText.includes('reading') || lowerText.includes('chapter')) return 'reading';
        if (lowerText.includes('lecture') || lowerText.includes('video')) return 'lecture';
        
        return 'content';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : '#2196F3'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 12px;
            z-index: 10004;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 4000);
    }

    addQuickActionsToContent() {
        // Add quick action buttons to Canvas content areas (existing functionality)
        const contentElements = document.querySelectorAll('.user_content, .show-content');
        
        contentElements.forEach(element => {
            if (!element.querySelector('.ai-quick-actions')) {
                const quickActions = document.createElement('div');
                quickActions.className = 'ai-quick-actions';
                quickActions.innerHTML = `
                    <button class="ai-quick-btn" data-action="summarize">
                        📝 Summarize
                    </button>
                    <button class="ai-quick-btn" data-action="questions">
                        ❓ Generate Questions
                    </button>
                `;
                
                element.insertBefore(quickActions, element.firstChild);
                
                quickActions.addEventListener('click', (e) => {
                    if (e.target.classList.contains('ai-quick-btn')) {
                        const action = e.target.dataset.action;
                        this.handleQuickAction(action, element);
                    }
                });
            }
        });
    }

    async handleQuickAction(action, contentElement) {
        const content = contentElement.innerText;
        
        if (action === 'summarize') {
            // Open panel and trigger analysis
            this.createAssistantPanel();
            setTimeout(() => this.analyzeCurrentPage(), 100);
        } else if (action === 'questions') {
            // Generate study questions
            this.generateStudyQuestions(content);
        }
    }

    async generateStudyQuestions(content) {
        try {
            const response = await fetch(`${API_BASE_URL}/ask-question`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: "Generate 5 study questions based on this content",
                    context: content,
                    source: 'canvas_page'
                })
            });
            
            const result = await response.json();
            
            // Show questions in a popup
            const popup = document.createElement('div');
            popup.className = 'ai-questions-popup';
            popup.innerHTML = `
                <div class="popup-content">
                    <h4>📚 Study Questions</h4>
                    <div class="questions-content">${result.answer || result.response}</div>
                    <button class="popup-close">Close</button>
                </div>
            `;
            
            document.body.appendChild(popup);
            
            popup.querySelector('.popup-close').addEventListener('click', () => popup.remove());
            
            // Auto remove after 10 seconds
            setTimeout(() => popup.remove(), 10000);
            
        } catch (error) {
            console.error('Questions generation error:', error);
        }
    }
}

// Initialize the AI assistant when the script loads
const aiAssistant = new CanvasAIAssistant();

// Enhanced navigation change detection for Canvas SPA
let lastUrl = location.href;
let lastPathname = location.pathname;

// Multiple methods to detect Canvas navigation changes
const navigationObserver = new MutationObserver(() => {
    const url = location.href;
    const pathname = location.pathname;
    
    if (url !== lastUrl || pathname !== lastPathname) {
        console.log(`📍 Canvas navigation detected: ${pathname}`);
        lastUrl = url;
        lastPathname = pathname;
        
        // Re-enhance pages after navigation with multiple delays
        setTimeout(() => aiAssistant.enhanceCanvasPages(), 500);   // Quick enhancement
        setTimeout(() => aiAssistant.enhanceCanvasPages(), 1500);  // Medium delay
        setTimeout(() => aiAssistant.enhanceCanvasPages(), 3000);  // Longer delay for slow loading
    }
});

// Observe document changes for navigation
navigationObserver.observe(document, { subtree: true, childList: true });

// Also listen for Canvas-specific events
window.addEventListener('popstate', () => {
    console.log('📍 Popstate navigation detected');
    setTimeout(() => aiAssistant.enhanceCanvasPages(), 1000);
});

// Listen for hash changes
window.addEventListener('hashchange', () => {
    console.log('📍 Hash navigation detected');
    setTimeout(() => aiAssistant.enhanceCanvasPages(), 500);
});

// Additional Canvas-specific event listeners
document.addEventListener('click', (e) => {
    // Check if clicked element is a Canvas navigation link
    const link = e.target.closest('a');
    if (link && link.href && link.href.includes('/courses/')) {
        console.log('📍 Canvas link clicked, scheduling enhancement...');
        // Enhancement after click with delays
        setTimeout(() => aiAssistant.enhanceCanvasPages(), 1000);
        setTimeout(() => aiAssistant.enhanceCanvasPages(), 2500);
    }
});
