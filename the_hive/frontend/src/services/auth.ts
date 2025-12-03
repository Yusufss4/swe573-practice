// SRS FR-1: Authentication service
// Handles user registration, login, and session management

import apiClient from './api'
import type { User } from '@/types'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  display_name?: string
  location_lat?: number
  location_lon?: number
  location_name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface LoginResponse extends AuthResponse {
  user?: User
}

/**
 * SRS FR-1.3: Login functionality
 * Returns JWT token and fetches user data
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  // Backend expects JSON with username and password
  const response = await apiClient.post<AuthResponse>('/auth/login', credentials)

  // SRS FR-1.5: Store token for session management
  if (response.data.access_token) {
    localStorage.setItem('access_token', response.data.access_token)
    
    // Fetch user profile after successful login
    try {
      const user = await getProfile()
      return {
        ...response.data,
        user,
      }
    } catch (error) {
      // If profile fetch fails, still return token but no user
      return response.data
    }
  }

  return response.data
}

/**
 * SRS FR-1.1: User registration
 * SRS FR-1.2: Email and password validation (backend)
 */
export const register = async (data: RegisterRequest): Promise<User> => {
  // Register returns the user object directly
  const response = await apiClient.post<User>('/auth/register', data)

  // After registration, user needs to login separately
  // We don't get a token from registration
  return response.data
}

/**
 * SRS FR-1.3: Logout functionality
 */
export const logout = (): void => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
}

/**
 * Get current user from localStorage
 */
export const getCurrentUser = (): User | null => {
  const userJson = localStorage.getItem('user')
  if (!userJson) return null

  try {
    return JSON.parse(userJson)
  } catch {
    return null
  }
}

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('access_token')
}

/**
 * Fetch current user profile from API
 * SRS FR-2: Profile management
 */
export const getProfile = async (): Promise<User> => {
  const response = await apiClient.get<User>('/auth/me')
  
  // Update localStorage with fresh user data
  localStorage.setItem('user', JSON.stringify(response.data))
  
  return response.data
}

/**
 * Update user profile
 * SRS FR-2.4: Edit personal details
 */
export const updateProfile = async (data: Partial<User>): Promise<User> => {
  const response = await apiClient.patch<User>('/auth/me', data)
  
  // Update localStorage
  localStorage.setItem('user', JSON.stringify(response.data))
  
  return response.data
}
