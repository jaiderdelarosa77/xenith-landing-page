'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { supplierSchema, SupplierFormData, Supplier } from '@/lib/validations/supplier'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'
import { FileUp } from 'lucide-react'
import toast from 'react-hot-toast'

interface SupplierFormProps {
  supplier?: Supplier | null
  onSubmit: (data: SupplierFormData) => Promise<void>
  onCancel: () => void
  isSubmitting?: boolean
  isContractor?: boolean
}

export function SupplierForm({
  supplier,
  onSubmit,
  onCancel,
  isSubmitting = false,
  isContractor = false,
}: SupplierFormProps) {
  const entityName = isContractor ? 'Contratista' : 'Proveedor'
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SupplierFormData>({
    resolver: zodResolver(supplierSchema),
    defaultValues: supplier
      ? {
          name: supplier.name,
          nit: supplier.nit || '',
          contactName: supplier.contactName || '',
          email: supplier.email || '',
          phone: supplier.phone || '',
          address: supplier.address || '',
          city: supplier.city || '',
          country: supplier.country || '',
          website: supplier.website || '',
          notes: supplier.notes || '',
          rutUrl: supplier.rutUrl || '',
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
          placeholder="AudioPro S.A.S"
          error={errors.name?.message}
          {...register('name')}
        />

        <Input
          label="NIT / Documento"
          placeholder="900.123.456-7"
          error={errors.nit?.message}
          {...register('nit')}
        />

        <Input
          label="Persona de Contacto"
          placeholder="Juan Garcia"
          error={errors.contactName?.message}
          {...register('contactName')}
        />

        <Input
          label="Email"
          type="email"
          placeholder="contacto@audiopro.com"
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
          label="Sitio Web"
          placeholder="https://audiopro.com"
          error={errors.website?.message}
          {...register('website')}
        />

        <Input
          label="Direccion"
          placeholder="Calle 100 #15-20"
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
          {supplier?.rutUrl && (
            <p className="text-xs text-green-400 mt-1">RUT adjunto</p>
          )}
        </div>
      </div>

      <Textarea
        label="Notas"
        placeholder={`Informacion adicional sobre el ${entityName.toLowerCase()}...`}
        rows={4}
        error={errors.notes?.message}
        {...register('notes')}
      />

      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" variant="primary" isLoading={isSubmitting}>
          {supplier ? `Actualizar ${entityName}` : `Crear ${entityName}`}
        </Button>
      </div>
    </form>
  )
}
