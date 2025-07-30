# Canvas AI Assistant API

A FastAPI-powered backend for processing educational content and providing AI-powered assistance for Canvas LMS integration.

## 🚀 Features

- **Content Analysis**: AI-powered analysis of educational materials
- **Question Answering**: Semantic search and GPT-powered responses
- **Quiz Generation**: Automated quiz creation from content
- **Canvas Integration**: Browser extension backend support
- **Vector Database**: ChromaDB for semantic content storage

## 📦 Deployment on Railway

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Manual Deployment

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Connect GitHub**: Link your GitHub account to Railway

3. **Deploy Project**:
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Add FastAPI server for Railway deployment"
   git push origin main
   ```

4. **Create Railway Project**:
   - Go to Railway dashboard
   - Click "New Project" > "Deploy from GitHub repo"
   - Select your cucoV2 repository
   - Railway will auto-detect the Python app

5. **Set Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. **Deploy**: Railway will automatically build and deploy!

## 🔧 Local Development

### Setup

```bash
# Install dependencies
pip install -r requirments.txt

# Copy environment file
cp .env.example .env
# Edit .env with your OpenAI API key

# Run the server
python src/api_server.py
```

### API Endpoints

- `GET /` - Health check
- `POST /analyze-content` - Process educational content
- `POST /ask-question` - Ask questions about content
- `POST /generate-quiz` - Create quizzes
- `GET /stats` - System statistics

### Example Usage

```bash
# Test the API
curl -X POST "http://localhost:8000/analyze-content" \
  -H "Content-Type: application/json" \
  -d '{"content": "Photosynthesis is the process...", "title": "Biology Chapter 1"}'
```

## 🌐 Browser Extension Integration

Once deployed, your Railway URL becomes the backend for the Canvas browser extension:

```javascript
const API_BASE = 'https://your-app.railway.app';

// Analyze content
const response = await fetch(`${API_BASE}/analyze-content`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: canvasContent, title: pageTitle })
});
```

## 📁 Project Structure

```
cucoV2/
├── src/
│   ├── api_server.py          # FastAPI application
│   ├── content_pipeline.py    # Content processing pipeline
│   ├── core_assistant.py      # AI assistant core
│   └── ...                    # Other modules
├── railway.toml               # Railway configuration
├── requirments.txt           # Python dependencies
└── .env.example              # Environment template
```

## 🔒 Security Notes

- API keys are environment variables
- CORS configured for browser extensions
- Input validation on all endpoints
- Rate limiting recommended for production

## 📊 Monitoring

Railway provides built-in monitoring:
- View logs in Railway dashboard
- Monitor CPU/memory usage
- Set up alerts for downtime

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key**: Ensure it's set in Railway environment variables
2. **Memory Issues**: Railway provides 512MB free tier
3. **Cold Starts**: First request may be slower

### Support

- Check Railway logs for detailed error messages
- Verify environment variables are set correctly
- Test endpoints locally first
