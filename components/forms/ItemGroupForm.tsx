'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { itemGroupSchema, ItemGroupFormData, ItemGroup } from '@/lib/validations/itemGroup'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'

interface ItemGroupFormProps {
  initialData?: ItemGroup
  onSubmit: (data: ItemGroupFormData) => Promise<void>
  isLoading?: boolean
}

export function ItemGroupForm({ initialData, onSubmit, isLoading }: ItemGroupFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ItemGroupFormData>({
    resolver: zodResolver(itemGroupSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-200 mb-2">
          Nombre del Grupo *
        </label>
        <Input
          id="name"
          placeholder="Ej: Sistema de Audio Medio"
          error={errors.name?.message}
          {...register('name')}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-200 mb-2">
          Descripcion
        </label>
        <Textarea
          id="description"
          placeholder="Describe el contenido de este grupo..."
          rows={4}
          error={errors.description?.message}
          {...register('description')}
        />
      </div>

      <div className="flex justify-end gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => window.history.back()}
        >
          Cancelar
        </Button>
        <Button type="submit" variant="primary" isLoading={isLoading}>
          {initialData ? 'Guardar Cambios' : 'Crear Grupo'}
        </Button>
      </div>
    </form>
  )
}
