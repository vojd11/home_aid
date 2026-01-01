import React from 'react'
import { useTranslation } from 'react-i18next'
import { 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel, 
  Box,
  Typography
} from '@mui/material'
import { Language as LanguageIcon } from '@mui/icons-material'
import { SUPPORTED_LANGUAGES, changeLanguage, type LanguageCode } from '../utils/language'

interface LanguageSelectorProps {
  variant?: 'outlined' | 'filled' | 'standard'
  size?: 'small' | 'medium'
  showLabel?: boolean
  iconOnly?: boolean
}

export default function LanguageSelector({ 
  variant = 'outlined', 
  size = 'medium',
  showLabel = true,
  iconOnly = false
}: LanguageSelectorProps) {
  const { i18n, t } = useTranslation()

  const handleLanguageChange = async (event: any) => {
    const newLanguage = event.target.value as LanguageCode
    await changeLanguage(newLanguage)
  }

  if (iconOnly) {
    return (
      <FormControl size={size}>
        <Select
          value={i18n.language}
          onChange={handleLanguageChange}
          variant={variant}
          sx={{
            minWidth: 60,
            '& .MuiSelect-select': {
              paddingLeft: 1,
              paddingRight: '24px !important'
            }
          }}
          startAdornment={<LanguageIcon sx={{ mr: 1, color: 'action.active' }} />}
          renderValue={(value: string) => {
            const lang = SUPPORTED_LANGUAGES.find(l => l.code === value)
            return lang?.code.toUpperCase() || 'EN'
          }}
        >
          {SUPPORTED_LANGUAGES.map((language) => (
            <MenuItem key={language.code} value={language.code}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {language.code.toUpperCase()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {language.nativeName}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    )
  }

  return (
    <FormControl variant={variant} size={size} sx={{ minWidth: 120 }}>
      {showLabel && (
        <InputLabel id="language-select-label">
          {t('settings.language')}
        </InputLabel>
      )}
      <Select
        labelId="language-select-label"
        value={i18n.language}
        onChange={handleLanguageChange}
        label={showLabel ? t('settings.language') : undefined}
        startAdornment={<LanguageIcon sx={{ mr: 1, color: 'action.active' }} />}
      >
        {SUPPORTED_LANGUAGES.map((language) => (
          <MenuItem key={language.code} value={language.code}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {language.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ({language.nativeName})
              </Typography>
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}
