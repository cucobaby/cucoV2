# Cuco AI Assistant - Web Application

## 🚀 Getting Started

This is the web application component of the Cuco AI Educational Assistant. It provides an advanced interface for managing your AI-powered learning experience.

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the web-app directory:
```bash
cd web-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open http://localhost:3000 in your browser

### Environment Variables

Create a `.env.local` file in the web-app directory:

```env
VITE_API_URL=https://cucov2-production.up.railway.app
```

## 🏗️ Architecture

```
web-app/
├── src/
│   ├── components/     # Reusable UI components
│   │   └── Layout.jsx  # Main app layout
│   ├── pages/          # Route components
│   │   ├── Dashboard.jsx
│   │   ├── Search.jsx
│   │   ├── ContentManager.jsx
│   │   ├── Analytics.jsx
│   │   └── Settings.jsx
│   ├── services/       # API integration
│   │   └── api.js      # Axios configuration
│   ├── hooks/          # Custom React hooks
│   │   └── useApi.js   # API data fetching
│   ├── utils/          # Helper functions
│   │   └── helpers.js  # Utility functions
│   └── index.css       # Global styles
├── package.json
├── vite.config.js      # Vite configuration
└── tailwind.config.js  # Tailwind CSS config
```

## 🎨 Features

### Current
- **📊 Dashboard** - Overview of study progress and recent activity
- **🔍 Advanced Search** - Rich search interface with filters
- **📱 Responsive Design** - Works on all device sizes
- **🎨 Modern UI** - Clean, professional interface

### Planned
- **📚 Content Management** - Organize uploaded materials
- **📈 Analytics** - Detailed progress tracking
- **⚙️ Settings** - Customizable preferences
- **🎯 Study Sessions** - Timed study with tracking
- **📝 Note Taking** - Rich text editor

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Tech Stack

- **Frontend**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Build Tool**: Vite

## 🌐 Deployment

The web app can be deployed to:
- **Vercel** (recommended for frontend)
- **Netlify**
- **Railway** (same as backend)

### Vercel Deployment

1. Connect your GitHub repo to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables

## 🔗 Integration

### Chrome Extension Integration

The web app is designed to work seamlessly with the Chrome extension:

1. **Extension** provides quick Canvas integration
2. **Web App** offers advanced features and better UX
3. Both share the same FastAPI backend
4. User can switch between interfaces smoothly

### API Endpoints

The web app connects to these backend endpoints:

- `POST /query` - Ask questions
- `POST /query-parsed` - Get structured responses
- `POST /ingest-content` - Upload content
- `GET /stats` - Get usage statistics
- `GET /health` - Health check

## 📝 Next Steps

1. **Install dependencies** and run locally
2. **Test API connection** to your Railway backend
3. **Customize styling** to match your preferences
4. **Add new features** as needed
5. **Deploy to production**

## 🤝 Contributing

This is the foundation for your advanced AI assistant web app. Build upon it by:

1. Adding new pages and components
2. Enhancing the UI/UX
3. Connecting more API endpoints
4. Adding advanced features

Happy coding! 🚀
