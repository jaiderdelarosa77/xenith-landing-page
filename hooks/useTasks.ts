'use client'

import { useCallback } from 'react'
import { useTaskStore, TaskWithRelations } from '@/store/taskStore'
import { TaskStatus, Priority } from '@/lib/validations/project'
import toast from 'react-hot-toast'

interface FetchTasksOptions {
  search?: string
  status?: TaskStatus
  priority?: Priority
  assignedTo?: string
  myTasks?: boolean
}

export function useTasks() {
  const {
    tasks,
    isLoading,
    error,
    searchQuery,
    filters,
    setTasks,
    updateTask,
    setLoading,
    setError,
    setSearchQuery,
    setFilters,
    clearFilters,
  } = useTaskStore()

  const fetchTasks = useCallback(async (options?: FetchTasksOptions) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL('/api/tasks', window.location.origin)

      if (options?.search) url.searchParams.set('search', options.search)
      if (options?.status) url.searchParams.set('status', options.status)
      if (options?.priority) url.searchParams.set('priority', options.priority)
      if (options?.assignedTo) url.searchParams.set('assignedTo', options.assignedTo)
      if (options?.myTasks) url.searchParams.set('myTasks', 'true')

      const response = await fetch(url.toString())

      if (!response.ok) {
        throw new Error('Error al obtener tareas')
      }

      const data = await response.json()
      setTasks(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }, [setTasks, setLoading, setError])

  const changeTaskStatus = useCallback(async (id: string, status: TaskStatus) => {
    try {
      const response = await fetch(`/api/tasks/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al actualizar tarea')
      }

      const updatedTask = await response.json()
      updateTask(id, updatedTask)
      toast.success('Tarea actualizada')
      return updatedTask
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      toast.error(message)
      return null
    }
  }, [updateTask])

  return {
    tasks,
    isLoading,
    error,
    searchQuery,
    filters,
    setSearchQuery,
    setFilters,
    clearFilters,
    fetchTasks,
    changeTaskStatus,
  }
}
