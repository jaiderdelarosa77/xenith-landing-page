import { z } from 'zod'

export const itemGroupSchema = z.object({
  name: z.string().min(3, 'El nombre debe tener al menos 3 caracteres'),
  description: z.string().optional(),
})

export type ItemGroupFormData = z.infer<typeof itemGroupSchema>

export const addItemToGroupSchema = z.object({
  inventoryItemId: z.string().min(1, 'El item es requerido'),
  quantity: z.number().int().min(1, 'La cantidad debe ser al menos 1').default(1),
  notes: z.string().optional(),
})

export type AddItemToGroupFormData = z.infer<typeof addItemToGroupSchema>

export type ItemGroupItem = {
  id: string
  groupId: string
  inventoryItemId: string
  quantity: number
  notes: string | null
  createdAt: Date
  inventoryItem?: {
    id: string
    serialNumber: string | null
    assetTag: string | null
    status: 'IN' | 'OUT' | 'MAINTENANCE' | 'LOST'
    location: string | null
    product?: {
      id: string
      sku: string
      name: string
      brand: string | null
      model: string | null
      rentalPrice: number | null
      category?: {
        id: string
        name: string
        color: string | null
      }
    }
  }
}

export type ItemGroup = {
  id: string
  name: string
  description: string | null
  createdAt: Date
  updatedAt: Date
  items?: ItemGroupItem[]
  _count?: {
    items: number
  }
}
