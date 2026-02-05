import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/db/prisma'
import { addItemToGroupSchema } from '@/lib/validations/itemGroup'
import { ZodError } from 'zod'

// POST /api/item-groups/[id]/items - Add an item to a group
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { id: groupId } = await params
    const body = await request.json()
    const validatedData = addItemToGroupSchema.parse(body)

    // Verify group exists
    const group = await prisma.itemGroup.findUnique({
      where: { id: groupId },
    })

    if (!group) {
      return NextResponse.json(
        { error: 'Grupo no encontrado' },
        { status: 404 }
      )
    }

    // Verify inventory item exists
    const inventoryItem = await prisma.inventoryItem.findUnique({
      where: { id: validatedData.inventoryItemId },
    })

    if (!inventoryItem) {
      return NextResponse.json(
        { error: 'Item de inventario no encontrado' },
        { status: 404 }
      )
    }

    // Check if item is already in the group
    const existingItem = await prisma.itemGroupItem.findUnique({
      where: {
        groupId_inventoryItemId: {
          groupId,
          inventoryItemId: validatedData.inventoryItemId,
        },
      },
    })

    if (existingItem) {
      return NextResponse.json(
        { error: 'Este item ya está en el grupo' },
        { status: 400 }
      )
    }

    // Add item to group
    await prisma.itemGroupItem.create({
      data: {
        groupId,
        inventoryItemId: validatedData.inventoryItemId,
        quantity: validatedData.quantity,
        notes: validatedData.notes || null,
      },
    })

    // Return updated group
    const updatedGroup = await prisma.itemGroup.findUnique({
      where: { id: groupId },
      include: {
        items: {
          include: {
            inventoryItem: {
              select: {
                id: true,
                serialNumber: true,
                assetTag: true,
                status: true,
                location: true,
                product: {
                  select: {
                    id: true,
                    sku: true,
                    name: true,
                    brand: true,
                    model: true,
                    rentalPrice: true,
                    category: {
                      select: {
                        id: true,
                        name: true,
                        color: true,
                      },
                    },
                  },
                },
              },
            },
          },
          orderBy: { createdAt: 'asc' },
        },
        _count: {
          select: {
            items: true,
          },
        },
      },
    })

    return NextResponse.json(updatedGroup, { status: 201 })
  } catch (error) {
    if (error instanceof ZodError) {
      return NextResponse.json(
        { error: 'Datos inválidos', issues: error.issues },
        { status: 400 }
      )
    }

    console.error('Error adding item to group:', error)
    return NextResponse.json(
      { error: 'Error al agregar item al grupo' },
      { status: 500 }
    )
  }
}
