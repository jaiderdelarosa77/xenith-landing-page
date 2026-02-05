'use client'

import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { conceptSchema, ConceptFormData, Concept, conceptCategories } from '@/lib/validations/concept'
import { Supplier } from '@/lib/validations/supplier'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Card } from '@/components/ui/Card'

interface ConceptFormProps {
  initialData?: Concept
  onSubmit: (data: ConceptFormData) => Promise<void>
  isLoading?: boolean
}

export function ConceptForm({ initialData, onSubmit, isLoading }: ConceptFormProps) {
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [loadingSuppliers, setLoadingSuppliers] = useState(true)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ConceptFormData>({
    resolver: zodResolver(conceptSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      supplierId: initialData?.supplierId || '',
      unitPrice: initialData?.unitPrice ? Number(initialData.unitPrice) : undefined,
      category: initialData?.category || '',
      notes: initialData?.notes || '',
      isActive: initialData?.isActive ?? true,
    },
  })

  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        const response = await fetch('/api/suppliers')
        if (response.ok) {
          const data = await response.json()
          setSuppliers(data)
        }
      } catch (error) {
        console.error('Error fetching suppliers:', error)
      } finally {
        setLoadingSuppliers(false)
      }
    }

    fetchSuppliers()
  }, [])

  const supplierOptions = [
    { value: '', label: 'Sin contratista asignado' },
    ...suppliers.map((s) => ({
      value: s.id,
      label: s.name + (s.contactName ? ` (${s.contactName})` : ''),
    })),
  ]

  const categoryOptions = [
    { value: '', label: 'Selecciona una categoria' },
    ...conceptCategories,
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card>
        <Card.Header>
          <Card.Title>Informacion del Concepto</Card.Title>
          <Card.Description>
            Define el servicio o concepto que ofrece el contratista
          </Card.Description>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <Input
                label="Nombre del Concepto *"
                placeholder="Ej: Show de luces LED, Servicio de catering, DJ"
                error={errors.name?.message}
                {...register('name')}
              />
            </div>

            <div className="md:col-span-2">
              <Textarea
                label="Descripcion"
                placeholder="Describe el servicio o concepto..."
                rows={3}
                error={errors.description?.message}
                {...register('description')}
              />
            </div>

            <Select
              label="Categoria"
              options={categoryOptions}
              error={errors.category?.message}
              {...register('category')}
            />

            <Input
              label="Precio de Referencia"
              type="number"
              min="0"
              step="1"
              placeholder="0"
              error={errors.unitPrice?.message}
              {...register('unitPrice', { valueAsNumber: true })}
            />
          </div>
        </Card.Content>
      </Card>

      <Card>
        <Card.Header>
          <Card.Title>Contratista Asociado</Card.Title>
          <Card.Description>
            Opcionalmente, asocia este concepto a un contratista especifico
          </Card.Description>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 gap-6">
            {loadingSuppliers ? (
              <div className="text-center py-4">
                <div className="inline-block w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-gray-400 mt-2 text-sm">Cargando contratistas...</p>
              </div>
            ) : (
              <Select
                label="Contratista"
                options={supplierOptions}
                error={errors.supplierId?.message}
                {...register('supplierId')}
              />
            )}

            <Textarea
              label="Notas Adicionales"
              placeholder="Notas sobre el servicio, requerimientos especiales, etc..."
              rows={3}
              error={errors.notes?.message}
              {...register('notes')}
            />

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="isActive"
                className="w-4 h-4 rounded border-gray-700 bg-gray-800 text-violet-500 focus:ring-violet-500"
                {...register('isActive')}
              />
              <label htmlFor="isActive" className="text-sm text-gray-300">
                Concepto activo (disponible para usar en cotizaciones)
              </label>
            </div>
          </div>
        </Card.Content>
      </Card>

      <div className="flex justify-end gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => window.history.back()}
        >
          Cancelar
        </Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>
          {initialData ? 'Guardar Cambios' : 'Crear Concepto'}
        </Button>
      </div>
    </form>
  )
}
