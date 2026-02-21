'use client'

import { useCallback } from 'react'
import { useClientStore } from '@/store/clientStore'
import { ClientFormData } from '@/lib/validations/client'
import { apiFetch, apiUrl } from '@/lib/api/client'
import toast from 'react-hot-toast'

export function useClients() {
  const {
    clients,
    currentClient,
    isLoading,
    error,
    searchQuery,
    setClients,
    setCurrentClient,
    addClient,
    updateClient,
    removeClient,
    setLoading,
    setError,
    setSearchQuery,
  } = useClientStore()

  const fetchClients = useCallback(async (search?: string) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL(apiUrl('/v1/clients'))
      if (search) {
        url.searchParams.set('search', search)
      }

      const response = await fetch(url.toString(), { credentials: 'include' })

      if (!response.ok) {
        throw new Error('Error al obtener clientes')
      }

      const data = await response.json()
      setClients(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }, [setClients, setLoading, setError])

  const fetchClient = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/clients/${id}`)

      if (!response.ok) {
        throw new Error('Error al obtener cliente')
      }

      const data = await response.json()
      setCurrentClient(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [setCurrentClient, setLoading, setError])

  const createClient = useCallback(async (data: ClientFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch('/v1/clients', {
        method: 'POST',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al crear cliente')
      }

      const newClient = await response.json()
      addClient(newClient)
      toast.success('Cliente creado exitosamente')
      return newClient
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [addClient, setLoading, setError])

  const editClient = useCallback(async (id: string, data: ClientFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/clients/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al actualizar cliente')
      }

      const updatedClient = await response.json()
      updateClient(id, updatedClient)
      toast.success('Cliente actualizado exitosamente')
      return updatedClient
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateClient, setLoading, setError])

  const deleteClient = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/clients/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al eliminar cliente')
      }

      removeClient(id)
      toast.success('Cliente eliminado exitosamente')
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [removeClient, setLoading, setError])

  return {
    clients,
    currentClient,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    fetchClients,
    fetchClient,
    createClient,
    editClient,
    deleteClient,
  }
}
