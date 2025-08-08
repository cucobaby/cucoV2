import { useState } from 'react'
import { Search as SearchIcon, Filter, SortAsc, BookOpen, Calendar, Tag } from 'lucide-react'

export default function Search() {
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState({
    contentType: 'all',
    dateRange: 'all',
    difficulty: 'all'
  })
  const [results, setResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setIsLoading(true)
    // TODO: Connect to API
    setTimeout(() => {
      setResults([
        {
          id: 1,
          title: "Protein Structure Fundamentals",
          excerpt: "Proteins are complex molecules that play critical roles in the body. They are made up of amino acids...",
          type: "study_guide",
          date: "2024-08-07",
          relevance: 95
        },
        {
          id: 2,
          title: "DNA Replication Process",
          excerpt: "DNA replication is the process by which DNA makes a copy of itself during cell division...",
          type: "assignment",
          date: "2024-08-06",
          relevance: 88
        }
      ])
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Advanced Search</h2>
        
        {/* Search Input */}
        <div className="relative mb-6">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Ask a question or search your content..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
          />
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Content Type</label>
            <select 
              value={filters.contentType}
              onChange={(e) => setFilters({...filters, contentType: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Types</option>
              <option value="study_guide">Study Guides</option>
              <option value="assignment">Assignments</option>
              <option value="quiz">Quizzes</option>
              <option value="discussion">Discussions</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select 
              value={filters.dateRange}
              onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <select 
              value={filters.difficulty}
              onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <div className="flex items-end">
            <button 
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Quick Search Suggestions */}
        <div className="border-t pt-4">
          <p className="text-sm text-gray-600 mb-3">Quick searches:</p>
          <div className="flex flex-wrap gap-2">
            {['protein structure', 'DNA replication', 'photosynthesis', 'cell division', 'enzyme function'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => {setQuery(suggestion); handleSearch()}}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search Results */}
      {results.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Search Results ({results.length})
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <SortAsc className="h-4 w-4" />
              Sorted by relevance
            </div>
          </div>

          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all cursor-pointer">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-lg font-medium text-gray-900 hover:text-primary-600">
                    {result.title}
                  </h4>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-full text-xs">
                      {result.type.replace('_', ' ')}
                    </span>
                    <span>{result.relevance}% match</span>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-3 line-clamp-2">
                  {result.excerpt}
                </p>
                
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {new Date(result.date).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <BookOpen className="h-4 w-4" />
                    Study Material
                  </div>
                  <div className="flex items-center gap-1">
                    <Tag className="h-4 w-4" />
                    Biology
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {results.length === 0 && query && !isLoading && (
        <div className="card text-center py-12">
          <SearchIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-500 mb-4">
            Try adjusting your search terms or filters
          </p>
          <button className="btn-secondary">
            Browse All Content
          </button>
        </div>
      )}

      {/* Initial State */}
      {results.length === 0 && !query && (
        <div className="card text-center py-12">
          <SearchIcon className="h-12 w-12 text-primary-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Search Your Knowledge Base</h3>
          <p className="text-gray-500 mb-4">
            Use advanced search to find specific information from your uploaded content
          </p>
          <div className="flex justify-center gap-4">
            <button 
              onClick={() => setQuery('protein structure')}
              className="btn-secondary"
            >
              Try Sample Search
            </button>
            <button className="btn-primary">
              Upload New Content
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
