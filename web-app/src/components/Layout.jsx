import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Home, 
  Search, 
  BookOpen, 
  BarChart3, 
  Settings, 
  Menu,
  X,
  Bot,
  ExternalLink
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Advanced Search', href: '/search', icon: Search },
  { name: 'Content Manager', href: '/content', icon: BookOpen },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0
      `}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Bot className="h-8 w-8 text-primary-500" />
            <span className="text-xl font-bold text-gray-900">Cuco AI</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="mt-8 px-4">
          <div className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    sidebar-link
                    ${isActive ? 'active' : 'text-gray-600 hover:text-gray-900'}
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </div>

          {/* Chrome Extension Link */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Quick Access
            </div>
            <a
              href="https://canvas.instructure.com"
              target="_blank"
              rel="noopener noreferrer"
              className="sidebar-link text-gray-600 hover:text-gray-900"
            >
              <ExternalLink className="h-5 w-5" />
              Open Canvas
            </a>
          </div>
        </nav>

        {/* Version info */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="text-xs text-gray-400 text-center">
            Cuco AI v1.0.0
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="md:hidden p-2 rounded-lg hover:bg-gray-100"
                >
                  <Menu className="h-5 w-5" />
                </button>
                <div className="md:ml-0 ml-4">
                  <h1 className="text-lg font-semibold text-gray-900">
                    {navigation.find(item => item.href === location.pathname)?.name || 'Cuco AI Assistant'}
                  </h1>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="text-sm text-gray-500">
                  Connected to Canvas
                </div>
                <div className="h-2 w-2 bg-green-400 rounded-full"></div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
