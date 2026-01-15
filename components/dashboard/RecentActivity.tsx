import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { FileText, FolderKanban, Users, DollarSign } from 'lucide-react'

interface Activity {
  id: string
  type: 'project' | 'client' | 'quotation' | 'payment'
  title: string
  description: string
  timestamp: string
  status?: 'success' | 'warning' | 'info'
}

const activities: Activity[] = [
  {
    id: '1',
    type: 'project',
    title: 'Nuevo proyecto creado',
    description: 'Sistema de Automatización Industrial',
    timestamp: 'Hace 2 horas',
    status: 'success',
  },
  {
    id: '2',
    type: 'quotation',
    title: 'Cotización enviada',
    description: 'QT-2026-0001 - Empresa Demo S.A.',
    timestamp: 'Hace 5 horas',
    status: 'info',
  },
  {
    id: '3',
    type: 'client',
    title: 'Nuevo cliente registrado',
    description: 'Juan Pérez - Empresa Demo',
    timestamp: 'Hace 1 día',
    status: 'success',
  },
  {
    id: '4',
    type: 'payment',
    title: 'Pago recibido',
    description: '$87,000.00 MXN - Anticipo 50%',
    timestamp: 'Hace 2 días',
    status: 'success',
  },
]

const activityIcons = {
  project: FolderKanban,
  client: Users,
  quotation: FileText,
  payment: DollarSign,
}

const activityColors = {
  project: 'text-violet-400 bg-violet-500/10',
  client: 'text-blue-400 bg-blue-500/10',
  quotation: 'text-amber-400 bg-amber-500/10',
  payment: 'text-green-400 bg-green-500/10',
}

export function RecentActivity() {
  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle>Actividad Reciente</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const Icon = activityIcons[activity.type]
            const colorClass = activityColors[activity.type]

            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 p-3 rounded-lg hover:bg-gray-900/30 transition-colors"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <p className="text-sm font-medium text-gray-200">
                      {activity.title}
                    </p>
                    {activity.status && (
                      <Badge variant={activity.status} className="flex-shrink-0">
                        {activity.status === 'success' && 'Completado'}
                        {activity.status === 'warning' && 'Pendiente'}
                        {activity.status === 'info' && 'En proceso'}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-400 mb-1">
                    {activity.description}
                  </p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
