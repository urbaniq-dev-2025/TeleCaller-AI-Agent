import React, { useState, useEffect } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import SuggestionCard from './components/SuggestionCard'
import './styles/App.css'

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const { connectionStatus, connect, disconnect, lastMessage } = useWebSocket()

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data)
        
        if (data.type === 'suggestion') {
          // Add new suggestion
          setSuggestions(prev => [data.data, ...prev].slice(0, 10)) // Keep last 10
        } else if (data.type === 'call_ended') {
          // Clear suggestions when call ends
          setSuggestions([])
          setSessionId(null)
        } else if (data.type === 'stream_started') {
          // Set session ID when stream starts
          setSessionId(data.session_id)
        }
      } catch (e) {
        console.error('Error parsing message:', e)
      }
    }
  }, [lastMessage])

  // Auto-remove suggestions after 5 seconds
  useEffect(() => {
    if (suggestions.length > 0) {
      const timer = setTimeout(() => {
        setSuggestions(prev => prev.slice(0, -1))
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [suggestions])

  const handleConnect = () => {
    // For now, use a test session ID
    // In real usage, this would come from the backend when a call starts
    const testSessionId = 'test-session-' + Date.now()
    setSessionId(testSessionId)
    connect(`ws://localhost:8000/ws/ui/${testSessionId}`)
  }

  const handleDisconnect = () => {
    disconnect()
    setSessionId(null)
    setSuggestions([])
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Real-Time AI Call Coaching</h1>
        <div className="connection-status">
          <span className={`status-indicator ${connectionStatus}`}>
            {connectionStatus === 'connected' ? '●' : '○'}
          </span>
          <span className="status-text">
            {connectionStatus === 'connected' ? 'Connected' : 
             connectionStatus === 'connecting' ? 'Connecting...' : 
             connectionStatus === 'error' ? 'Error' : 'Disconnected'}
          </span>
          {connectionStatus === 'disconnected' && (
            <button onClick={handleConnect} className="connect-btn">
              Connect
            </button>
          )}
          {connectionStatus === 'connected' && (
            <button onClick={handleDisconnect} className="disconnect-btn">
              Disconnect
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        {sessionId && (
          <div className="session-info">
            <p>Session: {sessionId.substring(0, 8)}...</p>
          </div>
        )}

        <div className="suggestions-container">
          {suggestions.length === 0 ? (
            <div className="empty-state">
              <p>Waiting for coaching suggestions...</p>
              <p className="hint">Suggestions will appear here during an active call</p>
            </div>
          ) : (
            <div className="suggestions-list">
              {suggestions.map((suggestion, index) => (
                <SuggestionCard key={`${suggestion.timestamp}-${index}`} suggestion={suggestion} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
