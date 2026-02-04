import React from 'react'
import '../styles/SuggestionCard.css'

function SuggestionCard({ suggestion }) {
  const getSeverityClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'severity-high'
      case 'medium':
        return 'severity-medium'
      case 'low':
        return 'severity-low'
      default:
        return 'severity-medium'
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp * 1000)
    return date.toLocaleTimeString()
  }

  return (
    <div className={`suggestion-card ${getSeverityClass(suggestion.severity)}`}>
      <div className="suggestion-header">
        <span className="suggestion-type">{suggestion.type?.replace(/_/g, ' ')}</span>
        <span className="suggestion-time">{formatTimestamp(suggestion.timestamp)}</span>
      </div>
      <div className="suggestion-message">{suggestion.message}</div>
      <div className="suggestion-severity-badge">{suggestion.severity}</div>
    </div>
  )
}

export default SuggestionCard
