// @ts-nocheck
import { useState, useEffect, useRef } from 'react'
import { TextField, InputAdornment, IconButton } from '@mui/material'
import { Search, Clear } from '@mui/icons-material'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  debounceMs?: number
  className?: string
}

export default function SearchBar({ 
  value, 
  onChange, 
  placeholder = 'Search medications...', 
  debounceMs = 300,
  className = ''
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value)
  const inputRef = useRef<HTMLInputElement>(null)
  const isTypingRef = useRef(false)

  // Debounce the search input
  useEffect(() => {
    const handler = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue)
        isTypingRef.current = false
      }
    }, debounceMs)

    return () => {
      clearTimeout(handler)
    }
  }, [localValue, onChange, debounceMs, value])

  // Update local value when external value changes (but only if user is not actively typing)
  useEffect(() => {
    if (value !== localValue && !isTypingRef.current) {
      setLocalValue(value)
    }
  }, [value, localValue])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    isTypingRef.current = true
    setLocalValue(e.target.value)
  }

  const handleClear = () => {
    isTypingRef.current = false
    setLocalValue('')
    onChange('')
  }

  const handleFocus = () => {
    isTypingRef.current = true
  }

  const handleBlur = () => {
    // Small delay to allow for proper state sync
    setTimeout(() => {
      isTypingRef.current = false
    }, 100)
  }

  return (
    <TextField
      ref={inputRef}
      value={localValue}
      onChange={handleInputChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      placeholder={placeholder}
      variant="outlined"
      fullWidth
      className={className}
      autoComplete="off"
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <Search sx={{ color: 'action.active', ml: 0.5 }} />
          </InputAdornment>
        ),
        endAdornment: localValue && (
          <InputAdornment position="end">
            <IconButton
              onClick={handleClear}
              edge="end"
              size="small"
              sx={{ 
                color: 'action.active',
                mr: 0.5,
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
              title="Clear search"
              aria-label="Clear search"
            >
              <Clear fontSize="small" />
            </IconButton>
          </InputAdornment>
        ),
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: '12px',
          backgroundColor: 'background.paper',
          transition: 'all 0.2s ease-in-out',
          paddingLeft: '8px',
          paddingRight: '8px',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          },
          '&.Mui-focused': {
            boxShadow: '0 8px 24px rgba(37, 99, 235, 0.15)',
          },
        },
        '& .MuiInputAdornment-root': {
          marginLeft: '4px',
          marginRight: '4px',
        },
      }}
    />
  )
}
