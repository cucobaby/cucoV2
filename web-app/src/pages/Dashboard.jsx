import { useState, useEffect } from 'react'
import { 
  BookOpen, 
  MessageSquare, 
  TrendingUp, 
  Clock,
  Target,
  Brain,
  Plus,
  Search,
  ArrowRight
} from 'lucide-react'
import { apiService } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_content: 0,
    questions_asked: 0,
    study_streak: 0,
    last_active: 'Loading...'
  })

  const [loading, setLoading] = useState(true)

  const [recentQuestions, setRecentQuestions] = useState([
    { id: 1, question: "What is protein structure?", timestamp: "10 min ago", topic: "Biochemistry" },
    { id: 2, question: "Explain DNA replication", timestamp: "1 hour ago", topic: "Molecular Biology" },
    { id: 3, question: "How does photosynthesis work?", timestamp: "2 hours ago", topic: "Cell Biology" },
  ])

  const [studyTopics, setStudyTopics] = useState([
    { name: "Protein Structure", progress: 85, color: "bg-blue-500" },
    { name: "DNA Replication", progress: 70, color: "bg-green-500" },
    { name: "Cell Biology", progress: 60, color: "bg-purple-500" },
    { name: "Photosynthesis", progress: 45, color: "bg-orange-500" },
  ])

  // Fetch stats from API
  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log('Fetching stats from API...')
        const data = await apiService.getStats()
        console.log('Stats received:', data)
        setStats(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl p-8 text-white">
        <h2 className="text-3xl font-bold mb-2">Welcome back to Cuco AI! 🤖</h2>
        <p className="text-primary-100 text-lg mb-6">
          Ready to continue your learning journey? You're doing great!
        </p>
        <div className="flex gap-4">
          <button className="bg-white text-primary-600 px-6 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors">
            Ask a Question
          </button>
          <button className="border border-white text-white px-6 py-2 rounded-lg font-medium hover:bg-white hover:bg-opacity-10 transition-colors">
            Upload Content
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Content Items</p>
              <p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats.total_content}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <MessageSquare className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Questions Asked</p>
              <p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats.questions_asked}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Study Streak</p>
              <p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats.study_streak} days</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Clock className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Last Active</p>
              <p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats.last_active}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Questions */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Recent Questions
            </h3>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All
            </button>
          </div>
          
          <div className="space-y-4">
            {recentQuestions.map((question) => (
              <div key={question.id} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                <p className="font-medium text-gray-900 mb-2">{question.question}</p>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs">
                    {question.topic}
                  </span>
                  <span>{question.timestamp}</span>
                </div>
              </div>
            ))}
          </div>

          <button className="w-full mt-4 p-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary-300 hover:text-primary-600 transition-colors flex items-center justify-center gap-2">
            <Plus className="h-5 w-5" />
            Ask New Question
          </button>
        </div>

        {/* Study Progress */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Study Progress
            </h3>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View Analytics
            </button>
          </div>
          
          <div className="space-y-4">
            {studyTopics.map((topic, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-900">{topic.name}</span>
                  <span className="text-gray-500">{topic.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${topic.color} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${topic.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-primary-50 rounded-lg">
            <p className="text-sm text-primary-700 mb-2">
              <strong>Study Tip:</strong> You're making great progress on Protein Structure! 
              Consider reviewing DNA Replication next to strengthen your foundation.
            </p>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center gap-1">
              Generate Study Plan
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
            <Search className="h-6 w-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-gray-900">Advanced Search</h4>
            <p className="text-sm text-gray-500 mt-1">Search through your knowledge base with filters</p>
          </button>

          <button className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
            <BookOpen className="h-6 w-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-gray-900">Manage Content</h4>
            <p className="text-sm text-gray-500 mt-1">Organize and review your uploaded materials</p>
          </button>

          <button className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors text-left">
            <TrendingUp className="h-6 w-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-gray-900">View Analytics</h4>
            <p className="text-sm text-gray-500 mt-1">Track your learning progress and insights</p>
          </button>
        </div>
      </div>
    </div>
  )
}
