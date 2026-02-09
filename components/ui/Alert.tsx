import { HTMLAttributes } from 'react'
import { cn } from '@/lib/utils/cn'
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react'

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  title?: string
}

export function Alert({
  className,
  variant = 'default',
  title,
  children,
  ...props
}: AlertProps) {
  const variants = {
    default: {
      container: 'bg-gray-800/50 text-gray-300 border-gray-700',
      icon: <Info className="w-5 h-5" />,
    },
    success: {
      container: 'bg-green-500/10 text-green-400 border-green-500/20',
      icon: <CheckCircle className="w-5 h-5" />,
    },
    warning: {
      container: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      icon: <AlertCircle className="w-5 h-5" />,
    },
    error: {
      container: 'bg-red-500/10 text-red-400 border-red-500/20',
      icon: <XCircle className="w-5 h-5" />,
    },
    info: {
      container: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      icon: <Info className="w-5 h-5" />,
    },
  }

  const config = variants[variant]

  return (
    <div
      className={cn(
        'relative flex gap-3 p-4 rounded-lg border',
        config.container,
        className
      )}
      role="alert"
      {...props}
    >
      <div className="flex-shrink-0 mt-0.5">{config.icon}</div>
      <div className="flex-1">
        {title && <h5 className="font-medium mb-1">{title}</h5>}
        <div className="text-sm">{children}</div>
      </div>
    </div>
  )
}
