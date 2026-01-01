# Localization/Translation Implementation

This document describes the localization system implemented in the Home Aid Kit frontend application.

## Overview

The application now supports multiple languages with automatic language detection, persistence, and easy switching. The implementation uses `react-i18next` for internationalization.

## Supported Languages

- **English (en)** - Default language
- **Russian (ru)** - Secondary language

## Features

### 🌍 Language Detection
- Automatically detects user's browser language on first visit
- Falls back to English if browser language is not supported
- Remembers language preference in localStorage

### 💾 Language Persistence
- User's language choice is saved in browser's localStorage
- Language preference persists across browser sessions
- Automatic restoration of preferred language on app reload

### 🎛️ Language Switching
- Language selector component available in:
  - Login page (top-right corner)
  - Dashboard desktop header (icon-only mode)
  - Dashboard mobile drawer (full selector with labels)
- Instant language switching without page refresh
- Visual feedback with language names in both English and native scripts

## Implementation Details

### Directory Structure
```
frontend/src/
├── locales/
│   ├── en.json          # English translations
│   └── ru.json          # Russian translations
├── components/
│   └── LanguageSelector.tsx  # Language selector component
├── hooks/
│   └── useLanguage.ts   # Language management hook
├── utils/
│   └── language.ts      # Language utilities
└── i18n.ts             # i18next configuration
```

### Key Files

#### Translation Files
- `src/locales/en.json` - English translations organized by feature
- `src/locales/ru.json` - Russian translations with identical structure

#### Components
- `LanguageSelector.tsx` - Reusable language selector with multiple display modes
  - `iconOnly` - Compact icon with language code
  - `showLabel` - Full selector with "Language" label
  - `variant` - Material-UI variant (outlined, filled, standard)

#### Utilities
- `language.ts` - Helper functions for language management
  - Language detection from browser/localStorage
  - Language validation and fallbacks
  - Type-safe language code handling

#### Configuration
- `i18n.ts` - i18next configuration with:
  - Automatic language detection
  - LocalStorage persistence
  - Fallback to English

### Usage Examples

#### Using translations in components:
```tsx
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t } = useTranslation()
  
  return (
    <Typography>
      {t('auth.welcomeBack')}
    </Typography>
  )
}
```

#### Using the language selector:
```tsx
import LanguageSelector from '../components/LanguageSelector'

// Icon-only mode (for headers)
<LanguageSelector iconOnly size="small" />

// Full selector with label
<LanguageSelector variant="outlined" showLabel />
```

## Translation Structure

### Translation Keys Organization
```json
{
  "app": {
    "title": "Application name",
    "subtitle": "Application description"
  },
  "auth": {
    "login": "Login related text",
    "signup": "Signup related text"
  },
  "dashboard": {
    "navigation": "Dashboard navigation",
    "content": "Dashboard content"
  },
  "common": {
    "buttons": "Common buttons and actions",
    "messages": "Common messages"
  }
}
```

## Docker Integration

The localization system works seamlessly with Docker:

1. **Dependencies**: `i18next` and `react-i18next` are installed via package.json
2. **Build Process**: Translation files are included in the Docker image
3. **Runtime**: No server-side dependencies required - all translation logic runs in the browser

## Adding New Languages

To add a new language (e.g., Spanish):

1. Create translation file: `src/locales/es.json`
2. Update language utilities in `src/utils/language.ts`:
   ```ts
   export const SUPPORTED_LANGUAGES = [
     { code: 'en', name: 'English', nativeName: 'English' },
     { code: 'ru', name: 'Russian', nativeName: 'Русский' },
     { code: 'es', name: 'Spanish', nativeName: 'Español' }
   ] as const
   ```
3. Import in `src/i18n.ts`:
   ```ts
   import esTranslations from './locales/es.json'
   
   const resources = {
     en: { translation: enTranslations },
     ru: { translation: ruTranslations },
     es: { translation: esTranslations }
   }
   ```

## Browser Compatibility

The localization system works in all modern browsers and gracefully handles:
- Missing localStorage support (falls back to session-based language)
- Unsupported browser languages (falls back to English)
- Network connectivity issues (uses cached translations)

## Performance

- Translation files are bundled with the application (no runtime loading)
- Language switching is instant (no network requests)
- Minimal bundle size impact (~2KB per language file)
- Tree shaking removes unused translation keys during build
