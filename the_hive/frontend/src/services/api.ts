// SRS: API client configuration
// Axios instance with authentication and error handling

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import config from '@/utils/config'
import type { ApiError } from '@/types'

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor - attach JWT token
// SRS FR-1.5: Session-based authentication
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Remove Content-Type for FormData - let browser set it with proper boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    // Preserve the full axios error for better error handling
    return Promise.reject(error)
  }
)

export default apiClient
