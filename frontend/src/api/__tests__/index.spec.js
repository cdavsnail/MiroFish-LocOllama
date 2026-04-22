import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import MockAdapter from 'axios-mock-adapter'
import service, { requestWithRetry } from '../index'
import i18n from '../../i18n'

// Mock i18n
vi.mock('../../i18n', () => ({
  default: {
    global: {
      locale: {
        value: 'en'
      }
    }
  }
}))

describe('api/index.js', () => {
  let mock

  beforeEach(() => {
    // Create a new mock adapter instance for the axios service
    mock = new MockAdapter(service)

    // Clear mocks before each test
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
  })

  afterEach(() => {
    // Reset mock adapter after each test
    mock.reset()
    vi.restoreAllMocks()
  })

  describe('Request Interceptor', () => {
    it('should add Accept-Language header based on i18n.global.locale.value', async () => {
      mock.onGet('/test').reply(200, { success: true })

      const response = await service.get('/test')

      expect(mock.history.get.length).toBe(1)
      expect(mock.history.get[0].headers['Accept-Language']).toBe('en')
    })
  })

  describe('Response Interceptor', () => {
    it('should return response data directly on success', async () => {
      const mockData = { success: true, data: 'test data' }
      mock.onGet('/success').reply(200, mockData)

      const response = await service.get('/success')

      expect(response).toEqual(mockData)
    })

    it('should return response data when success field is undefined', async () => {
      const mockData = { data: 'test data' }
      mock.onGet('/undefined-success').reply(200, mockData)

      const response = await service.get('/undefined-success')

      expect(response).toEqual(mockData)
    })

    it('should reject and log error when response data success is false', async () => {
      const mockErrorData = { success: false, error: 'Custom Error Message' }
      mock.onGet('/error').reply(200, mockErrorData)

      await expect(service.get('/error')).rejects.toThrow('Custom Error Message')
      expect(console.error).toHaveBeenCalledWith('API Error:', 'Custom Error Message')
    })

    it('should log timeout error', async () => {
      mock.onGet('/timeout').timeout()

      await expect(service.get('/timeout')).rejects.toThrow()
      expect(console.error).toHaveBeenCalledWith('Request timeout')
    })

    it('should log network error', async () => {
      mock.onGet('/network-error').networkError()

      await expect(service.get('/network-error')).rejects.toThrow()
      expect(console.error).toHaveBeenCalledWith('Network error - please check your connection')
    })
  })

  describe('requestWithRetry', () => {
    it('should return result if the first request succeeds', async () => {
      const mockFn = vi.fn().mockResolvedValue('success')

      const result = await requestWithRetry(mockFn, 3, 10)

      expect(result).toBe('success')
      expect(mockFn).toHaveBeenCalledTimes(1)
    })

    it('should retry and succeed after failures', async () => {
      const mockFn = vi.fn()
        .mockRejectedValueOnce(new Error('fail 1'))
        .mockRejectedValueOnce(new Error('fail 2'))
        .mockResolvedValueOnce('success on 3')

      const result = await requestWithRetry(mockFn, 3, 10)

      expect(result).toBe('success on 3')
      expect(mockFn).toHaveBeenCalledTimes(3)
      expect(console.warn).toHaveBeenCalledTimes(2)
    })

    it('should throw error if all retries fail', async () => {
      const error = new Error('persistent fail')
      const mockFn = vi.fn().mockRejectedValue(error)

      await expect(requestWithRetry(mockFn, 3, 10)).rejects.toThrow('persistent fail')

      expect(mockFn).toHaveBeenCalledTimes(3)
      expect(console.warn).toHaveBeenCalledTimes(2)
    })
  })
})
