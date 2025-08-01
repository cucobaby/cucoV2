# Chrome Extension Testing Guide

## Quick Setup and Testing

### 1. Load Extension in Chrome
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` folder from this project
5. The extension should now appear in your extensions list

### 2. Test on Canvas
1. Navigate to any Canvas course page
2. Look for the 🤖 buttons next to Canvas links
3. Click a 🤖 button to test content ingestion
4. Check the browser console (F12 → Console) for debug messages

### 3. Expected Behavior
When you click a 🤖 button:
- A notification should appear: "Processing: [Link Name]"
- Content should be sent to the knowledge base
- Success notification: "✅ Added '[Link Name]' to knowledge base"
- No popup menus should appear (this was the old behavior)

### 4. Debug Console Messages
Look for these messages in the browser console:
- `📍 Canvas navigation detected`
- `🤖 Adding AI button to: [Link Name]`
- `📥 Ingesting content: [Link Name]`
- `📚 Ingested content: [Link Name]`

### 5. Testing Different Link Types
The extension should detect and add buttons to:
- ✅ Assignments (`/assignments/`)
- ✅ Discussions (`/discussion_topics/`)
- ✅ Pages (`/pages/`)
- ✅ Quizzes (`/quizzes/`)
- ✅ Files (`/files/`)
- ✅ Module items (`/modules/`)
- ✅ Announcements (`/announcements/`)

### 6. API Integration
- Make sure the Railway API is running and accessible
- The extension will send requests to your Railway URL
- Check Network tab in browser dev tools for API calls

### 7. Troubleshooting
If buttons don't appear:
1. Check if you're on a Canvas page (*.instructure.com)
2. Try refreshing the page
3. Check browser console for errors
4. Verify the extension is enabled

If ingestion fails:
1. Check if the Railway API is accessible
2. Look for CORS errors in console
3. Verify the API endpoint is responding
4. Check API logs on Railway dashboard

### 8. Content Verification
After ingesting content, you can verify it worked by:
1. Using the AI assistant's question interface
2. Asking questions about the ingested content
3. Checking if the AI has knowledge of the Canvas material

## Key Changes in This Version
- **No more popup menus** - direct content ingestion
- **Silent operation** - buttons work in background
- **Knowledge base building** - content gets added for later querying
- **Canvas-wide coverage** - buttons on all relevant link types
