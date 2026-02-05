'use client'

import { ItemGroupItem } from '@/lib/validations/itemGroup'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Trash2, Package } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface GroupItemsListProps {
  items: ItemGroupItem[]
  onRemoveItem: (itemId: string) => void
  isLoading?: boolean
}

const statusConfig = {
  IN: { label: 'En Bodega', className: 'bg-green-500/10 text-green-400' },
  OUT: { label: 'Afuera', className: 'bg-blue-500/10 text-blue-400' },
  MAINTENANCE: { label: 'Mantenimiento', className: 'bg-amber-500/10 text-amber-400' },
  LOST: { label: 'Perdido', className: 'bg-red-500/10 text-red-400' },
}

export function GroupItemsList({ items, onRemoveItem, isLoading }: GroupItemsListProps) {
  if (items.length === 0) {
    return (
      <Card>
        <Card.Content>
          <div className="text-center py-8">
            <Package className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No hay items en este grupo</p>
            <p className="text-sm text-gray-500 mt-1">
              Agrega items usando el selector de abajo
            </p>
          </div>
        </Card.Content>
      </Card>
    )
  }

  // Calculate total rental price
  const totalRentalPrice = items.reduce((acc, item) => {
    const price = item.inventoryItem?.product?.rentalPrice || 0
    return acc + (Number(price) * item.quantity)
  }, 0)

  // Group items by category for summary
  const categorySummary = items.reduce((acc, item) => {
    const categoryName = item.inventoryItem?.product?.category?.name || 'Sin categoria'
    if (!acc[categoryName]) {
      acc[categoryName] = 0
    }
    acc[categoryName] += item.quantity
    return acc
  }, {} as Record<string, number>)

  return (
    <Card>
      <Card.Header>
        <div className="flex items-center justify-between">
          <div>
            <Card.Title>Items del Grupo ({items.length})</Card.Title>
            <Card.Description>
              {Object.entries(categorySummary).map(([cat, count], idx) => (
                <span key={cat}>
                  {idx > 0 && ' • '}
                  {count} {cat}
                </span>
              ))}
            </Card.Description>
          </div>
          {totalRentalPrice > 0 && (
            <div className="text-right">
              <p className="text-xs text-gray-400">Precio de Alquiler Total</p>
              <p className="text-lg font-semibold text-violet-400">
                ${totalRentalPrice.toLocaleString('es-CO')}
              </p>
            </div>
          )}
        </div>
      </Card.Header>

      <Card.Content>
        <div className="space-y-2">
          {items.map((groupItem) => {
            const item = groupItem.inventoryItem
            const status = item?.status || 'IN'

            return (
              <div
                key={groupItem.id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-200 truncate">
                        {item?.product?.name || 'Sin nombre'}
                      </span>
                      {item?.product?.category && (
                        <span
                          className="px-2 py-0.5 rounded-full text-xs"
                          style={{
                            backgroundColor: item.product.category.color
                              ? `${item.product.category.color}20`
                              : undefined,
                            color: item.product.category.color || undefined,
                          }}
                        >
                          {item.product.category.name}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
                      <span className="font-mono">
                        {item?.assetTag || item?.serialNumber || item?.id?.slice(-8)}
                      </span>
                      {item?.product?.brand && (
                        <>
                          <span>•</span>
                          <span>{item.product.brand} {item.product.model}</span>
                        </>
                      )}
                      {item?.product?.rentalPrice && (
                        <>
                          <span>•</span>
                          <span className="text-violet-400">
                            ${Number(item.product.rentalPrice).toLocaleString('es-CO')}/dia
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                    statusConfig[status].className
                  )}>
                    {statusConfig[status].label}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                  onClick={() => {
                    if (item?.id && confirm('¿Quitar este item del grupo?')) {
                      onRemoveItem(item.id)
                    }
                  }}
                  disabled={isLoading}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            )
          })}
        </div>
      </Card.Content>
    </Card>
  )
}
