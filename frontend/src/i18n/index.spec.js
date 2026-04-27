import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock local storage before importing i18n
const localStorageMock = (() => {
  let store = {}
  return {
    getItem(key) {
      return store[key] || null
    },
    setItem(key, value) {
      store[key] = value.toString()
    },
    clear() {
      store = {}
    }
  }
})()

vi.stubGlobal('localStorage', localStorageMock)

// Need to reset modules to clear imported glob and module state
beforeEach(() => {
  localStorage.clear()
  vi.resetModules()
})

describe('i18n Configuration', async () => {
  it('should initialize with default locale "zh" when localStorage is empty', async () => {
    const { default: i18n } = await import('./index.js')

    expect(i18n.global.locale.value).toBe('zh')
    // Check fallbackLocale is either en or zh to match potential different configurations
    expect(['zh', 'en']).toContain(i18n.global.fallbackLocale.value)
  })

  it('should initialize with locale from localStorage if available', async () => {
    localStorage.setItem('locale', 'en')
    const { default: i18n } = await import('./index.js')

    expect(i18n.global.locale.value).toBe('en')
    expect(['zh', 'en']).toContain(i18n.global.fallbackLocale.value)
  })

  it('should have availableLocales populated correctly', async () => {
    const { availableLocales } = await import('./index.js')

    expect(availableLocales).toBeInstanceOf(Array)
    expect(availableLocales.length).toBeGreaterThan(0)

    // Check structure of elements in availableLocales
    expect(availableLocales[0]).toHaveProperty('key')
    expect(availableLocales[0]).toHaveProperty('label')

    // Verify common locales are present
    const keys = availableLocales.map(l => l.key)
    expect(keys).toContain('zh')
    expect(keys).toContain('en')
  })

  it('should correctly load and provide translations', async () => {
    const { default: i18n } = await import('./index.js')

    // Ensure that some standard translation keys can be resolved
    // Since we don't know exact keys, we'll check if messages object has content
    const messages = i18n.global.messages.value

    expect(messages).toHaveProperty('zh')
    expect(messages).toHaveProperty('en')

    // Just verify the objects are not empty
    expect(Object.keys(messages.zh).length).toBeGreaterThan(0)
    expect(Object.keys(messages.en).length).toBeGreaterThan(0)
  })
})
