import { z } from 'zod'

export const contactSchema = z.object({
  name: z
    .string()
    .min(2, 'El nombre debe tener al menos 2 caracteres')
    .max(100, 'El nombre no puede exceder 100 caracteres'),

  email: z
    .string()
    .email('Email inválido')
    .min(5, 'El email es muy corto')
    .max(100, 'El email no puede exceder 100 caracteres'),

  phone: z
    .string()
    .optional()
    .refine(
      (val) => !val || /^[\d\s\-\+\(\)]+$/.test(val),
      'Número de teléfono inválido'
    ),

  company: z
    .string()
    .max(100, 'El nombre de la empresa no puede exceder 100 caracteres')
    .optional(),

  subject: z
    .string()
    .min(5, 'El asunto debe tener al menos 5 caracteres')
    .max(200, 'El asunto no puede exceder 200 caracteres'),

  message: z
    .string()
    .min(10, 'El mensaje debe tener al menos 10 caracteres')
    .max(2000, 'El mensaje no puede exceder 2000 caracteres'),
})

export type ContactFormData = z.infer<typeof contactSchema>
