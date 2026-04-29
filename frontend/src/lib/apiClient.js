import axios from 'axios'

const DEFAULT_TIMEOUT_MS = 180000
const FALLBACK_API_BASE_URL = 'http://localhost:8000'

const baseURL = (import.meta.env.VITE_API_BASE_URL || FALLBACK_API_BASE_URL).replace(/\/+$/, '')

export const apiClient = axios.create({
  baseURL,
  timeout: DEFAULT_TIMEOUT_MS,
})

export function getErrorMessage(error, fallbackMessage) {
  return error?.response?.data?.detail || error?.message || fallbackMessage
}

export function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

export function getApiBaseUrl() {
  return baseURL
}
