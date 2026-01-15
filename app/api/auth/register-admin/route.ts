import { NextResponse } from 'next/server'
import { hash } from 'bcrypt'
import { prisma } from '@/lib/db/prisma'

export async function POST() {
  try {
    // Check if admin already exists
    const existingUser = await prisma.user.findUnique({
      where: { email: 'admin@xenith.com' },
    })

    if (existingUser) {
      return NextResponse.json(
        { message: 'Admin user already exists' },
        { status: 400 }
      )
    }

    // Create admin user with hashed password
    const hashedPassword = await hash('admin123', 10)

    const user = await prisma.user.create({
      data: {
        email: 'admin@xenith.com',
        name: 'Admin XENITH',
        password: hashedPassword,
      },
    })

    return NextResponse.json({
      message: 'Admin user created successfully',
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    console.error('Error creating admin user:', error)
    return NextResponse.json(
      { message: 'Error creating admin user', error: String(error) },
      { status: 500 }
    )
  }
}
