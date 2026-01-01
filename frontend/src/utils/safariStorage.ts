/**
 * Safari-compatible storage utility
 * 
 * Safari sometimes has issues with localStorage in private browsing mode
 * or in certain contexts. This utility provides a fallback mechanism.
 */

interface SafariStorage {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
  removeItem(key: string): void
}

class SafariStorageImpl implements SafariStorage {
  private fallbackStorage = new Map<string, string>()
  private isLocalStorageAvailable = this.checkLocalStorageAvailability()

  private checkLocalStorageAvailability(): boolean {
    try {
      const testKey = '__localStorage_test__'
      localStorage.setItem(testKey, 'test')
      localStorage.removeItem(testKey)
      return true
    } catch {
      return false
    }
  }

  getItem(key: string): string | null {
    if (this.isLocalStorageAvailable) {
      try {
        return localStorage.getItem(key)
      } catch {
        // Fall back to in-memory storage
      }
    }
    return this.fallbackStorage.get(key) || null
  }

  setItem(key: string, value: string): void {
    if (this.isLocalStorageAvailable) {
      try {
        localStorage.setItem(key, value)
        return
      } catch {
        // Fall back to in-memory storage
      }
    }
    this.fallbackStorage.set(key, value)
  }

  removeItem(key: string): void {
    if (this.isLocalStorageAvailable) {
      try {
        localStorage.removeItem(key)
      } catch {
        // Fall back to in-memory storage
      }
    }
    this.fallbackStorage.delete(key)
  }
}

export const safariStorage = new SafariStorageImpl()
