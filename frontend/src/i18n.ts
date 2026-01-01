import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import enTranslations from './locales/en.json'
import uaTranslations from './locales/ua.json'

const resources = {
  en: {
    translation: enTranslations
  },
  ua: {
    translation: uaTranslations
  }
}

// Get saved language from localStorage or use browser language
const getInitialLanguage = () => {
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage && resources[savedLanguage as keyof typeof resources]) {
    return savedLanguage
  }
  
  // Try to get language from browser
  const browserLanguage = navigator.language.split('-')[0]
  if (resources[browserLanguage as keyof typeof resources]) {
    return browserLanguage
  }
  
  // Default to English
  return 'en'
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    
    interpolation: {
      escapeValue: false // React already does escaping
    },
    
    // Save language preference when changed
    saveMissing: false,
    
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  })

// Save language to localStorage when it changes
i18n.on('languageChanged', (lng: string) => {
  localStorage.setItem('language', lng)
})

export default i18n
