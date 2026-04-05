import { api } from './client'
import type { LoginResponse, UserRead } from './types'

export async function login(email: string, password: string): Promise<LoginResponse> {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post<LoginResponse>('/api/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function getCurrentUser(): Promise<UserRead> {
  const { data } = await api.get<UserRead>('/api/auth/me')
  return data
}
