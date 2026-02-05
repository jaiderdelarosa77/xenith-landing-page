'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import { Search, Plus, Filter, X, Package } from 'lucide-react'
import { InventoryItem } from '@/lib/validations/inventory'
import { cn } from '@/lib/utils/cn'

interface Category {
  id: string
  name: string
  color: string | null
}

interface ItemSelectorProps {
  onAddItem: (itemId: string) => void
  excludeItemIds?: string[]
  isLoading?: boolean
}

const statusConfig = {
  IN: { label: 'En Bodega', className: 'bg-green-500/10 text-green-400' },
  OUT: { label: 'Afuera', className: 'bg-blue-500/10 text-blue-400' },
  MAINTENANCE: { label: 'Mantenimiento', className: 'bg-amber-500/10 text-amber-400' },
  LOST: { label: 'Perdido', className: 'bg-red-500/10 text-red-400' },
}

export function ItemSelector({ onAddItem, excludeItemIds = [], isLoading }: ItemSelectorProps) {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [loadingItems, setLoadingItems] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  const fetchCategories = useCallback(async () => {
    try {
      const response = await fetch('/api/categories')
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
      }
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }, [])

  const fetchItems = useCallback(async () => {
    setLoadingItems(true)
    try {
      const url = new URL('/api/inventory', window.location.origin)
      if (search) url.searchParams.set('search', search)

      const response = await fetch(url.toString())
      if (response.ok) {
        const data = await response.json()
        setItems(data)
      }
    } catch (error) {
      console.error('Error fetching items:', error)
    } finally {
      setLoadingItems(false)
    }
  }, [search])

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  useEffect(() => {
    const debounce = setTimeout(() => {
      fetchItems()
    }, 300)

    return () => clearTimeout(debounce)
  }, [fetchItems])

  // Filter items by category and exclude already added items
  const filteredItems = items.filter((item) => {
    if (excludeItemIds.includes(item.id)) return false
    if (selectedCategory && item.product?.category?.id !== selectedCategory) return false
    return true
  })

  return (
    <Card>
      <Card.Header>
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <Card.Title>Agregar Items al Grupo</Card.Title>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filtros
            </Button>
          </div>

          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Buscar por nombre, SKU, serie..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
              />
            </div>
          </div>

          {showFilters && (
            <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-800">
              <button
                onClick={() => setSelectedCategory('')}
                className={cn(
                  'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
                  !selectedCategory
                    ? 'bg-violet-500 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                )}
              >
                Todas
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={cn(
                    'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
                    selectedCategory === cat.id
                      ? 'bg-violet-500 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  )}
                  style={selectedCategory === cat.id && cat.color ? {
                    backgroundColor: cat.color,
                  } : undefined}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          )}
        </div>
      </Card.Header>

      <Card.Content>
        {loadingItems ? (
          <div className="text-center py-8">
            <div className="inline-block w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 mt-2 text-sm">Cargando items...</p>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-8">
            <Package className="w-10 h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">
              {items.length === 0
                ? 'No hay items disponibles'
                : 'No se encontraron items con los filtros seleccionados'}
            </p>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto space-y-2">
            {filteredItems.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-200 truncate">
                        {item.product?.name || 'Sin nombre'}
                      </span>
                      {item.product?.category && (
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
                        {item.assetTag || item.serialNumber || item.id.slice(-8)}
                      </span>
                      {item.product?.brand && (
                        <>
                          <span>•</span>
                          <span>{item.product.brand} {item.product.model}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap',
                    statusConfig[item.status].className
                  )}>
                    {statusConfig[item.status].label}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 text-violet-400 hover:text-violet-300 hover:bg-violet-500/10"
                  onClick={() => onAddItem(item.id)}
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card.Content>
    </Card>
  )
}
