# ChromaDB Clear Tools 🧹

This folder contains standalone tools to clear ChromaDB data for focused testing. These tools are completely independent and won't mess with your main code.

## Quick Start

### Option 1: Python Script (Cross-platform)
```bash
# Clear local ChromaDB only (default)
python clear_chroma_tool.py

# Clear Railway ChromaDB only  
python clear_chroma_tool.py --railway

# Clear both local and Railway
python clear_chroma_tool.py --both

# Skip confirmation prompt
python clear_chroma_tool.py --both --confirm
```

### Option 2: Windows Batch File
```cmd
# Double-click clear_chroma.bat or run from command prompt
clear_chroma.bat

# With arguments
clear_chroma.bat --railway
clear_chroma.bat --both --confirm
```

### Option 3: PowerShell Script (Recommended for Windows)
```powershell
# Run from PowerShell
.\clear_chroma.ps1

# With options
.\clear_chroma.ps1 -Railway
.\clear_chroma.ps1 -Both
.\clear_chroma.ps1 -Both -Confirm

# Show help
.\clear_chroma.ps1 -Help
```

## What Each Tool Does

### `clear_chroma_tool.py` - Main Python Script
- ✅ Detects and clears local ChromaDB automatically
- ✅ Can clear Railway ChromaDB via API
- ✅ Shows document counts before clearing
- ✅ Safe error handling
- ✅ Confirmation prompts
- ✅ Cross-platform compatible

### `clear_chroma.bat` - Windows Batch Script
- ✅ Simple double-click execution
- ✅ Calls the Python script
- ✅ Works in Command Prompt
- ✅ Pauses to show results

### `clear_chroma.ps1` - PowerShell Script
- ✅ Native PowerShell interface
- ✅ Colored output
- ✅ Built-in help system
- ✅ Parameter validation
- ✅ Better Windows integration

## Clearing Options

### Local ChromaDB (`--local`)
- Clears ChromaDB stored on your local machine
- Checks multiple possible paths:
  - `./chroma_db_v3_fresh` (default)
  - `./chroma_db`
  - `/tmp/chroma_db_railway`
  - Environment variable `CHROMA_DB_PATH`

### Railway ChromaDB (`--railway`)
- Clears ChromaDB on Railway deployment
- Uses the `/clear-knowledge-base` API endpoint
- Requires Railway API to be running
- URL: `https://cucov2-production.up.railway.app`

### Both (`--both`)
- Clears both local and Railway ChromaDB
- Useful for complete fresh start

## Usage Scenarios

### 🧪 **Focused Testing**
When you want to test with specific content only:
```bash
# Clear everything and start fresh
python clear_chroma_tool.py --both --confirm

# Upload specific test content via Chrome extension
# Test AI responses with only that content
```

### 🔄 **Development Workflow**
During development when you need clean data:
```bash
# Quick local clear during development
python clear_chroma_tool.py

# Or use PowerShell for better experience
.\clear_chroma.ps1
```

### 🚀 **Deployment Testing**
When testing the full pipeline:
```bash
# Clear Railway to test fresh deployment
python clear_chroma_tool.py --railway

# Test content upload and retrieval
```

### 🧹 **Complete Reset**
When you want to start completely fresh:
```bash
# Clear everything, no questions asked
python clear_chroma_tool.py --both --confirm
```

## Safety Features

### ✅ **Confirmation Prompts**
- By default, asks for confirmation before clearing
- Use `--confirm` to skip prompts for automation

### ✅ **Document Counting**
- Shows how many documents will be removed
- Displays collection names and sizes

### ✅ **Error Handling**
- Handles missing ChromaDB gracefully
- Shows clear error messages
- Continues on partial failures

### ✅ **Multiple Path Detection**
- Automatically finds ChromaDB wherever it's stored
- Checks environment variables
- Handles different installation patterns

## Requirements

### For Python Script:
```bash
pip install chromadb requests
```

### For PowerShell Script:
- Windows PowerShell or PowerShell Core
- Python with chromadb and requests

### For Batch Script:
- Windows Command Prompt
- Python in PATH

## Output Examples

### Successful Local Clear:
```
🧹 Clearing Local ChromaDB...
🔍 Found ChromaDB at: ./chroma_db_v3_fresh
   📊 Collection 'canvas_content': 13 documents
   ✅ Deleted collection 'canvas_content'
✅ Local ChromaDB cleared: 13 documents removed
```

### Successful Railway Clear:
```
🧹 Clearing Railway ChromaDB...
✅ Railway ChromaDB cleared: Successfully cleared 13 documents from canvas_content collection
```

### No Data Found:
```
🧹 Clearing Local ChromaDB...
ℹ️  No local ChromaDB found or all were already empty
```

## Troubleshooting

### Python Not Found
```bash
# Install Python or add to PATH
# Windows: Add Python to system PATH
# macOS/Linux: Use package manager
```

### ChromaDB Import Error
```bash
pip install chromadb
```

### Railway API Not Responding
- Check if Railway deployment is running
- Verify API URL in script
- Check network connection

### Permission Errors
- Run as administrator if needed
- Check file permissions on ChromaDB directory

## Integration with Development Workflow

### Before Testing New Features:
```bash
.\clear_chroma.ps1 -Both -Confirm
```

### Before Content Quality Tests:
```bash
python clear_chroma_tool.py --local
# Then upload specific test content
```

### Before Deployment Verification:
```bash
python clear_chroma_tool.py --railway
# Then test the full pipeline
```

## File Structure
```
cucoV2/
├── clear_chroma_tool.py     # Main Python script
├── clear_chroma.bat         # Windows batch file
├── clear_chroma.ps1         # PowerShell script
└── CLEAR_CHROMA_README.md   # This documentation
```

## Notes

- These tools are completely standalone
- They don't modify your main application code
- Safe to run anytime during development
- Can be run while the main application is running
- Useful for A/B testing with different content sets

---

**Need help?** Run `.\clear_chroma.ps1 -Help` for PowerShell help or check this README.
