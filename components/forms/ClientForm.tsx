'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { clientSchema, ClientFormData, Client } from '@/lib/validations/client'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { FileUp } from 'lucide-react'
import toast from 'react-hot-toast'

interface ClientFormProps {
  client?: Client | null
  onSubmit: (data: ClientFormData) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
}

export function ClientForm({
  client,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: ClientFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientSchema),
    defaultValues: client
      ? {
          name: client.name,
          company: client.company || '',
          email: client.email,
          phone: client.phone || '',
          address: client.address || '',
          city: client.city || '',
          country: client.country || '',
          nit: client.nit || '',
          notes: client.notes || '',
          rutUrl: client.rutUrl || '',
        }
      : undefined,
  })

  const handleRutUpload = () => {
    toast('Funcionalidad de carga de RUT disponible proximamente', {
      icon: '📄',
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Nombre *"
          placeholder="Juan Perez"
          error={errors.name?.message}
          {...register('name')}
        />

        <Input
          label="Empresa"
          placeholder="Acme Corp"
          error={errors.company?.message}
          {...register('company')}
        />

        <Input
          label="NIT / Documento"
          placeholder="900.123.456-7"
          error={errors.nit?.message}
          {...register('nit')}
        />

        <Input
          label="Email *"
          type="email"
          placeholder="juan@example.com"
          error={errors.email?.message}
          {...register('email')}
        />

        <Input
          label="Telefono"
          placeholder="+57 300 123 4567"
          error={errors.phone?.message}
          {...register('phone')}
        />

        <Input
          label="Direccion"
          placeholder="Calle Principal #123"
          error={errors.address?.message}
          {...register('address')}
        />

        <Input
          label="Ciudad"
          placeholder="Bogota"
          error={errors.city?.message}
          {...register('city')}
        />

        <Input
          label="Pais"
          placeholder="Colombia"
          error={errors.country?.message}
          {...register('country')}
        />

        <div className="flex flex-col justify-end">
          <label className="block text-sm font-medium text-gray-200 mb-2">
            RUT (PDF)
          </label>
          <Button
            type="button"
            variant="outline"
            className="w-full justify-center"
            onClick={handleRutUpload}
          >
            <FileUp className="w-4 h-4 mr-2" />
            Adjuntar RUT
          </Button>
          {client?.rutUrl && (
            <p className="text-xs text-green-400 mt-1">RUT adjunto</p>
          )}
        </div>
      </div>

      <Textarea
        label="Notas"
        placeholder="Informacion adicional sobre el cliente..."
        rows={4}
        error={errors.notes?.message}
        {...register('notes')}
      />

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting}>
          {client ? 'Actualizar Cliente' : 'Crear Cliente'}
        </Button>
      </div>
    </form>
  )
}
