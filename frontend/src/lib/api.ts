import axios from 'axios'

console.log('Environment VITE_API_URL:', import.meta.env.VITE_API_URL)
const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
console.log('Resolved API_BASE_URL:', API_BASE_URL)

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token and ensure trailing slashes
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  if (config.url && ['post', 'put', 'patch'].includes(config.method?.toLowerCase() || '')) {
  }

  return config
})

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    console.log('Interceptor Error:', error.response?.status, error.config?.url)
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Don't redirect on login failures
      // Don't redirect on login failures - check for custom header OR url
      const headers = error.config?.headers
      const hasHeader = headers && (
        (headers['X-Login-Request']) ||
        (typeof headers.get === 'function' && headers.get('X-Login-Request'))
      )

      const url = error.config?.url || ''
      const isAuthUrl = url.includes('login') || url.includes('auth')

      console.log('Interceptor Check:', { hasHeader, isAuthUrl, url })

      if (hasHeader || isAuthUrl) {
        console.log('Skipping refresh for auth/login request error')
        return Promise.reject(error)
      }
      console.log('Attempting refresh...')
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      console.log('Found refresh token:', !!refreshToken)
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          })

          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// DRLZ API functions
export const drlzApi = {
  searchMedications: async (query: string, limit: number = 20) => {
    const response = await api.get('/drlz/search-drlz', {
      params: { query, limit }
    })
    return response.data
  },

  getStatistics: async () => {
    const response = await api.get('/drlz/drlz-stats')
    return response.data
  }
}

// Auth API - alias for the main api instance with authentication
export const authApi = api

export default api
