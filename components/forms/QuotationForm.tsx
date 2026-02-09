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
import { InventoryItem } from '@/lib/validations/inventory'
import { ItemGroup } from '@/lib/validations/itemGroup'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Plus, Trash2, Search, Package, Package2, X, ChevronDown, ChevronUp } from 'lucide-react'
import { format, addDays } from 'date-fns'

interface QuotationFormProps {
  quotation?: Quotation | null
  onSubmit: (data: QuotationFormData) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
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
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([])
  const [itemGroups, setItemGroups] = useState<ItemGroup[]>([])
  const [loadingData, setLoadingData] = useState(true)
  const [showItemSearch, setShowItemSearch] = useState(false)
  const [showGroupSearch, setShowGroupSearch] = useState(false)
  const [itemSearch, setItemSearch] = useState('')
  const [groupSearch, setGroupSearch] = useState('')
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set())

  const defaultValidUntil = format(addDays(new Date(), 30), 'yyyy-MM-dd')

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
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
          tax: '19',
          notes: quotation.notes || '',
          terms: quotation.terms || '',
          items: quotation.items.map((item) => ({
            inventoryItemId: item.inventoryItemId || null,
            description: item.description,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
          })),
          groups: quotation.groups?.map((g) => ({
            groupId: g.groupId,
            name: g.name,
            description: g.description || '',
            unitPrice: Number(g.unitPrice),
            quantity: g.quantity,
          })) || [],
        }
      : {
          status: 'DRAFT' as QuotationStatus,
          validUntil: defaultValidUntil,
          discount: '0',
          tax: '19',
          items: [],
          groups: [],
        },
  })

  const { fields: itemFields, append: appendItem, remove: removeItem } = useFieldArray({
    control,
    name: 'items',
  })

  const { fields: groupFields, append: appendGroup, remove: removeGroup } = useFieldArray({
    control,
    name: 'groups',
  })

  const watchedItems = watch('items')
  const watchedGroups = watch('groups')
  const watchedDiscount = watch('discount')
  const watchedTax = watch('tax')

  // Calculate totals
  const itemsSubtotal = watchedItems?.reduce((acc, item) => {
    const qty = Number(item.quantity) || 0
    const price = Number(item.unitPrice) || 0
    return acc + qty * price
  }, 0) || 0

  const groupsSubtotal = watchedGroups?.reduce((acc, group) => {
    const qty = Number(group.quantity) || 0
    const price = Number(group.unitPrice) || 0
    return acc + qty * price
  }, 0) || 0

  const subtotal = itemsSubtotal + groupsSubtotal
  const discount = Number(watchedDiscount) || 0
  const taxRate = Number(watchedTax) || 19
  const subtotalAfterDiscount = subtotal - discount
  const taxAmount = subtotalAfterDiscount * (taxRate / 100)
  const total = subtotalAfterDiscount + taxAmount

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientsRes, projectsRes, inventoryRes, groupsRes] = await Promise.all([
          fetch('/api/clients'),
          fetch('/api/projects'),
          fetch('/api/inventory?status=IN'),
          fetch('/api/item-groups'),
        ])

        if (clientsRes.ok) {
          const clientsData = await clientsRes.json()
          setClients(clientsData)
        }

        if (projectsRes.ok) {
          const projectsData = await projectsRes.json()
          setProjects(projectsData)
        }

        if (inventoryRes.ok) {
          const inventoryData = await inventoryRes.json()
          setInventoryItems(inventoryData)
        }

        if (groupsRes.ok) {
          const groupsData = await groupsRes.json()
          setItemGroups(groupsData)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoadingData(false)
      }
    }

    fetchData()
  }, [])

  const handleAddInventoryItem = (item: InventoryItem) => {
    const rentalPrice = item.product?.rentalPrice
      ? Number(item.product.rentalPrice)
      : item.product?.unitPrice
        ? Number(item.product.unitPrice)
        : 0

    const description = [
      item.product?.name,
      item.product?.brand && item.product?.model
        ? `(${item.product.brand} ${item.product.model})`
        : item.product?.brand || item.product?.model,
      item.serialNumber ? `S/N: ${item.serialNumber}` : null,
      item.assetTag ? `Tag: ${item.assetTag}` : null,
    ].filter(Boolean).join(' ')

    appendItem({
      inventoryItemId: item.id,
      description,
      quantity: 1,
      unitPrice: rentalPrice,
    })

    setShowItemSearch(false)
    setItemSearch('')
  }

  const handleAddGroup = (group: ItemGroup) => {
    // Calculate default price based on items' rental prices
    const defaultPrice = group.items?.reduce((acc, item) => {
      const price = item.inventoryItem?.product?.rentalPrice
        ? Number(item.inventoryItem.product.rentalPrice)
        : 0
      return acc + price * (item.quantity || 1)
    }, 0) || 0

    appendGroup({
      groupId: group.id,
      name: group.name,
      description: group.description || '',
      unitPrice: defaultPrice,
      quantity: 1,
    })

    setShowGroupSearch(false)
    setGroupSearch('')
  }

  const toggleGroupExpanded = (index: number) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedGroups(newExpanded)
  }

  const filteredInventoryItems = inventoryItems.filter(item => {
    if (!itemSearch) return true
    const searchLower = itemSearch.toLowerCase()
    return (
      item.product?.name?.toLowerCase().includes(searchLower) ||
      item.product?.sku?.toLowerCase().includes(searchLower) ||
      item.serialNumber?.toLowerCase().includes(searchLower) ||
      item.assetTag?.toLowerCase().includes(searchLower) ||
      item.product?.brand?.toLowerCase().includes(searchLower)
    )
  })

  const filteredGroups = itemGroups.filter(group => {
    if (!groupSearch) return true
    const searchLower = groupSearch.toLowerCase()
    return (
      group.name?.toLowerCase().includes(searchLower) ||
      group.description?.toLowerCase().includes(searchLower)
    )
  })

  // Get already added inventory item IDs
  const addedItemIds = watchedItems
    ?.filter(item => item.inventoryItemId)
    .map(item => item.inventoryItemId) || []

  // Get already added group IDs
  const addedGroupIds = watchedGroups?.map(g => g.groupId) || []

  // Filter out already added items and groups
  const availableItems = filteredInventoryItems.filter(
    item => !addedItemIds.includes(item.id)
  )
  const availableGroups = filteredGroups.filter(
    group => !addedGroupIds.includes(group.id)
  )

  // Get group details for displaying items
  const getGroupDetails = (groupId: string) => {
    return itemGroups.find(g => g.id === groupId)
  }

  if (loadingData) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="inline-block w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin" />
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
    <>
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
                  placeholder="Alquiler de equipos para evento corporativo"
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

        {/* Groups Section */}
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Package2 className="w-5 h-5 text-cyan-400" />
                  Grupos / Paquetes
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  Agrega paquetes de equipos predefinidos
                </p>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowGroupSearch(true)}
              >
                <Package2 className="w-4 h-4 mr-2" />
                Agregar Grupo
              </Button>
            </div>
          </Card.Header>
          <Card.Content>
            {groupFields.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Package2 className="w-10 h-10 mx-auto mb-3 opacity-50" />
                <p>No hay grupos agregados</p>
                <p className="text-sm mt-1">Haz clic en &quot;Agregar Grupo&quot; para incluir un paquete</p>
              </div>
            ) : (
              <div className="space-y-4">
                {groupFields.map((field, index) => {
                  const groupQty = Number(watchedGroups?.[index]?.quantity) || 0
                  const groupPrice = Number(watchedGroups?.[index]?.unitPrice) || 0
                  const groupTotal = groupQty * groupPrice
                  const groupDetails = getGroupDetails(watchedGroups?.[index]?.groupId || '')
                  const isExpanded = expandedGroups.has(index)

                  return (
                    <div
                      key={field.id}
                      className="rounded-lg border bg-cyan-500/5 border-cyan-500/20"
                    >
                      <div className="p-4">
                        <div className="grid grid-cols-12 gap-4">
                          <div className="col-span-12 md:col-span-5">
                            <div className="flex items-center gap-2 mb-1">
                              <label className="block text-sm font-medium text-gray-300">
                                Nombre del Grupo
                              </label>
                              <span className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-400">
                                Paquete
                              </span>
                            </div>
                            <Input
                              placeholder="Nombre del grupo"
                              {...register(`groups.${index}.name`)}
                            />
                            <input type="hidden" {...register(`groups.${index}.groupId`)} />
                            <input type="hidden" {...register(`groups.${index}.description`)} />
                          </div>
                          <div className="col-span-4 md:col-span-2">
                            <Input
                              label="Cantidad"
                              type="number"
                              min="1"
                              step="1"
                              {...register(`groups.${index}.quantity`, {
                                valueAsNumber: true,
                              })}
                            />
                          </div>
                          <div className="col-span-4 md:col-span-2">
                            <Input
                              label="Precio"
                              type="number"
                              min="0"
                              step="1"
                              placeholder="0"
                              {...register(`groups.${index}.unitPrice`, {
                                valueAsNumber: true,
                              })}
                            />
                          </div>
                          <div className="col-span-3 md:col-span-2">
                            <label className="block text-sm font-medium text-gray-300 mb-1.5">
                              Total
                            </label>
                            <div className="px-4 py-2.5 bg-gray-800/50 border border-gray-700 rounded-lg text-green-400 font-medium">
                              {formatCurrency(groupTotal)}
                            </div>
                          </div>
                          <div className="col-span-1 flex items-end justify-center pb-1 gap-1">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleGroupExpanded(index)}
                              title={isExpanded ? 'Ocultar items' : 'Ver items'}
                            >
                              {isExpanded ? (
                                <ChevronUp className="w-4 h-4" />
                              ) : (
                                <ChevronDown className="w-4 h-4" />
                              )}
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                              onClick={() => removeGroup(index)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>

                      {/* Expanded items list */}
                      {isExpanded && groupDetails?.items && (
                        <div className="px-4 pb-4">
                          <div className="bg-gray-900/50 rounded-lg p-3">
                            <p className="text-xs text-gray-400 mb-2 font-medium">
                              Items incluidos en este paquete:
                            </p>
                            <div className="space-y-1">
                              {groupDetails.items.map((item) => (
                                <div
                                  key={item.id}
                                  className="flex items-center justify-between text-sm py-1"
                                >
                                  <div className="flex items-center gap-2">
                                    <span className="text-gray-300">
                                      {item.inventoryItem?.product?.name || 'Item'}
                                    </span>
                                    {item.inventoryItem?.product?.category && (
                                      <span
                                        className="px-1.5 py-0.5 rounded text-xs"
                                        style={{
                                          backgroundColor: item.inventoryItem.product.category.color
                                            ? `${item.inventoryItem.product.category.color}20`
                                            : undefined,
                                          color: item.inventoryItem.product.category.color || undefined,
                                        }}
                                      >
                                        {item.inventoryItem.product.category.name}
                                      </span>
                                    )}
                                  </div>
                                  <span className="text-gray-500 font-mono text-xs">
                                    {item.inventoryItem?.assetTag || item.inventoryItem?.serialNumber || ''}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </Card.Content>
        </Card>

        {/* Items */}
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <Package className="w-5 h-5 text-orange-400" />
                  Items Individuales
                </h3>
                <p className="text-sm text-gray-400 mt-1">
                  Agrega equipos individuales o conceptos manuales
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowItemSearch(true)}
                >
                  <Package className="w-4 h-4 mr-2" />
                  Del Inventario
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => appendItem({ inventoryItemId: null, description: '', quantity: 1, unitPrice: 0 })}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Manual
                </Button>
              </div>
            </div>
          </Card.Header>
          <Card.Content>
            {itemFields.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Package className="w-10 h-10 mx-auto mb-3 opacity-50" />
                <p>No hay items individuales agregados</p>
              </div>
            ) : (
              <div className="space-y-4">
                {itemFields.map((field, index) => {
                  const itemQty = Number(watchedItems?.[index]?.quantity) || 0
                  const itemPrice = Number(watchedItems?.[index]?.unitPrice) || 0
                  const itemTotal = itemQty * itemPrice
                  const isInventoryItem = !!watchedItems?.[index]?.inventoryItemId

                  return (
                    <div
                      key={field.id}
                      className={`grid grid-cols-12 gap-4 p-4 rounded-lg border ${
                        isInventoryItem
                          ? 'bg-orange-500/5 border-orange-500/20'
                          : 'bg-gray-900/30 border-gray-800'
                      }`}
                    >
                      <div className="col-span-12 md:col-span-5">
                        <div className="flex items-center gap-2 mb-1">
                          <label className="block text-sm font-medium text-gray-300">
                            Descripcion *
                          </label>
                          {isInventoryItem && (
                            <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-400">
                              Inventario
                            </span>
                          )}
                        </div>
                        <Input
                          placeholder="Descripcion del item"
                          error={errors.items?.[index]?.description?.message}
                          {...register(`items.${index}.description`)}
                        />
                        <input type="hidden" {...register(`items.${index}.inventoryItemId`)} />
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
                          step="1"
                          placeholder="0"
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
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                          onClick={() => removeItem(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {errors.items?.message && (
              <p className="text-sm text-red-400 mt-4">{errors.items.message}</p>
            )}
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
                {groupsSubtotal > 0 && (
                  <div className="flex justify-between items-center py-2 text-sm">
                    <span className="text-gray-400">Grupos ({groupFields.length})</span>
                    <span className="text-cyan-400">{formatCurrency(groupsSubtotal)}</span>
                  </div>
                )}
                {itemsSubtotal > 0 && (
                  <div className="flex justify-between items-center py-2 text-sm">
                    <span className="text-gray-400">Items ({itemFields.length})</span>
                    <span className="text-orange-400">{formatCurrency(itemsSubtotal)}</span>
                  </div>
                )}
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
                      step="1"
                      placeholder="0"
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

                <div className="flex justify-between items-center py-3 border-t-2 border-orange-500/50">
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

      {/* Inventory Item Search Modal */}
      {showItemSearch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowItemSearch(false)}
          />
          <div className="relative bg-gray-900 rounded-xl border border-gray-800 w-full max-w-3xl max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-800 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold">Agregar Item del Inventario</h3>
                <p className="text-gray-400 text-sm mt-1">
                  Selecciona los equipos disponibles para agregar a la cotizacion
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowItemSearch(false)}
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="p-4 border-b border-gray-800">
              <Input
                placeholder="Buscar por nombre, SKU, serial, marca..."
                value={itemSearch}
                onChange={(e) => setItemSearch(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>

            <div className="p-4 overflow-y-auto max-h-[50vh]">
              {availableItems.length > 0 ? (
                <div className="space-y-2">
                  {availableItems.slice(0, 30).map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors cursor-pointer"
                      onClick={() => handleAddInventoryItem(item)}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{item.product?.name}</p>
                          {item.product?.brand && (
                            <span className="text-xs text-gray-500">
                              {item.product.brand} {item.product.model}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
                          <span className="font-mono">{item.product?.sku}</span>
                          {item.serialNumber && (
                            <span>S/N: {item.serialNumber}</span>
                          )}
                          {item.assetTag && (
                            <span>Tag: {item.assetTag}</span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-green-400">
                          {item.product?.rentalPrice
                            ? formatCurrency(Number(item.product.rentalPrice))
                            : item.product?.unitPrice
                              ? formatCurrency(Number(item.product.unitPrice))
                              : '-'
                          }
                        </p>
                        <p className="text-xs text-gray-500">por dia</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Package className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No hay items disponibles</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {itemSearch
                      ? 'No se encontraron items con ese criterio de busqueda'
                      : 'Todos los items disponibles ya fueron agregados'
                    }
                  </p>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-gray-800 flex justify-end">
              <Button variant="outline" onClick={() => setShowItemSearch(false)}>
                Cerrar
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Group Search Modal */}
      {showGroupSearch && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowGroupSearch(false)}
          />
          <div className="relative bg-gray-900 rounded-xl border border-gray-800 w-full max-w-3xl max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-800 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <Package2 className="w-6 h-6 text-cyan-400" />
                  Agregar Grupo de Equipos
                </h3>
                <p className="text-gray-400 text-sm mt-1">
                  Selecciona un paquete predefinido para agregar a la cotizacion
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowGroupSearch(false)}
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="p-4 border-b border-gray-800">
              <Input
                placeholder="Buscar grupo por nombre..."
                value={groupSearch}
                onChange={(e) => setGroupSearch(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>

            <div className="p-4 overflow-y-auto max-h-[50vh]">
              {availableGroups.length > 0 ? (
                <div className="space-y-2">
                  {availableGroups.map((group) => {
                    const groupPrice = group.items?.reduce((acc, item) => {
                      const price = item.inventoryItem?.product?.rentalPrice
                        ? Number(item.inventoryItem.product.rentalPrice)
                        : 0
                      return acc + price * (item.quantity || 1)
                    }, 0) || 0

                    return (
                      <div
                        key={group.id}
                        className="p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors cursor-pointer border border-transparent hover:border-cyan-500/30"
                        onClick={() => handleAddGroup(group)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-lg">{group.name}</p>
                              <span className="px-2 py-0.5 rounded-full text-xs bg-cyan-500/20 text-cyan-400">
                                {group._count?.items || group.items?.length || 0} items
                              </span>
                            </div>
                            {group.description && (
                              <p className="text-gray-400 text-sm mt-1">{group.description}</p>
                            )}
                            {group.items && group.items.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {group.items.slice(0, 5).map((item) => (
                                  <span
                                    key={item.id}
                                    className="px-2 py-0.5 rounded bg-gray-700 text-xs text-gray-300"
                                  >
                                    {item.inventoryItem?.product?.name || 'Item'}
                                  </span>
                                ))}
                                {group.items.length > 5 && (
                                  <span className="px-2 py-0.5 rounded bg-gray-700 text-xs text-gray-400">
                                    +{group.items.length - 5} mas
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                          <div className="text-right ml-4">
                            <p className="font-semibold text-green-400 text-lg">
                              {formatCurrency(groupPrice)}
                            </p>
                            <p className="text-xs text-gray-500">precio sugerido</p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Package2 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No hay grupos disponibles</p>
                  <p className="text-sm text-gray-500 mt-1">
                    {groupSearch
                      ? 'No se encontraron grupos con ese criterio de busqueda'
                      : 'Todos los grupos ya fueron agregados o no hay grupos creados'
                    }
                  </p>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-gray-800 flex justify-end">
              <Button variant="outline" onClick={() => setShowGroupSearch(false)}>
                Cerrar
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
