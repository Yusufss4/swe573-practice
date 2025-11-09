// SRS FR-1: Authentication Context
// Provides global authentication state management

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { User } from '@/types'
import * as authService from '@/services/auth'

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
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

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
