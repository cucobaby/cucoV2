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
                            📄 Analyze Entire Page
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
        resultDiv.innerHTML = '<div class="ai-loading">🔄 Analyzing content...</div>';
        
        try {
            // Extract page content
            const content = this.extractPageContent();
            
            const response = await fetch(`${API_BASE_URL}/analyze-content`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    source: 'canvas_page',
                    url: window.location.href
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            resultDiv.innerHTML = `
                <div class="ai-analysis-result">
                    <h5>📊 Analysis Summary</h5>
                    <p>${result.summary || 'Content analyzed successfully'}</p>
                    
                    ${result.key_concepts ? `
                        <h5>🔑 Key Concepts</h5>
                        <ul>
                            ${result.key_concepts.map(concept => `<li>${concept}</li>`).join('')}
                        </ul>
                    ` : ''}
                    
                    ${result.difficulty_level ? `
                        <p><strong>Difficulty:</strong> ${result.difficulty_level}</p>
                    ` : ''}
                </div>
            `;
        } catch (error) {
            console.error('Analysis error:', error);
            resultDiv.innerHTML = `
                <div class="ai-error">
                    ❌ Analysis failed: ${error.message}
                    <br><small>Check console for details</small>
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
        // Extract text content from Canvas page
        const contentAreas = [
            '.show-content',
            '.content-wrap',
            '.ic-Layout-contentMain',
            '.user_content',
            '.course-content',
            'main',
            '#content'
        ];
        
        let content = '';
        
        for (const selector of contentAreas) {
            const element = document.querySelector(selector);
            if (element) {
                content += element.innerText + '\n';
            }
        }
        
        // Fallback to page title and basic content
        if (!content.trim()) {
            content = document.title + '\n' + document.body.innerText.slice(0, 5000);
        }
        
        return content.slice(0, 10000); // Limit content size
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
