import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export function formatDateTime(date) {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function truncateText(text, maxLength = 100) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function getContentTypeIcon(type) {
  const icons = {
    'study_guide': '📚',
    'assignment': '📝',
    'quiz': '❓',
    'discussion': '💬',
    'page': '📄',
    'file': '📎',
    'default': '📋'
  }
  return icons[type] || icons.default
}

export function getContentTypeColor(type) {
  const colors = {
    'study_guide': 'bg-blue-100 text-blue-700',
    'assignment': 'bg-green-100 text-green-700',
    'quiz': 'bg-orange-100 text-orange-700',
    'discussion': 'bg-purple-100 text-purple-700',
    'page': 'bg-gray-100 text-gray-700',
    'file': 'bg-yellow-100 text-yellow-700',
    'default': 'bg-gray-100 text-gray-700'
  }
  return colors[type] || colors.default
}
