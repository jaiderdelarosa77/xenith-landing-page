import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db/prisma'
import { canViewModule } from '@/lib/auth/check-permission'
import { auth } from '@/auth'
import { SUPERADMIN_EMAIL } from '@/lib/validations/user'

// GET /api/tasks - List all tasks with filters
export async function GET(request: NextRequest) {
  try {
    const permissionCheck = await canViewModule('tareas')
    if (!permissionCheck.hasPermission) {
      return NextResponse.json(
        { error: permissionCheck.error },
        { status: permissionCheck.status }
      )
    }

    const session = await auth()
    const { searchParams } = new URL(request.url)
    const search = searchParams.get('search') || ''
    const status = searchParams.get('status')
    const priority = searchParams.get('priority')
    const assignedTo = searchParams.get('assignedTo')
    const myTasks = searchParams.get('myTasks')

    const where: any = {}

    // Search filter
    if (search) {
      where.OR = [
        { title: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } },
        { project: { title: { contains: search, mode: 'insensitive' } } },
      ]
    }

    // Status filter
    if (status) {
      where.status = status
    }

    // Priority filter
    if (priority) {
      where.priority = priority
    }

    // Assigned user filter
    if (assignedTo) {
      where.assignedTo = assignedTo
    }

    // My tasks filter - show only tasks assigned to current user
    if (myTasks === 'true' && session?.user?.id) {
      where.assignedTo = session.user.id
    }

    const tasks = await prisma.task.findMany({
      where,
      include: {
        project: {
          select: {
            id: true,
            title: true,
            status: true,
          },
        },
        assignedUser: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
      orderBy: [
        { status: 'asc' },
        { priority: 'desc' },
        { dueDate: 'asc' },
        { createdAt: 'desc' },
      ],
    })

    return NextResponse.json(tasks)
  } catch (error) {
    console.error('Error fetching tasks:', error)
    return NextResponse.json(
      { error: 'Error al obtener tareas' },
      { status: 500 }
    )
  }
}
