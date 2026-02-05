import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { prisma } from '@/lib/db/prisma'

// DELETE /api/item-groups/[id]/items/[itemId] - Remove an item from a group
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string; itemId: string }> }
) {
  try {
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { id: groupId, itemId } = await params

    // Verify the item group item exists
    const groupItem = await prisma.itemGroupItem.findFirst({
      where: {
        groupId,
        inventoryItemId: itemId,
      },
    })

    if (!groupItem) {
      return NextResponse.json(
        { error: 'Item no encontrado en el grupo' },
        { status: 404 }
      )
    }

    // Remove item from group
    await prisma.itemGroupItem.delete({
      where: { id: groupItem.id },
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

    return NextResponse.json(updatedGroup)
  } catch (error) {
    console.error('Error removing item from group:', error)
    return NextResponse.json(
      { error: 'Error al quitar item del grupo' },
      { status: 500 }
    )
  }
}
