'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { apiFetch } from '@/lib/api/client'

export function useAuth() {
  const {
    user,
    setUser,
    logout: logoutStore,
    isLoading,
    setLoading,
    hasCheckedSession,
    markSessionChecked,
  } = useAuthStore()

  useEffect(() => {
    if (hasCheckedSession) return
    markSessionChecked()

    const loadSession = async () => {
      setLoading(true)
      try {
        const response = await apiFetch('/v1/auth/me')
        if (!response.ok) {
          setUser(null)
          return
        }
        const data = await response.json()
        setUser({
          id: data.id,
          email: data.email,
          name: data.name || null,
          image: data.image || null,
        })
      } catch {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    loadSession()
  }, [hasCheckedSession, markSessionChecked, setLoading, setUser])

  const logout = async () => {
    try {
      await apiFetch('/v1/auth/logout', { method: 'POST' })
    } finally {
      logoutStore()
      if (typeof window !== 'undefined') {
        localStorage.removeItem('xenith-auth-storage')
      }
      setUser(null)
    }
  }

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    logout,
  }
}
