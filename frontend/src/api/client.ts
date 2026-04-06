import axios, { AxiosError } from 'axios'

// Frontend is served from the same origin as the API -- no absolute URL needed.
const baseURL = ''

export const TOKEN_STORAGE_KEY = 'hlp.token'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname
      if (path !== '/login') {
        localStorage.removeItem(TOKEN_STORAGE_KEY)
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string } | undefined
    if (data?.detail) return data.detail
    return err.message
  }
  if (err instanceof Error) return err.message
  return 'An unexpected error occurred'
}
