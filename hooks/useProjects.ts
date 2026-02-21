'use client'

import { useCallback } from 'react'
import { useProjectStore } from '@/store/projectStore'
import { ProjectFormData, ProjectStatus, Priority } from '@/lib/validations/project'
import { apiFetch, apiUrl } from '@/lib/api/client'
import toast from 'react-hot-toast'

interface FetchProjectsOptions {
  search?: string
  status?: ProjectStatus
  priority?: Priority
  clientId?: string
  assignedTo?: string
}

export function useProjects() {
  const {
    projects,
    currentProject,
    isLoading,
    error,
    searchQuery,
    filters,
    setProjects,
    setCurrentProject,
    addProject,
    updateProject,
    removeProject,
    setLoading,
    setError,
    setSearchQuery,
    setFilters,
    clearFilters,
  } = useProjectStore()

  const fetchProjects = useCallback(async (options?: FetchProjectsOptions) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL(apiUrl('/v1/projects'))

      if (options?.search) url.searchParams.set('search', options.search)
      if (options?.status) url.searchParams.set('status', options.status)
      if (options?.priority) url.searchParams.set('priority', options.priority)
      if (options?.clientId) url.searchParams.set('clientId', options.clientId)
      if (options?.assignedTo) url.searchParams.set('assignedTo', options.assignedTo)

      const response = await fetch(url.toString(), { credentials: 'include' })

      if (!response.ok) {
        throw new Error('Error al obtener proyectos')
      }

      const data = await response.json()
      setProjects(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }, [setProjects, setLoading, setError])

  const fetchProject = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/projects/${id}`)

      if (!response.ok) {
        throw new Error('Error al obtener proyecto')
      }

      const data = await response.json()
      setCurrentProject(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [setCurrentProject, setLoading, setError])

  const createProject = useCallback(async (data: ProjectFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch('/v1/projects', {
        method: 'POST',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al crear proyecto')
      }

      const newProject = await response.json()
      addProject(newProject)
      toast.success('Proyecto creado exitosamente')
      return newProject
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [addProject, setLoading, setError])

  const editProject = useCallback(async (id: string, data: ProjectFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/projects/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al actualizar proyecto')
      }

      const updatedProject = await response.json()
      updateProject(id, updatedProject)
      toast.success('Proyecto actualizado exitosamente')
      return updatedProject
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateProject, setLoading, setError])

  const deleteProject = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await apiFetch(`/v1/projects/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al eliminar proyecto')
      }

      removeProject(id)
      toast.success('Proyecto eliminado exitosamente')
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [removeProject, setLoading, setError])

  return {
    projects,
    currentProject,
    isLoading,
    error,
    searchQuery,
    filters,
    setSearchQuery,
    setFilters,
    clearFilters,
    fetchProjects,
    fetchProject,
    createProject,
    editProject,
    deleteProject,
  }
}
