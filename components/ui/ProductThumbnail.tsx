'use client'

import { useState } from 'react'
import { ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { ImagePreviewModal } from './ImagePreviewModal'

interface ProductThumbnailProps {
  imageUrl?: string | null
  productName: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
  showPreviewOnClick?: boolean
}

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-12 h-12',
  lg: 'w-16 h-16',
}

const iconSizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
}

export function ProductThumbnail({
  imageUrl,
  productName,
  size = 'md',
  className,
  showPreviewOnClick = true,
}: ProductThumbnailProps) {
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [imageError, setImageError] = useState(false)

  const hasValidImage = imageUrl && !imageError

  const handleClick = (e: React.MouseEvent) => {
    if (showPreviewOnClick && hasValidImage) {
      e.stopPropagation()
      setIsPreviewOpen(true)
    }
  }

  const handleImageError = () => {
    setImageError(true)
  }

  return (
    <>
      <div
        onClick={handleClick}
        className={cn(
          'flex-shrink-0 rounded-lg overflow-hidden bg-gray-800 border border-gray-700',
          'flex items-center justify-center',
          sizeClasses[size],
          hasValidImage && showPreviewOnClick && 'cursor-zoom-in hover:border-orange-500 transition-colors',
          className
        )}
        title={hasValidImage && showPreviewOnClick ? 'Click para ampliar' : productName}
      >
        {hasValidImage ? (
          <>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt={productName}
              className="w-full h-full object-cover"
              onError={handleImageError}
            />
          </>
        ) : (
          <ImageIcon className={cn('text-gray-600', iconSizeClasses[size])} />
        )}
      </div>

      {showPreviewOnClick && (
        <ImagePreviewModal
          isOpen={isPreviewOpen}
          onClose={() => setIsPreviewOpen(false)}
          imageUrl={imageUrl || null}
          alt={productName}
        />
      )}
    </>
  )
}
