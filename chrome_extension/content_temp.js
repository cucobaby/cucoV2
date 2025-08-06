// Canvas AI Assistant - Simple Content Scraper
// Adds a single "Add Content" button to Canvas pages

console.log('🤖 Canvas AI Assistant initialized');
console.log('📍 URL:', window.location.href);

const API_BASE_URL = 'https://cucov2-production.up.railway.app';

class CanvasContentScraper {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    async init() {
        if (this.isInitialized) return;
        
        console.log('🎯 Initializing Canvas Content Scraper...');
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupButton());
        } else {
            this.setupButton();
        }
        
        this.isInitialized = true;
    }

    setupButton() {
        console.log('🔧 Setting up Add Content button...');
        
        // Only add button if we're on a Canvas course page with content
        if (this.isCanvasContentPage()) {
            this.addContentButton();
        } else {
            console.log('📄 Not a Canvas content page, skipping button');
        }
    }

    isCanvasContentPage() {
        const url = window.location.href;
        
        // Check if we're in a Canvas course
        const isInCourse = url.includes('/courses/');
        
        // Check for content-rich pages
        const contentPages = [
            '/pages/',
            '/assignments/',
            '/quizzes/',
            '/discussion_topics/',
            '/modules/',
            '/announcements/',
            '/syllabus'
        ];
        
        const isContentPage = contentPages.some(pattern => url.includes(pattern));
        
        // Also check if page has educational content
        const hasEducationalContent = this.detectEducationalContent();
        
        const shouldShow = isInCourse && (isContentPage || hasEducationalContent);
        
        console.log(`🔍 Page check: inCourse=${isInCourse}, contentPage=${isContentPage}, hasEducation=${hasEducationalContent}, result=${shouldShow}`);
        
        return shouldShow;
    }

    detectEducationalContent() {
        // Look for Canvas content containers
        const contentSelectors = [
            '.user_content',
            '.show-content',
            '.assignment-description',
            '.page-content',
            '.wiki-page-content',
            '.course-content'
        ];
        
        for (const selector of contentSelectors) {
            const element = document.querySelector(selector);
            if (element && element.textContent.trim().length > 100) {
                console.log(`✅ Found educational content via: ${selector}`);
                return true;
            }
        }
        
        // Check for educational keywords
        const pageText = document.body.textContent.toLowerCase();
        const educationalKeywords = [
            'study guide', 'learning objectives', 'assignment', 'quiz',
            'chapter', 'lesson', 'vocabulary', 'definition'
        ];
        
        const foundKeywords = educationalKeywords.filter(keyword => 
            pageText.includes(keyword)
        );
        
        if (foundKeywords.length >= 2) {
            console.log(`✅ Found educational keywords: ${foundKeywords.join(', ')}`);
            return true;
        }
        
        return false;
    }

    addContentButton() {
        // Remove existing button if present
        const existingButton = document.getElementById('canvas-add-content-btn');
        if (existingButton) {
            existingButton.remove();
        }

        // Find the best place to add the button
        const targetContainer = this.findButtonContainer();
        if (!targetContainer) {
            console.log('⚠️ No suitable container found for button');
            return;
        }

        // Create the button
        const button = document.createElement('div');
        button.id = 'canvas-add-content-btn';
        button.className = 'canvas-add-content-button';
        
        button.innerHTML = `
            <div class="button-content">
                <div class="button-icon">📚</div>
                <div class="button-text">
                    <strong>Add Content</strong>
                    <span>Upload this page to AI knowledge base</span>
                </div>
            </div>
        `;

        // Add click handler
        button.addEventListener('click', () => this.handleAddContent());

        // Insert the button
        if (targetContainer.firstChild) {
            targetContainer.insertBefore(button, targetContainer.firstChild);
        } else {
            targetContainer.appendChild(button);
        }

        // Add styles
        this.addButtonStyles();

        console.log('✅ Add Content button added successfully');
    }

    findButtonContainer() {
        // Try to find the best container for the button
        const candidates = [
            '.user_content',
            '.show-content',
            '.assignment-description',
            '.page-content',
            '.wiki-page-content',
            '#content',
            '.ic-Layout-contentMain',
            'main[role="main"]',
            '.content-wrap'
        ];

        for (const selector of candidates) {
            const container = document.querySelector(selector);
            if (container && container.textContent.trim().length > 100) {
                console.log(`✅ Found button container: ${selector}`);
                return container;
            }
        }

        // Fallback: create container at top of page
        const fallback = document.createElement('div');
        fallback.style.cssText = 'margin: 16px; padding: 0;';
        
        const contentArea = document.querySelector('#content') || 
                           document.querySelector('main') || 
                           document.body;
        
        if (contentArea.firstChild) {
            contentArea.insertBefore(fallback, contentArea.firstChild);
        } else {
            contentArea.appendChild(fallback);
        }
        
        console.log('✅ Created fallback container');
        return fallback;
    }

    addButtonStyles() {
        // Only add styles once
        if (document.getElementById('canvas-content-styles')) {
            return;
        }

        const styles = document.createElement('style');
        styles.id = 'canvas-content-styles';
        styles.textContent = `
            .canvas-add-content-button {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 16px 20px;
                margin: 16px 0;
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
                transition: all 0.3s ease;
                border: none;
                font-family: inherit;
                max-width: 400px;
            }

            .canvas-add-content-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
                background: linear-gradient(135deg, #45a049 0%, #4CAF50 100%);
            }

            .button-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .button-icon {
                font-size: 24px;
                background: rgba(255, 255, 255, 0.2);
                padding: 8px;
                border-radius: 50%;
                min-width: 40px;
                text-align: center;
            }

            .button-text {
                flex: 1;
            }

            .button-text strong {
                display: block;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 4px;
            }

            .button-text span {
                font-size: 13px;
                opacity: 0.9;
                display: block;
            }

            .canvas-add-content-button.loading {
                opacity: 0.7;
                cursor: not-allowed;
            }

            .canvas-add-content-button.success {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            }

            .canvas-add-content-button.error {
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            }
        `;

        document.head.appendChild(styles);
    }

    async handleAddContent() {
        const button = document.getElementById('canvas-add-content-btn');
        const buttonText = button.querySelector('.button-text');
        
        // Show loading state
        button.classList.add('loading');
        buttonText.innerHTML = `
            <strong>Processing...</strong>
            <span>Extracting content from page...</span>
        `;

        try {
            console.log('📚 Starting content extraction...');
            
            // Extract content from the page
            const content = this.extractPageContent();
            
            if (!content || content.trim().length < 50) {
                throw new Error('No significant content found on this page');
            }

            // Get page info
            const pageTitle = this.getPageTitle();
            const contentType = this.getContentType();
            
            console.log(`📤 Uploading: "${pageTitle}" (${content.length} characters)`);

            // Upload to knowledge base
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
                throw new Error(`Upload failed: ${response.status}`);
            }

            const result = await response.json();
            console.log('✅ Content uploaded successfully:', result);

            // Show success state
            button.classList.remove('loading');
            button.classList.add('success');
            buttonText.innerHTML = `
                <strong>✅ Content Added!</strong>
                <span>Created ${result.chunks_created || 1} chunks</span>
            `;

            // Reset button after 3 seconds
            setTimeout(() => {
                button.classList.remove('success');
                buttonText.innerHTML = `
                    <strong>Add Content</strong>
                    <span>Upload this page to AI knowledge base</span>
                `;
            }, 3000);

        } catch (error) {
            console.error('❌ Content upload error:', error);
            
            // Show error state
            button.classList.remove('loading');
            button.classList.add('error');
            buttonText.innerHTML = `
                <strong>❌ Upload Failed</strong>
                <span>${error.message}</span>
            `;

            // Reset button after 4 seconds
            setTimeout(() => {
                button.classList.remove('error');
                buttonText.innerHTML = `
                    <strong>Add Content</strong>
                    <span>Upload this page to AI knowledge base</span>
                `;
            }, 4000);
        }
    }

    extractPageContent() {
        console.log('🔍 Extracting educational content...');
        
        // Get page title
        const title = this.getPageTitle();
        
        // Extract main content from Canvas content areas
        const contentSelectors = [
            '.user_content',
            '.show-content',
            '.assignment-description',
            '.page-content',
            '.wiki-page-content',
            '.course-content',
            '.syllabus-content',
            '.announcement-content'
        ];

        let extractedContent = [];
        
        // Extract from priority selectors
        for (const selector of contentSelectors) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = this.cleanText(element.innerText);
                if (text && text.length > 50) {
                    extractedContent.push(text);
                    console.log(`✅ Extracted from ${selector}: ${text.length} chars`);
                }
            });
        }

        // If no content found, try broader extraction
        if (extractedContent.length === 0) {
            console.log('⚠️ No priority content found, trying broader extraction...');
            
            const mainContent = document.querySelector('main') || 
                               document.querySelector('#content') || 
                               document.querySelector('.ic-Layout-contentMain');
            
            if (mainContent) {
                const text = this.cleanText(mainContent.innerText);
                if (text && text.length > 100) {
                    extractedContent.push(text);
                    console.log(`✅ Extracted from main content: ${text.length} chars`);
                }
            }
        }

        // Build final content
        let finalContent = '';
        if (title) {
            finalContent += `TITLE: ${title}\n\n`;
        }
        
        finalContent += 'CONTENT:\n';
        finalContent += extractedContent.join('\n\n');

        console.log(`📊 Final content: ${finalContent.length} characters`);
        return finalContent;
    }

    cleanText(text) {
        if (!text) return '';
        
        return text
            .replace(/\s+/g, ' ') // Normalize whitespace
            .replace(/\n\s*\n/g, '\n') // Remove excessive line breaks
            .trim();
    }

    getPageTitle() {
        // Try multiple strategies to get the best title
        const titleSources = [
            () => document.querySelector('h1')?.innerText?.trim(),
            () => document.querySelector('.page-title')?.innerText?.trim(),
            () => document.querySelector('.assignment-title')?.innerText?.trim(),
            () => document.title?.trim()
        ];

        for (const getTitleFn of titleSources) {
            const title = getTitleFn();
            if (title && title.length > 3 && title.length < 200) {
                return title;
            }
        }

        return document.title || 'Canvas Page';
    }

    getContentType() {
        const url = window.location.href;
        
        if (url.includes('/assignments/')) return 'assignment';
        if (url.includes('/quizzes/')) return 'quiz';
        if (url.includes('/discussion_topics/')) return 'discussion';
        if (url.includes('/pages/')) return 'page';
        if (url.includes('/modules/')) return 'module';
        if (url.includes('/announcements/')) return 'announcement';
        if (url.includes('/syllabus')) return 'syllabus';
        
        return 'page';
    }

    extractCourseId() {
        const urlMatch = window.location.href.match(/\/courses\/(\d+)/);
        return urlMatch ? urlMatch[1] : null;
    }
}

// Initialize the content scraper
console.log('🚀 Creating Canvas Content Scraper...');
window.canvasContentScraper = new CanvasContentScraper();
console.log('✅ Canvas Content Scraper initialized');
