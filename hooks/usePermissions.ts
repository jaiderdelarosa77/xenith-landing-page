'use client'

import { useState, useEffect, useCallback } from 'react'
import { SystemModule, SUPERADMIN_EMAIL } from '@/lib/validations/user'
import { apiFetch } from '@/lib/api/client'
import { useAuthStore } from '@/store/authStore'

interface Permission {
  module: string
  canView: boolean
  canEdit: boolean
}

interface UsePermissionsReturn {
  permissions: Permission[]
  isLoading: boolean
  canView: (module: SystemModule) => boolean
  canEdit: (module: SystemModule) => boolean
  isSuperAdmin: boolean
  isAdmin: boolean
  refetch: () => Promise<void>
}

export function usePermissions(): UsePermissionsReturn {
  const user = useAuthStore((state) => state.user)
  const authLoading = useAuthStore((state) => state.isLoading)
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [userRole, setUserRole] = useState<string | null>(null)

  const isSuperAdmin = user?.email === SUPERADMIN_EMAIL
  const isAdmin = isSuperAdmin || userRole === 'ADMIN'

  const fetchPermissions = useCallback(async () => {
    if (authLoading) return

    if (!user) {
      setPermissions([])
      setIsLoading(false)
      return
    }

    // Superadmin tiene todos los permisos
    if (isSuperAdmin) {
      setIsLoading(false)
      return
    }

    try {
      const response = await apiFetch('/v1/profile')

      // Handle unauthorized/forbidden silently (user is logging out)
      if (response.status === 401 || response.status === 403) {
        setPermissions([])
        setIsLoading(false)
        return
      }

      if (response.ok) {
        const data = await response.json()
        setPermissions(data.permissions || [])
        setUserRole(data.role || null)
      }
    } catch (error) {
      console.error('Error fetching permissions:', error)
    } finally {
      setIsLoading(false)
    }
  }, [user, authLoading, isSuperAdmin])

  useEffect(() => {
    fetchPermissions()
  }, [fetchPermissions])

  const canView = useCallback(
    (module: SystemModule): boolean => {
      // Superadmin tiene todos los permisos
      if (isSuperAdmin) return true

      const permission = permissions.find((p) => p.module === module)
      return permission?.canView || false
    },
    [permissions, isSuperAdmin]
  )

  const canEdit = useCallback(
    (module: SystemModule): boolean => {
      // Superadmin tiene todos los permisos
      if (isSuperAdmin) return true

      const permission = permissions.find((p) => p.module === module)
      return permission?.canEdit || false
    },
    [permissions, isSuperAdmin]
  )

  return {
    permissions,
    isLoading: authLoading || isLoading,
    canView,
    canEdit,
    isSuperAdmin,
    isAdmin,
    refetch: fetchPermissions,
  }
}
