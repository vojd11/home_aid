import { createContext, useContext, useState, useEffect, ReactNode, useCallback, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import { User, LoginForm, RegisterForm } from '../types'
import { safariStorage } from '../utils/safariStorage'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (credentials: LoginForm) => Promise<void>
  register: (userData: RegisterForm) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Export the context for use in a separate hook file
export { AuthContext }

// Provider component - must be a named function for Fast Refresh
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [hasToken, setHasToken] = useState(false)
  const queryClient = useQueryClient()

  // Stable function for fetching current user
  const fetchCurrentUser = useCallback(async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
      return response.data
    } catch (error) {
      console.warn('Failed to fetch current user:', error)
      safariStorage.removeItem('access_token')
      safariStorage.removeItem('refresh_token')
      setUser(null)
      setHasToken(false)
      throw error
    }
  }, [])

  // Check for existing token on mount with Safari-specific handling
  useEffect(() => {
    let timeoutId: number

    const initializeAuth = async () => {
      try {
        // Add small delay for Safari to ensure localStorage is ready
        await new Promise(resolve => setTimeout(resolve, 50))

        const accessToken = safariStorage.getItem('access_token')
        const refreshToken = safariStorage.getItem('refresh_token')
        const hasAnyToken = !!accessToken || !!refreshToken

        console.log('Auth initialization - tokens found:', { access: !!accessToken, refresh: !!refreshToken })

        setHasToken(hasAnyToken)
        setIsInitialized(true)

        // If no tokens, clear user state immediately
        if (!hasAnyToken) {
          setUser(null)
        }
      } catch (error) {
        console.warn('Auth initialization error:', error)
        setHasToken(false)
        setUser(null)
        setIsInitialized(true)
      }
    }

    // Use timeout to ensure Safari localStorage is ready
    timeoutId = window.setTimeout(initializeAuth, 10)

    return () => clearTimeout(timeoutId)
  }, [])

  const { isLoading: queryIsLoading, error: queryError } = useQuery({
    queryKey: ['currentUser'],
    queryFn: fetchCurrentUser,
    enabled: hasToken && !user && isInitialized,
    retry: (failureCount: number, error: any) => {
      // Don't retry on 401 errors (invalid token)
      if (error?.response?.status === 401) {
        return false
      }
      // Retry up to 2 times for other errors
      return failureCount < 2
    },
    retryDelay: 1000, // 1 second delay between retries
    staleTime: 300000, // 5 minutes
    gcTime: 300000, // 5 minutes
  })

  // Handle query error
  useEffect(() => {
    if (queryError && hasToken) {
      console.warn('Current user query failed:', queryError)
      // If query fails and we have a token, clear it
      safariStorage.removeItem('access_token')
      safariStorage.removeItem('refresh_token')
      setHasToken(false)
      setUser(null)
    }
  }, [queryError, hasToken])

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginForm) => {
      const response = await api.post('/auth/login', credentials, {
        headers: { 'X-Login-Request': 'true' }
      })
      return response.data
    },
    onSuccess: (data: any) => {
      safariStorage.setItem('access_token', data.access_token)
      safariStorage.setItem('refresh_token', data.refresh_token)
      setUser(data.user)
      setHasToken(true)
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
    },
  })

  const registerMutation = useMutation({
    mutationFn: async (userData: RegisterForm) => {
      const response = await api.post('/auth/register', {
        email: userData.email,
        password: userData.password,
      }, {
        headers: { 'X-Login-Request': 'true' }
      })
      return response.data
    },
    onSuccess: (data: any) => {
      safariStorage.setItem('access_token', data.access_token)
      safariStorage.setItem('refresh_token', data.refresh_token)
      // Login endpoint returns tokens, but not user object usually. 
      // User will be fetched by invalidateQueries below.
      setHasToken(true)
      queryClient.invalidateQueries({ queryKey: ['currentUser'] })
    },
  })

  const login = useCallback(async (credentials: LoginForm) => {
    await loginMutation.mutateAsync(credentials)
  }, [loginMutation])

  const register = useCallback(async (userData: RegisterForm) => {
    await registerMutation.mutateAsync(userData)
  }, [registerMutation])

  const logout = useCallback(() => {
    safariStorage.removeItem('access_token')
    safariStorage.removeItem('refresh_token')
    setUser(null)
    setHasToken(false)
    queryClient.clear()
  }, [queryClient])

  // Calculate loading state more carefully with timeout protection
  const isLoading = !isInitialized ||
    (hasToken && !user && queryIsLoading && !queryError)

  // Debug logging in development
  useEffect(() => {
    // Simple development check that works in Vite
    const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    if (isDev) {
      console.log('Auth State Debug:', {
        isInitialized,
        hasToken,
        user: !!user,
        queryIsLoading,
        queryError: !!queryError,
        isLoading,
        loginPending: loginMutation.isPending,
        registerPending: registerMutation.isPending
      })
    }
  }, [isInitialized, hasToken, user, queryIsLoading, queryError, isLoading, loginMutation.isPending, registerMutation.isPending])

  // Memorize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    user,
    isLoading,
    login,
    register,
    logout,
  }), [user, isLoading, login, register, logout])

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}