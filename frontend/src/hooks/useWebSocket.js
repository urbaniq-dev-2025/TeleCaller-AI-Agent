import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url = null) {
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [lastMessage, setLastMessage] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const connect = useCallback((wsUrl) => {
    if (!wsUrl) return

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close()
    }

    setConnectionStatus('connecting')

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setConnectionStatus('connected')
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        setLastMessage(event)
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('error')
      }

      ws.onclose = () => {
        setConnectionStatus('disconnected')
        console.log('WebSocket disconnected')
        
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          if (wsUrl) {
            connect(wsUrl)
          }
        }, 3000)
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      setConnectionStatus('error')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setConnectionStatus('disconnected')
    setLastMessage(null)
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    connectionStatus,
    lastMessage,
    connect,
    disconnect
  }
}
