'use client'

import { useCallback } from 'react'
import { useItemGroupStore } from '@/store/itemGroupStore'
import { ItemGroupFormData, AddItemToGroupFormData } from '@/lib/validations/itemGroup'
import { apiFetch, apiUrl } from '@/lib/api/client'
import toast from 'react-hot-toast'

export function useItemGroups() {
  const {
    groups,
    currentGroup,
    isLoading,
    error,
    filters,
    setGroups,
    setCurrentGroup,
    addGroup,
    updateGroup,
    removeGroup,
    setLoading,
    setError,
    setFilters,
    resetFilters,
  } = useItemGroupStore()

  const fetchGroups = useCallback(async (options?: {
    search?: string
    silent?: boolean
  }) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL(apiUrl('/v1/item-groups'))
      if (options?.search) url.searchParams.set('search', options.search)

      const response = await fetch(url.toString(), { credentials: 'include' })

      // Handle permission errors silently - just set empty array
      if (response.status === 401 || response.status === 403) {
        setGroups([])
        return
      }

      if (!response.ok) {
        throw new Error('Error al obtener grupos')
      }

      const data = await response.json()
      setGroups(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      if (!options?.silent) {
        toast.error(message)
      }
    } finally {
      setLoading(false)
    }
  }, [setGroups, setLoading, setError])

  const fetchGroup = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/item-groups/${id}`)

      if (!response.ok) {
        throw new Error('Error al obtener grupo')
      }

      const data = await response.json()
      setCurrentGroup(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [setCurrentGroup, setLoading, setError])

  const createGroup = useCallback(async (data: ItemGroupFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch('/v1/item-groups', {
        method: 'POST',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al crear grupo')
      }

      const newGroup = await response.json()
      addGroup(newGroup)
      toast.success('Grupo creado exitosamente')
      return newGroup
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [addGroup, setLoading, setError])

  const editGroup = useCallback(async (id: string, data: ItemGroupFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/item-groups/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al actualizar grupo')
      }

      const updatedGroup = await response.json()
      updateGroup(id, updatedGroup)
      toast.success('Grupo actualizado exitosamente')
      return updatedGroup
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateGroup, setLoading, setError])

  const deleteGroup = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/item-groups/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al eliminar grupo')
      }

      removeGroup(id)
      toast.success('Grupo eliminado exitosamente')
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [removeGroup, setLoading, setError])

  const addItemToGroup = useCallback(async (groupId: string, data: AddItemToGroupFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/item-groups/${groupId}/items`, {
        method: 'POST',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al agregar item al grupo')
      }

      const updatedGroup = await response.json()
      updateGroup(groupId, updatedGroup)
      toast.success('Item agregado al grupo')
      return updatedGroup
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateGroup, setLoading, setError])

  const removeItemFromGroup = useCallback(async (groupId: string, itemId: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/item-groups/${groupId}/items/${itemId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al quitar item del grupo')
      }

      const updatedGroup = await response.json()
      updateGroup(groupId, updatedGroup)
      toast.success('Item removido del grupo')
      return updatedGroup
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateGroup, setLoading, setError])

  return {
    groups,
    currentGroup,
    isLoading,
    error,
    filters,
    setFilters,
    resetFilters,
    fetchGroups,
    fetchGroup,
    createGroup,
    editGroup,
    deleteGroup,
    addItemToGroup,
    removeItemFromGroup,
  }
}
