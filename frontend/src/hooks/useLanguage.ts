import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  changeLanguage, 
  getCurrentLanguage, 
  getLanguageFromStorage, 
  getBrowserLanguage,
  type LanguageCode 
} from '../utils/language'

export const useLanguage = () => {
  const { i18n } = useTranslation()

  // Initialize language on hook mount
  useEffect(() => {
    const initializeLanguage = async () => {
      // Priority: localStorage > browser language > default
      const savedLanguage = getLanguageFromStorage()
      const targetLanguage = savedLanguage || getBrowserLanguage()
      
      if (targetLanguage !== getCurrentLanguage()) {
        await changeLanguage(targetLanguage)
      }
    }

    initializeLanguage()
  }, [])

  const setLanguage = async (languageCode: LanguageCode) => {
    return await changeLanguage(languageCode)
  }

  const currentLanguage = getCurrentLanguage()

  return {
    currentLanguage,
    setLanguage,
    isRTL: false, // Add RTL support if needed for future languages
  }
}
