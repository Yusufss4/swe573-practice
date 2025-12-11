// SRS: Environment configuration utilities
// Provides type-safe access to environment variables

export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  map: {
    defaultLat: parseFloat(import.meta.env.VITE_MAP_DEFAULT_LAT || '41.0082'),
    defaultLng: parseFloat(import.meta.env.VITE_MAP_DEFAULT_LNG || '28.9784'),
    defaultZoom: parseInt(import.meta.env.VITE_MAP_DEFAULT_ZOOM || '12', 10),
  },
} as const

export default config
