import { z } from 'zod'

export const clientSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  company: z.string().optional(),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  country: z.string().optional(),
  nit: z.string().optional(),
  notes: z.string().optional(),
  rutUrl: z.string().optional(),
})

export type ClientFormData = z.infer<typeof clientSchema>

export type Client = {
  id: string
  name: string
  company: string | null
  email: string
  phone: string | null
  address: string | null
  city: string | null
  country: string | null
  nit: string | null
  notes: string | null
  rutUrl: string | null
  createdAt: Date
  updatedAt: Date
}
