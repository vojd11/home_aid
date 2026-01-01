// @ts-nocheck
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Box, Paper, Typography, Button, Alert, Divider } from '@mui/material'
import { useAuth } from '../hooks/useAuth'
import { LoginForm, LoginSchema, RegisterForm, RegisterSchema } from '../types'
import PasswordField from '../components/PasswordField'
import EmailField from '../components/EmailField'
import LanguageSelector from '../components/LanguageSelector'

export default function LoginPageMUI() {
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState(null)
  const { user, login, register } = useAuth()
  const { t } = useTranslation()

  const {
    register: registerField,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    resolver: zodResolver(isLogin ? LoginSchema : RegisterSchema),
  })

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/" replace />
  }

  const onSubmit = async (data) => {
    try {
      setError(null)
      if (isLogin) {
        await login(data)
      } else {
        await register(data)
      }
    } catch (error) {
      console.error('Authentication error:', error)
      setError(error?.response?.data?.detail || t('auth.authError'))
    }
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    setError(null)
    reset()
  }

  return (
    <Box 
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #e8eaf6 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 4,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background decoration */}
      <Box
        sx={{
          position: 'absolute',
          top: '-160px',
          right: '-128px',
          width: '320px',
          height: '320px',
          borderRadius: '50%',
          backgroundColor: '#bbdefb',
          opacity: 0.2,
          filter: 'blur(48px)'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '-160px',
          left: '-128px',
          width: '320px',
          height: '320px',
          borderRadius: '50%',
          backgroundColor: '#d1c4e9',
          opacity: 0.2,
          filter: 'blur(48px)'
        }}
      />
      
      {/* Language Selector */}
      <Box
        sx={{
          position: 'absolute',
          top: 20,
          right: 20,
          zIndex: 20
        }}
      >
        <LanguageSelector iconOnly size="small" />
      </Box>
      
      {/* Main container */}
      <Box sx={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: '500px' }}>
        <Paper
          elevation={20}
          sx={{
            borderRadius: '24px',
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}
        >
          {/* App Bar with logo */}
          <Box 
            sx={{ 
              px: 5, 
              pt: 8, 
              pb: 5, 
              textAlign: 'center',
              background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)'
            }}
          >
            <Box
              sx={{
                width: '96px',
                height: '96px',
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 4,
                boxShadow: '0 8px 32px rgba(37, 99, 235, 0.3)',
                transition: 'transform 0.2s ease',
                '&:hover': {
                  transform: 'scale(1.05)'
                }
              }}
            >
              <svg width="48" height="48" fill="white" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z" />
              </svg>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 600, color: '#1f2937', mb: 2 }}>
              {t('app.title')}
            </Typography>
            <Typography variant="h6" sx={{ color: '#6b7280' }}>
              {t('app.subtitle')}
            </Typography>
          </Box>

          {/* Welcome Section */}
          <Box sx={{ px: 5, pb: 5 }}>
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Typography variant="h2" sx={{ fontWeight: 300, color: '#1f2937', mb: 2 }}>
                {isLogin ? t('auth.welcomeBack') : t('auth.createAccount')}
              </Typography>
              <Typography variant="body1" sx={{ color: '#6b7280', fontSize: '1.125rem', lineHeight: 1.6 }}>
                {isLogin 
                  ? t('auth.signInDescription')
                  : t('auth.signUpDescription')
                }
              </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
              <Alert 
                severity="error" 
                onClose={() => setError(null)}
                sx={{ mb: 5, borderRadius: '12px' }}
              >
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {/* Email Field */}
              <EmailField
                {...registerField('email')}
                error={!!errors.email}
                helperText={errors.email?.message}
                size="large"
              />

              {/* Password Field */}
              <PasswordField
                {...registerField('password')}
                label={t('auth.password')}
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                error={!!errors.password}
                helperText={errors.password?.message}
                size="large"
              />

              {/* Confirm Password Field (Register only) */}
              {!isLogin && (
                <PasswordField
                  {...registerField('confirmPassword')}
                  label={t('auth.confirmPassword')}
                  autoComplete="new-password"
                  error={!!errors.confirmPassword}
                  helperText={errors.confirmPassword?.message}
                  size="large"
                />
              )}

              {/* Primary Action Button */}
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={isSubmitting}
                sx={{
                  py: 3,
                  px: 4,
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  borderRadius: '12px',
                  background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                  boxShadow: '0 8px 32px rgba(37, 99, 235, 0.3)',
                  textTransform: 'none',
                  minHeight: '72px',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                    boxShadow: '0 12px 40px rgba(37, 99, 235, 0.4)',
                    transform: 'translateY(-2px)'
                  },
                  '&:disabled': {
                    background: '#9ca3af',
                    transform: 'none',
                    boxShadow: 'none'
                  }
                }}
              >
                {isSubmitting ? (
                  <>{t('auth.processing')}</>
                ) : (
                  <>{isLogin ? t('auth.signIn') : t('auth.createAccountButton')}</>
                )}
              </Button>

              {/* Divider */}
              <Divider sx={{ my: 2 }}>
                <Typography variant="body2" sx={{ color: '#6b7280' }}>{t('common.or')}</Typography>
              </Divider>

              {/* Social Login Buttons */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{
                    py: 2.5,
                    px: 4,
                    fontSize: '1.125rem',
                    fontWeight: 500,
                    borderRadius: '12px',
                    borderWidth: '2px',
                    textTransform: 'none',
                    minHeight: '64px',
                    borderColor: '#e5e7eb',
                    color: '#374151',
                    '&:hover': {
                      borderColor: '#d1d5db',
                      backgroundColor: '#f9fafb',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                    }
                  }}
                  startIcon={
                    <svg width="28" height="28" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                  }
                >
                  {t('auth.continueWithGoogle')}
                </Button>
                
                <Button
                  variant="outlined"
                  size="large"
                  sx={{
                    py: 2.5,
                    px: 4,
                    fontSize: '1.125rem',
                    fontWeight: 500,
                    borderRadius: '12px',
                    borderWidth: '2px',
                    textTransform: 'none',
                    minHeight: '64px',
                    borderColor: '#e5e7eb',
                    color: '#374151',
                    '&:hover': {
                      borderColor: '#d1d5db',
                      backgroundColor: '#f9fafb',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                    }
                  }}
                  startIcon={
                    <svg width="28" height="28" fill="#1877f2" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  }
                >
                  {t('auth.continueWithFacebook')}
                </Button>
              </Box>
            </Box>
          </Box>

          {/* Sign up/Sign in Toggle */}
          <Box 
            sx={{ 
              borderTop: '1px solid #f3f4f6',
              px: 5, 
              py: 4,
              background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)'
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {isLogin && (
                <Button
                  variant="text"
                  sx={{
                    fontSize: '1rem',
                    color: '#2563eb',
                    fontWeight: 500,
                    textTransform: 'none',
                    '&:hover': {
                      color: '#1d4ed8',
                      textDecoration: 'underline',
                      backgroundColor: 'transparent'
                    }
                  }}
                >
                  {t('auth.forgotPassword')}
                </Button>
              )}
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ...(isLogin ? {} : { mx: 'auto' }) }}>
                <Typography variant="body1" sx={{ color: '#6b7280' }}>
                  {isLogin ? t('auth.dontHaveAccount') : t('auth.alreadyHaveAccount')}
                </Typography>
                <Button
                  variant="text"
                  onClick={toggleMode}
                  sx={{
                    fontSize: '1rem',
                    color: '#2563eb',
                    fontWeight: 600,
                    textTransform: 'none',
                    '&:hover': {
                      color: '#1d4ed8',
                      textDecoration: 'underline',
                      backgroundColor: 'transparent'
                    }
                  }}
                >
                  {isLogin ? t('auth.signUp') : t('auth.signIn')}
                </Button>
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Box>
  )
}
