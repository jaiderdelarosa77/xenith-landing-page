import { z } from 'zod'

export const conceptSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  description: z.string().optional(),
  supplierId: z.string().optional().nullable(),
  unitPrice: z.number().min(0, 'El precio debe ser positivo').optional().nullable(),
  category: z.string().optional(),
  notes: z.string().optional(),
  isActive: z.boolean(),
})

export type ConceptFormData = z.infer<typeof conceptSchema>

export type Concept = {
  id: string
  name: string
  description: string | null
  supplierId: string | null
  unitPrice: number | null
  category: string | null
  notes: string | null
  isActive: boolean
  createdAt: Date
  updatedAt: Date
  supplier?: {
    id: string
    name: string
    contactName: string | null
    email: string | null
    phone: string | null
  } | null
}

// Categorías predefinidas para conceptos
export const conceptCategories = [
  { value: 'audio', label: 'Audio' },
  { value: 'iluminacion', label: 'Iluminación' },
  { value: 'video', label: 'Video' },
  { value: 'escenografia', label: 'Escenografía' },
  { value: 'catering', label: 'Catering' },
  { value: 'personal', label: 'Personal (Meseros, etc.)' },
  { value: 'transporte', label: 'Transporte' },
  { value: 'show', label: 'Show / Entretenimiento' },
  { value: 'fotografia', label: 'Fotografía' },
  { value: 'decoracion', label: 'Decoración' },
  { value: 'mobiliario', label: 'Mobiliario' },
  { value: 'otro', label: 'Otro' },
]
