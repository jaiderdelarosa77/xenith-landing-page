import { NextRequest, NextResponse } from 'next/server'
import { contactSchema } from '@/lib/validations/contact'
import { ZodError } from 'zod'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate request body
    const validatedData = contactSchema.parse(body)

    // TODO: Here you would typically:
    // 1. Save to database
    // 2. Send email notification
    // 3. Integrate with CRM
    // For now, we'll just log it
    console.log('Contact form submission:', validatedData)

    // Simulate email sending (replace with actual email service)
    // Example: await sendEmail({
    //   to: 'contacto@xenith.com',
    //   subject: `Nuevo contacto: ${validatedData.subject}`,
    //   body: `
    //     Nombre: ${validatedData.name}
    //     Email: ${validatedData.email}
    //     Teléfono: ${validatedData.phone || 'No proporcionado'}
    //     Empresa: ${validatedData.company || 'No proporcionado'}
    //     Mensaje: ${validatedData.message}
    //   `
    // })

    return NextResponse.json(
      {
        success: true,
        message: 'Mensaje enviado correctamente',
      },
      { status: 200 }
    )
  } catch (error) {
    if (error instanceof ZodError) {
      return NextResponse.json(
        {
          success: false,
          message: 'Datos de formulario inválidos',
          errors: error.issues,
        },
        { status: 400 }
      )
    }

    console.error('Contact form error:', error)

    return NextResponse.json(
      {
        success: false,
        message: 'Error al procesar el mensaje',
      },
      { status: 500 }
    )
  }
}
