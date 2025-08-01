# Canvas AI Assistant - Chrome Extension

🤖 **AI-powered educational assistant for Canvas LMS**

## 📁 Extension Structure

Your Canvas AI Assistant Chrome extension is now complete with the following files:

```
chrome_extension/
├── manifest.json          # Extension configuration
├── content.js            # Main Canvas integration script
├── background.js         # Service worker for extension lifecycle
├── popup.html           # Extension popup interface
├── popup.js             # Popup functionality
├── styles.css           # Canvas page styling
├── popup-styles.css     # Popup interface styling
├── icons/               # Extension icons (placeholder)
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md           # This file
```

## 🚀 **Installation Instructions**

### Step 1: Load Extension in Chrome
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select your `chrome_extension` folder: `e:\VSCODE\cucoV2\chrome_extension`

### Step 2: Configure Extension
1. Click the Canvas AI Assistant icon in your Chrome toolbar
2. Verify API connection shows "Connected" status
3. Adjust settings as needed:
   - ✅ Enable AI Assistant
   - ⚙️ Auto-analyze pages (optional)
   - 🔧 Show quick actions

### Step 3: Test on Canvas
1. Navigate to any Canvas page (e.g., `*.instructure.com` or `*.canvas.com`)
2. Look for the floating 🤖 AI Assistant button (bottom-right)
3. Click to open the AI panel and test features

## 🎯 **Features**

### 🏠 **Canvas Page Integration**
- **Floating AI Button**: Always accessible on Canvas pages
- **Quick Actions**: Analyze content, generate questions
- **Context Awareness**: Automatically detects Canvas content

### 📝 **Content Analysis**
- **Page Analysis**: Summarizes current Canvas content
- **Key Concepts**: Extracts important learning points
- **Difficulty Assessment**: Evaluates content complexity

### ❓ **AI Q&A**
- **Contextual Questions**: Ask about current page content
- **Smart Answers**: AI-powered responses using OpenAI
- **Study Questions**: Auto-generate practice questions

### ⚙️ **Settings & Configuration**
- **Toggle Features**: Enable/disable functionality
- **API Health Check**: Monitor backend connection
- **Usage Statistics**: Track analyzed pages and questions

## 🔗 **API Integration**

The extension connects to your Railway-deployed backend:
- **API Endpoint**: `https://cucov2-production.up.railway.app`
- **Health Check**: `/health`
- **Content Analysis**: `/analyze-content`
- **Q&A System**: `/ask-question`

## 🛠️ **Development Setup**

### Extension Development
1. Make changes to files in `chrome_extension/`
2. Go to `chrome://extensions/`
3. Click "Reload" on Canvas AI Assistant extension
4. Test changes on Canvas pages

### Backend Development
- Backend code is in `src/` folder
- API server deployed on Railway
- Make changes and push to trigger redeployment

## 📚 **Usage Guide**

### For Students:
1. **Study Help**: Click 🤖 button while reading Canvas content
2. **Quick Analysis**: Use "Analyze Current Page" for summaries
3. **Ask Questions**: Type questions about the material
4. **Practice**: Generate study questions from content

### For Educators:
1. **Content Review**: Analyze course materials for clarity
2. **Question Generation**: Create assessments from content
3. **Difficulty Check**: Evaluate content complexity
4. **Student Support**: Understand AI assistance available

## 🔧 **Troubleshooting**

### Extension Not Working
1. Check if developer mode is enabled
2. Reload extension in `chrome://extensions/`
3. Verify you're on a Canvas page (`*.instructure.com`)

### API Connection Issues
1. Click extension icon → "Check API Status"
2. Verify Railway deployment is active
3. Check browser console for error messages

### Features Not Appearing
1. Ensure "Enable AI Assistant" is checked
2. Refresh the Canvas page
3. Check if content scripts are blocked

## 🌟 **Next Steps**

### Icon Creation
Create actual icons to replace placeholders:
- `icons/icon16.png` (16x16px)
- `icons/icon48.png` (48x48px) 
- `icons/icon128.png` (128x128px)

### Advanced Features
- Quiz generation from content
- Study schedule integration
- Performance analytics
- Multi-language support

### Publishing
1. Test thoroughly on various Canvas pages
2. Create proper icons and screenshots
3. Submit to Chrome Web Store
4. Set up user feedback system

## 🎉 **Success!**

Your Canvas AI Assistant is now ready for testing! The extension will:
- ✅ Integrate seamlessly with Canvas pages
- ✅ Connect to your Railway-deployed API
- ✅ Provide AI-powered educational assistance
- ✅ Enhance the learning experience

Navigate to any Canvas page and click the 🤖 button to get started!
