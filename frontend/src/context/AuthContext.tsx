import { createContext, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import * as authApi from '@/api/auth'
import { TOKEN_STORAGE_KEY } from '@/api/client'
import type { UserRead, UserRoleType } from '@/api/types'

export interface AuthContextValue {
  user: UserRead | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  hasRole: (role: UserRoleType) => boolean
  hasAnyRole: (roles: UserRoleType[]) => boolean
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY))
  const [user, setUser] = useState<UserRead | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(Boolean(localStorage.getItem(TOKEN_STORAGE_KEY)))

  const refreshUser = useCallback(async () => {
    try {
      const me = await authApi.getCurrentUser()
      setUser(me)
    } catch {
      setUser(null)
      setToken(null)
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    const existing = localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!existing) {
      setIsLoading(false)
      return
    }
    ;(async () => {
      try {
        const me = await authApi.getCurrentUser()
        if (!cancelled) setUser(me)
      } catch {
        if (!cancelled) {
          localStorage.removeItem(TOKEN_STORAGE_KEY)
          setToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const resp = await authApi.login(email, password)
    localStorage.setItem(TOKEN_STORAGE_KEY, resp.access_token)
    setToken(resp.access_token)
    const me = await authApi.getCurrentUser()
    setUser(me)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const hasRole = useCallback((role: UserRoleType) => user?.roles.includes(role) ?? false, [user])
  const hasAnyRole = useCallback(
    (roles: UserRoleType[]) => (user ? roles.some((r) => user.roles.includes(r)) : false),
    [user],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
      refreshUser,
      hasRole,
      hasAnyRole,
    }),
    [user, token, isLoading, login, logout, refreshUser, hasRole, hasAnyRole],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
