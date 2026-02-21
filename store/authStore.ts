import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string | null
  image: string | null
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  hasCheckedSession: boolean
  setUser: (user: User | null) => void
  setLoading: (isLoading: boolean) => void
  markSessionChecked: () => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      hasCheckedSession: false,

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
          isLoading: false,
          hasCheckedSession: true,
        }),

      setLoading: (isLoading) =>
        set({ isLoading }),

      markSessionChecked: () =>
        set({ hasCheckedSession: true }),

      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          hasCheckedSession: true,
        }),
    }),
    {
      name: 'xenith-auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
