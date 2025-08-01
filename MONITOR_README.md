# 📊 Canvas AI Assistant - Pipeline Monitor Dashboard

A real-time web-based monitoring dashboard that you can open in any browser tab to track your Canvas AI Assistant data pipeline.

## 🚀 Quick Start

### Option 1: PowerShell Launcher (Recommended for Windows)
```powershell
.\launch_monitor.ps1
```

### Option 2: Python Launcher
```bash
python launch_monitor.py
```

### Option 3: Direct Browser Open
Simply double-click `monitor_dashboard.html` or open it in your browser

## 📊 Dashboard Features

### 🏥 **System Health Monitor**
- **API Response Time**: Real-time API latency monitoring
- **ChromaDB Status**: Database connection and health
- **OpenAI Status**: AI service connectivity
- **Extension Status**: Chrome extension connection status

### 📈 **Data Statistics**
- **Total Documents**: Number of documents in knowledge base
- **Collections**: ChromaDB collections count
- **Latest Upload**: Timestamp of most recent content
- **Storage Used**: Estimated storage consumption

### 🔄 **Recent Activity Log**
- Real-time activity monitoring
- API calls and responses
- Error tracking
- System events

### 🔍 **Live Search Testing**
- Test search functionality directly from dashboard
- See AI responses in real-time
- View source documents used
- Monitor search performance

### 📚 **Document Library**
- List all documents in knowledge base
- View document metadata
- See content previews
- Track upload sources and timestamps

### 🎛️ **Control Panel**
- **Refresh Data**: Manual data refresh
- **Clear Knowledge Base**: Empty all stored content
- **Export Data**: Download system statistics
- **Auto Refresh**: Toggle automatic updates (30s interval)

## 🔧 How to Use for Data Processing Monitoring

### 📥 **Before Adding Data:**
1. Open the monitor dashboard
2. Note current document count
3. Enable auto-refresh for real-time updates

### ⏱️ **During Data Upload:**
1. Watch the "Recent Activity" log for upload events
2. Monitor "Total Documents" counter for increases
3. Check "Latest Upload" timestamp for updates

### ✅ **Verify Full Processing:**
1. **Document Count Increased**: Confirms data was stored
2. **Latest Upload Updated**: Shows processing timestamp
3. **Test Search Works**: Validates data is searchable
4. **No Error Messages**: Indicates successful processing

### 🧪 **Testing Your Data:**
1. Use the "Test Search" section
2. Enter questions related to your uploaded content
3. Verify responses use your new data
4. Check that sources reference your documents

## 📋 Processing Completion Indicators

### ✅ **Data Fully Processed When:**
- [ ] Document count increased by expected amount
- [ ] Latest upload timestamp is recent (within last few minutes)
- [ ] Test search returns relevant answers using your content
- [ ] No error messages in activity log
- [ ] Document library shows your new content with proper metadata

### ⚠️ **Potential Issues to Watch For:**
- Document count doesn't increase (upload failed)
- Latest upload timestamp doesn't update (processing stuck)
- Test search doesn't find your content (indexing issues)
- Error messages in activity log (system problems)

## 🎯 Typical Data Processing Workflow

### 1. **Pre-Upload Check**
```
Open Dashboard → Note Current Stats → Enable Auto-Refresh
```

### 2. **Upload Content via Chrome Extension**
```
Use 🤖 buttons on Canvas → Watch Activity Log → Monitor Document Count
```

### 3. **Verify Processing Complete**
```
Document Count +1 → Latest Upload Updated → Test Search Works
```

### 4. **Quality Check**
```
Test with specific questions → Verify answers use new content → Check sources
```

## 🔄 Auto-Refresh Feature

- **Enable**: Click "Auto Refresh: OFF" to turn on
- **Interval**: Updates every 30 seconds
- **Benefits**: Real-time monitoring without manual refresh
- **Usage**: Great for watching data processing in real-time

## 🛠️ Technical Details

### **API Integration**
The dashboard connects to your Railway API at:
```
https://cucov2-production.up.railway.app
```

### **Endpoints Used**
- `/health` - API status checking
- `/list-documents` - Document inventory
- `/ask` - Search testing
- `/clear-knowledge-base` - Data clearing

### **Browser Compatibility**
- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- 🔧 Works offline for local monitoring

## 🚨 Troubleshooting

### **Dashboard Won't Load**
1. Check that `monitor_dashboard.html` exists
2. Try launching with `launch_monitor.ps1`
3. Open file directly in browser

### **API Status Shows Offline**
1. Check Railway deployment status
2. Verify API URL in dashboard code
3. Check network connection

### **No Documents Showing**
1. Verify documents exist with clear tool
2. Check API `/list-documents` endpoint
3. Refresh the dashboard

### **Search Test Fails**
1. Ensure documents are uploaded
2. Check API `/ask` endpoint
3. Verify OpenAI integration

## 📱 Mobile Friendly

The dashboard is responsive and works on:
- 📱 Mobile phones
- 📱 Tablets  
- 💻 Desktop computers
- 🖥️ Large monitors

## 🎨 Visual Indicators

### **Status Colors**
- 🟢 **Green**: System healthy/online
- 🔴 **Red**: System error/offline  
- 🟡 **Yellow**: Loading/processing
- 🔵 **Blue**: Information/metrics

### **Activity Log Colors**
- **White**: Normal activity
- **Red**: Error messages
- **Green**: Success operations
- **Gray**: Timestamps

## 💾 Data Export

Export system statistics including:
- Current document counts
- API status information
- Latest upload timestamps
- System health metrics

Files saved as: `pipeline-data-YYYY-MM-DD.json`

## 🔒 Security Notes

- Dashboard runs locally in your browser
- No sensitive data stored in dashboard
- API calls use HTTPS to Railway
- No authentication required for monitoring

## 📝 Tips for Effective Monitoring

### **For Development:**
- Keep dashboard open while coding
- Enable auto-refresh during testing
- Use clear tool before focused tests

### **For Data Quality:**
- Test search after each upload
- Monitor document metadata
- Watch for error patterns

### **For Performance:**
- Track API response times
- Monitor document processing speed
- Watch for memory/storage trends

---

**🎉 Ready to monitor your pipeline!** 

Open the dashboard and start tracking your Canvas AI Assistant data processing in real-time!
