'use client'

import { useEffect, useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  quotationSchema,
  QuotationFormData,
  Quotation,
  statusLabels,
  QuotationStatus,
} from '@/lib/validations/quotation'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Plus, Trash2 } from 'lucide-react'
import { format, addDays } from 'date-fns'

interface QuotationFormProps {
  quotation?: Quotation | null
  onSubmit: (data: QuotationFormData) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
  }).format(amount)
}

export function QuotationForm({
  quotation,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: QuotationFormProps) {
  const [clients, setClients] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [loadingData, setLoadingData] = useState(true)

  const defaultValidUntil = format(addDays(new Date(), 30), 'yyyy-MM-dd')

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<QuotationFormData>({
    resolver: zodResolver(quotationSchema),
    defaultValues: quotation
      ? {
          title: quotation.title,
          description: quotation.description || '',
          clientId: quotation.clientId,
          projectId: quotation.projectId || '',
          status: quotation.status,
          validUntil: format(new Date(quotation.validUntil), 'yyyy-MM-dd'),
          discount: quotation.discount?.toString() || '0',
          tax: '16',
          notes: quotation.notes || '',
          terms: quotation.terms || '',
          items: quotation.items.map((item) => ({
            description: item.description,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
          })),
        }
      : {
          status: 'DRAFT' as QuotationStatus,
          validUntil: defaultValidUntil,
          discount: '0',
          tax: '16',
          items: [{ description: '', quantity: 1, unitPrice: 0 }],
        },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  })

  const watchedItems = watch('items')
  const watchedDiscount = watch('discount')
  const watchedTax = watch('tax')

  // Calculate totals
  const subtotal = watchedItems?.reduce((acc, item) => {
    const qty = Number(item.quantity) || 0
    const price = Number(item.unitPrice) || 0
    return acc + qty * price
  }, 0) || 0

  const discount = Number(watchedDiscount) || 0
  const taxRate = Number(watchedTax) || 16
  const subtotalAfterDiscount = subtotal - discount
  const taxAmount = subtotalAfterDiscount * (taxRate / 100)
  const total = subtotalAfterDiscount + taxAmount

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientsRes, projectsRes] = await Promise.all([
          fetch('/api/clients'),
          fetch('/api/projects'),
        ])

        if (clientsRes.ok) {
          const clientsData = await clientsRes.json()
          setClients(clientsData)
        }

        if (projectsRes.ok) {
          const projectsData = await projectsRes.json()
          setProjects(projectsData)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoadingData(false)
      }
    }

    fetchData()
  }, [])

  if (loadingData) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="inline-block w-8 h-8 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const statusOptions = Object.entries(statusLabels).map(([value, label]) => ({
    value,
    label,
  }))

  const clientOptions = [
    { value: '', label: 'Selecciona un cliente' },
    ...clients.map((client) => ({
      value: client.id,
      label: `${client.name}${client.company ? ` - ${client.company}` : ''}`,
    })),
  ]

  const projectOptions = [
    { value: '', label: 'Sin proyecto asociado' },
    ...projects.map((project) => ({
      value: project.id,
      label: project.title,
    })),
  ]

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Basic Information */}
      <Card>
        <Card.Header>
          <h3 className="text-lg font-semibold">Informacion General</h3>
        </Card.Header>
        <Card.Content>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <Input
                label="Titulo de la Cotizacion *"
                placeholder="Desarrollo de sitio web corporativo"
                error={errors.title?.message}
                {...register('title')}
              />
            </div>

            <div className="md:col-span-2">
              <Textarea
                label="Descripcion"
                placeholder="Describe el alcance de la cotizacion..."
                rows={3}
                error={errors.description?.message}
                {...register('description')}
              />
            </div>

            <Select
              label="Cliente *"
              options={clientOptions}
              error={errors.clientId?.message}
              {...register('clientId')}
            />

            <Select
              label="Proyecto Asociado"
              options={projectOptions}
              error={errors.projectId?.message}
              {...register('projectId')}
            />

            <Select
              label="Estado *"
              options={statusOptions}
              error={errors.status?.message}
              {...register('status')}
            />

            <Input
              label="Valida hasta *"
              type="date"
              error={errors.validUntil?.message}
              {...register('validUntil')}
            />
          </div>
        </Card.Content>
      </Card>

      {/* Items */}
      <Card>
        <Card.Header>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Conceptos</h3>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ description: '', quantity: 1, unitPrice: 0 })}
            >
              <Plus className="w-4 h-4 mr-2" />
              Agregar Concepto
            </Button>
          </div>
        </Card.Header>
        <Card.Content>
          <div className="space-y-4">
            {fields.map((field, index) => {
              const itemQty = Number(watchedItems?.[index]?.quantity) || 0
              const itemPrice = Number(watchedItems?.[index]?.unitPrice) || 0
              const itemTotal = itemQty * itemPrice

              return (
                <div
                  key={field.id}
                  className="grid grid-cols-12 gap-4 p-4 bg-gray-900/30 rounded-lg border border-gray-800"
                >
                  <div className="col-span-12 md:col-span-5">
                    <Input
                      label="Descripcion *"
                      placeholder="Diseño de interfaz de usuario"
                      error={errors.items?.[index]?.description?.message}
                      {...register(`items.${index}.description`)}
                    />
                  </div>
                  <div className="col-span-4 md:col-span-2">
                    <Input
                      label="Cantidad *"
                      type="number"
                      min="1"
                      step="1"
                      error={errors.items?.[index]?.quantity?.message}
                      {...register(`items.${index}.quantity`, {
                        valueAsNumber: true,
                      })}
                    />
                  </div>
                  <div className="col-span-4 md:col-span-2">
                    <Input
                      label="Precio Unit. *"
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="0.00"
                      error={errors.items?.[index]?.unitPrice?.message}
                      {...register(`items.${index}.unitPrice`, {
                        valueAsNumber: true,
                      })}
                    />
                  </div>
                  <div className="col-span-3 md:col-span-2">
                    <label className="block text-sm font-medium text-gray-300 mb-1.5">
                      Total
                    </label>
                    <div className="px-4 py-2.5 bg-gray-800/50 border border-gray-700 rounded-lg text-green-400 font-medium">
                      {formatCurrency(itemTotal)}
                    </div>
                  </div>
                  <div className="col-span-1 flex items-end justify-center pb-1">
                    {fields.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        onClick={() => remove(index)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}

            {errors.items?.message && (
              <p className="text-sm text-red-400">{errors.items.message}</p>
            )}
          </div>
        </Card.Content>
      </Card>

      {/* Totals and Additional Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Additional Info */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-semibold">Informacion Adicional</h3>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <Textarea
                label="Notas"
                placeholder="Notas adicionales para el cliente..."
                rows={3}
                error={errors.notes?.message}
                {...register('notes')}
              />

              <Textarea
                label="Terminos y Condiciones"
                placeholder="Terminos de pago, garantias, etc..."
                rows={3}
                error={errors.terms?.message}
                {...register('terms')}
              />
            </div>
          </Card.Content>
        </Card>

        {/* Totals */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-semibold">Resumen</h3>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-gray-800">
                <span className="text-gray-400">Subtotal</span>
                <span className="font-medium">{formatCurrency(subtotal)}</span>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    label="Descuento"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    error={errors.discount?.message}
                    {...register('discount')}
                  />
                </div>
                <div className="pt-6 text-gray-400">
                  -{formatCurrency(discount)}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Input
                    label="IVA (%)"
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    error={errors.tax?.message}
                    {...register('tax')}
                  />
                </div>
                <div className="pt-6 text-gray-400">
                  +{formatCurrency(taxAmount)}
                </div>
              </div>

              <div className="flex justify-between items-center py-3 border-t-2 border-violet-500/50">
                <span className="text-lg font-semibold">Total</span>
                <span className="text-2xl font-bold text-green-400">
                  {formatCurrency(total)}
                </span>
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting}>
          {quotation ? 'Actualizar Cotizacion' : 'Crear Cotizacion'}
        </Button>
      </div>
    </form>
  )
}
