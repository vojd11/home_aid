import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { LoginForm, LoginSchema, RegisterForm, RegisterSchema } from '../types'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { user, login, register } = useAuth()

  const {
    register: registerField,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<LoginForm | RegisterForm>({
    resolver: zodResolver(isLogin ? LoginSchema : RegisterSchema),
  })

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/" replace />
  }

  const onSubmit = async (data: LoginForm | RegisterForm) => {
    try {
      setError(null)
      if (isLogin) {
        await login(data as LoginForm)
      } else {
        await register(data as RegisterForm)
      }
    } catch (error: any) {
      console.error('Authentication error:', error)
      setError(error?.response?.data?.detail || 'Authentication failed. Please try again.')
    }
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    setError(null)
    reset()
  }

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-200 opacity-20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-purple-200 opacity-20 blur-3xl"></div>
      </div>

      {/* Main container with proper centering */}
      <div className="relative z-10 w-full max-w-lg">
        {/* Material Design Card with proper elevation */}
        <div className="bg-white backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden transform transition-all duration-300 hover:shadow-2xl">
          {/* App Bar with logo */}
          <div className="px-10 pt-16 pb-10 text-center bg-gradient-to-b from-white to-gray-50">
            {/* Material Design FAB-style app icon */}
            <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg transform transition-transform hover:scale-105">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z" />
              </svg>
            </div>
            <h1 className="text-3xl font-semibold text-gray-900 mb-3">Home Aid Kit</h1>
            <p className="text-base text-gray-600">Medication Management</p>
          </div>

          {/* Welcome Section */}
          <div className="px-10 pb-10">
            <div className="text-center mb-10">
              <h2 className="text-4xl font-light text-gray-900 mb-4">
                {isLogin ? 'Welcome back' : 'Create account'}
              </h2>
              <p className="text-lg text-gray-600 leading-relaxed">
                {isLogin
                  ? 'Sign in to manage your household medications'
                  : 'Join to start managing your medications'
                }
              </p>
            </div>

            {/* Error Alert - Material Design Snackbar style */}
            {error && (
              <div className="mb-10 bg-red-50 border-2 border-red-200 rounded-xl p-5 flex items-start gap-4 shadow-sm">
                <div className="flex-shrink-0">
                  <svg className="w-6 h-6 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-red-800 text-base font-medium">{error}</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-red-400 hover:text-red-600 transition-colors p-1 rounded-full hover:bg-red-100"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            <form className="space-y-8" onSubmit={handleSubmit(onSubmit)}>
              {/* Email Field - Material Design Outlined TextField */}
              <div className="space-y-3">
                <div className="relative">
                  <input
                    {...registerField('email')}
                    type="email"
                    autoComplete="email"
                    placeholder="Email Address"
                    className={`w-full px-5 py-5 text-lg text-gray-900 bg-transparent border-2 rounded-xl transition-all duration-300 focus:outline-none hover:border-blue-300 ${errors.email
                        ? 'border-red-400 focus:border-red-500'
                        : 'border-gray-200 focus:border-blue-500'
                      }`}
                  />
                </div>
                {errors.email && (
                  <p className="text-red-500 text-base ml-1 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Password Field - Material Design Outlined TextField */}
              <div className="space-y-3">
                <div className="relative">
                  <input
                    {...registerField('password')}
                    type="password"
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                    placeholder="Password"
                    className={`w-full px-5 py-5 text-lg text-gray-900 bg-transparent border-2 rounded-xl transition-all duration-300 focus:outline-none hover:border-blue-300 ${errors.password
                        ? 'border-red-400 focus:border-red-500'
                        : 'border-gray-200 focus:border-blue-500'
                      }`}
                  />
                </div>
                {errors.password && (
                  <p className="text-red-500 text-base ml-1 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {errors.password.message}
                  </p>
                )}
              </div>

              {/* Confirm Password Field (Register only) */}
              {!isLogin && (
                <div className="space-y-3">
                  <div className="relative">
                    <input
                      {...registerField('confirmPassword')}
                      type="password"
                      autoComplete="new-password"
                      placeholder="Confirm Password"
                      className={`w-full px-5 py-5 text-lg text-gray-900 bg-transparent border-2 rounded-xl transition-all duration-300 focus:outline-none hover:border-blue-300 ${errors.confirmPassword
                          ? 'border-red-500 focus:border-red-600'
                          : 'border-gray-300 focus:border-blue-600'
                        }`}
                    />
                  </div>
                  {errors.confirmPassword && (
                    <p className="text-red-600 text-base ml-1 flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {errors.confirmPassword.message}
                    </p>
                  )}
                </div>
              )}

              {/* Primary Action Button - Material Design Contained Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-6 px-8 rounded-xl font-semibold text-xl transition-all duration-300 hover:from-blue-700 hover:to-blue-800 hover:shadow-2xl hover:-translate-y-0.5 focus:outline-none focus:ring-4 focus:ring-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:transform-none disabled:hover:shadow-none flex items-center justify-center gap-3 min-h-[72px] shadow-lg"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-7 h-7 border-3 border-white border-t-transparent rounded-full animate-spin" />
                    <span>{isLogin ? 'Signing in...' : 'Creating account...'}</span>
                  </>
                ) : (
                  <span>{isLogin ? 'Sign In' : 'Create Account'}</span>
                )}
              </button>

              {/* Divider */}
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-base">
                  <span className="px-3 bg-white text-gray-500">or</span>
                </div>
              </div>

              {/* Social Login Buttons - Material Design Outlined Buttons */}
              <div className="space-y-5">
                <button
                  type="button"
                  className="w-full border-2 border-gray-200 text-gray-700 py-5 px-8 rounded-xl font-medium text-lg transition-all duration-300 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-gray-500/20 flex items-center justify-center gap-4 min-h-[64px] group"
                >
                  <svg className="w-7 h-7" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  <span className="group-hover:text-gray-900 transition-colors">Continue with Google</span>
                </button>

                <button
                  type="button"
                  className="w-full border-2 border-gray-200 text-gray-700 py-5 px-8 rounded-xl font-medium text-lg transition-all duration-300 hover:border-gray-300 hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-gray-500/20 flex items-center justify-center gap-4 min-h-[64px] group"
                >
                  <svg className="w-7 h-7 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                  </svg>
                  <span className="group-hover:text-gray-900 transition-colors">Continue with Facebook</span>
                </button>
              </div>
            </form>
          </div>

          {/* Sign up/Sign in Toggle */}
          <div className="border-t border-gray-100 px-10 py-8 bg-gradient-to-b from-gray-50 to-gray-100">
            <div className="flex justify-between items-center">
              {/* Forgot Password Link (Login only) */}
              {isLogin && (
                <button
                  type="button"
                  className="text-base text-blue-600 hover:text-blue-700 font-medium transition-colors hover:underline"
                >
                  Forgot password?
                </button>
              )}

              <div className={isLogin ? '' : 'mx-auto'}>
                <span className="text-gray-600 text-base">
                  {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
                </span>
                <button
                  type="button"
                  onClick={toggleMode}
                  className="text-blue-600 hover:text-blue-700 font-semibold text-base transition-all duration-200 hover:underline"
                >
                  {isLogin ? 'Sign up' : 'Sign in'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
