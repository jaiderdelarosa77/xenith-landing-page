'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useSession, signOut } from 'next-auth/react'
import { useAuthStore } from '@/store/authStore'

export function useAuth() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const { user, setUser, logout: logoutStore, isLoading, setLoading } = useAuthStore()

  const isPending = status === 'loading'

  // Sync session with store
  useEffect(() => {
    if (isPending) {
      setLoading(true)
      return
    }

    if (session?.user) {
      setUser({
        id: session.user.id as string,
        email: session.user.email as string,
        name: session.user.name || null,
        image: session.user.image || null,
      })
      setLoading(false)
    } else if (!session && !isPending) {
      setUser(null)
      setLoading(false)
    }
  }, [session, isPending, setUser, setLoading])

  const logout = async () => {
    try {
      await signOut({ redirect: false })
      logoutStore()
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return {
    user: session?.user || user,
    isAuthenticated: !!session?.user,
    isLoading: isPending || isLoading,
    logout,
  }
}
