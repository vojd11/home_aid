import i18n from '../i18n'

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'ua', name: 'Ukrainian', nativeName: 'Українська' }
] as const

export type LanguageCode = typeof SUPPORTED_LANGUAGES[number]['code']

export const changeLanguage = async (languageCode: LanguageCode) => {
  try {
    await i18n.changeLanguage(languageCode)
    localStorage.setItem('language', languageCode)
    return true
  } catch (error) {
    console.error('Failed to change language:', error)
    return false
  }
}

export const getCurrentLanguage = (): LanguageCode => {
  return i18n.language as LanguageCode
}

export const getLanguageFromStorage = (): LanguageCode | null => {
  const saved = localStorage.getItem('language')
  if (saved && SUPPORTED_LANGUAGES.some(lang => lang.code === saved)) {
    return saved as LanguageCode
  }
  return null
}

export const getBrowserLanguage = (): LanguageCode => {
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LANGUAGES.some(lang => lang.code === browserLang)) {
    return browserLang as LanguageCode
  }
  return 'en' // default fallback
}

export const getLanguageName = (code: LanguageCode): string => {
  const language = SUPPORTED_LANGUAGES.find(lang => lang.code === code)
  return language?.name || 'Unknown'
}

export const getNativeLanguageName = (code: LanguageCode): string => {
  const language = SUPPORTED_LANGUAGES.find(lang => lang.code === code)
  return language?.nativeName || 'Unknown'
}
