'use client'

import { useCallback } from 'react'
import { useQuotationStore } from '@/store/quotationStore'
import { QuotationFormData, Quotation, QuotationStatus } from '@/lib/validations/quotation'
import toast from 'react-hot-toast'

interface FetchQuotationsOptions {
  search?: string
  status?: QuotationStatus
  clientId?: string
  projectId?: string
}

export function useQuotations() {
  const {
    quotations,
    currentQuotation,
    isLoading,
    error,
    searchQuery,
    filters,
    setQuotations,
    setCurrentQuotation,
    addQuotation,
    updateQuotation,
    removeQuotation,
    setLoading,
    setError,
    setSearchQuery,
    setFilters,
    clearFilters,
  } = useQuotationStore()

  const fetchQuotations = useCallback(async (options?: FetchQuotationsOptions) => {
    setLoading(true)
    setError(null)

    try {
      const url = new URL('/api/quotations', window.location.origin)

      if (options?.search) url.searchParams.set('search', options.search)
      if (options?.status) url.searchParams.set('status', options.status)
      if (options?.clientId) url.searchParams.set('clientId', options.clientId)
      if (options?.projectId) url.searchParams.set('projectId', options.projectId)

      const response = await fetch(url.toString())

      if (!response.ok) {
        throw new Error('Error al obtener cotizaciones')
      }

      const data = await response.json()
      setQuotations(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }, [setQuotations, setLoading, setError])

  const fetchQuotation = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/quotations/${id}`)

      if (!response.ok) {
        throw new Error('Error al obtener cotización')
      }

      const data = await response.json()
      setCurrentQuotation(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [setCurrentQuotation, setLoading, setError])

  const createQuotation = useCallback(async (data: QuotationFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/quotations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al crear cotización')
      }

      const newQuotation = await response.json()
      addQuotation(newQuotation)
      toast.success('Cotización creada exitosamente')
      return newQuotation
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [addQuotation, setLoading, setError])

  const editQuotation = useCallback(async (id: string, data: QuotationFormData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/quotations/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al actualizar cotización')
      }

      const updatedQuotation = await response.json()
      updateQuotation(id, updatedQuotation)
      toast.success('Cotización actualizada exitosamente')
      return updatedQuotation
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [updateQuotation, setLoading, setError])

  const deleteQuotation = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/quotations/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Error al eliminar cotización')
      }

      removeQuotation(id)
      toast.success('Cotización eliminada exitosamente')
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido'
      setError(message)
      toast.error(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [removeQuotation, setLoading, setError])

  const downloadPDF = useCallback(async (id: string, quotationNumber: string) => {
    try {
      toast.loading('Generando PDF...')
      const response = await fetch(`/api/quotations/${id}/pdf`)

      if (!response.ok) {
        throw new Error('Error al generar PDF')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Cotizacion-${quotationNumber}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.dismiss()
      toast.success('PDF descargado exitosamente')
    } catch (err) {
      toast.dismiss()
      const message = err instanceof Error ? err.message : 'Error desconocido'
      toast.error(message)
    }
  }, [])

  return {
    quotations,
    currentQuotation,
    isLoading,
    error,
    searchQuery,
    filters,
    setSearchQuery,
    setFilters,
    clearFilters,
    fetchQuotations,
    fetchQuotation,
    createQuotation,
    editQuotation,
    deleteQuotation,
    downloadPDF,
  }
}
