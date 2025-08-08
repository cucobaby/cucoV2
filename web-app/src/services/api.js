import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

// API Service Functions
export const apiService = {
  // Query endpoints
  async query(question) {
    const response = await api.post('/query', { question })
    return response.data
  },

  async queryParsed(question) {
    const response = await api.post('/query-parsed', { question })
    return response.data
  },

  // Content management
  async ingestContent(contentData) {
    const response = await api.post('/ingest-content', contentData)
    return response.data
  },

  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
    return response.data
  },

  // Knowledge base operations
  async getContentList() {
    const response = await api.get('/content/list')
    return response.data
  },

  async searchContent(query, filters = {}) {
    const response = await api.post('/api/content/search', { query, filters })
    return response.data
  },

  // Analytics and stats
  async getStats() {
    const response = await api.get('/api/stats')
    return response.data
  },

  async getAnalytics(timeRange = '7d') {
    const response = await api.get(`/api/analytics?range=${timeRange}`)
    return response.data
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  }
}

export default api
