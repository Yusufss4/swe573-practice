// SRS FR-1: Authentication Context
// Provides global authentication state management

import React, { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react'
import type { User, Notification } from '@/types'
import * as authService from '@/services/auth'
import { useQueryClient } from '@tanstack/react-query'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: authService.RegisterRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

/**
 * SRS FR-1.5: Authentication provider with session management
 * Stores JWT in localStorage and manages user state
 * SRS FR-N: WebSocket connection for real-time notifications
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const queryClient = useQueryClient()

  // WebSocket connection management
  const connectWebSocket = () => {
    const token = authService.getToken()
    if (!token || !user) return

    // WebSocket URL - use ws:// for local dev, wss:// for production
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/v1/notifications/ws?token=${token}`
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket connected')
        wsRef.current = ws
      }
      
      ws.onmessage = (event) => {
        try {
          const notification: Notification = JSON.parse(event.data)
          console.log('Received notification:', notification)
          
          // Invalidate notifications query to refresh the list
          queryClient.invalidateQueries({ queryKey: ['notifications'] })
          
          // Show browser notification if permitted
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
              body: notification.message,
              icon: '/hive-icon.png',
            })
          }
        } catch (error) {
          console.error('Error parsing notification:', error)
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
      ws.onclose = () => {
        console.log('WebSocket disconnected')
        wsRef.current = null
        
        // Attempt to reconnect after 5 seconds
        if (user) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...')
            connectWebSocket()
          }, 5000)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }

  const disconnectWebSocket = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedUser = authService.getCurrentUser()
      
      if (storedUser && authService.isAuthenticated()) {
        // Verify token is still valid by fetching fresh user data
        try {
          const freshUser = await authService.getProfile()
          setUser(freshUser)
        } catch (error) {
          // Token invalid, clear auth state
          authService.logout()
          setUser(null)
        }
      }
      
      setIsLoading(false)
    }

    initAuth()
  }, [])

  // Connect/disconnect WebSocket based on auth state
  useEffect(() => {
    if (user && !isLoading) {
      connectWebSocket()
    } else {
      disconnectWebSocket()
    }

    return () => {
      disconnectWebSocket()
    }
  }, [user, isLoading])

  const login = async (username: string, password: string) => {
    const response = await authService.login({ username, password })
    if (response.user) {
      setUser(response.user)
    }
  }

  const register = async (data: authService.RegisterRequest) => {
    const user = await authService.register(data)
    // After registration, automatically log in
    await login(data.username, data.password)
  }

  const logout = () => {
    authService.logout()
    setUser(null)
  }

  const refreshUser = async () => {
    const freshUser = await authService.getProfile()
    setUser(freshUser)
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Custom hook to access authentication context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
