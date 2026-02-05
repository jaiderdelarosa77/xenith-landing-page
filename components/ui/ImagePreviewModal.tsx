'use client'

import { useEffect, useCallback } from 'react'
import { X, ZoomIn, ZoomOut, RotateCw } from 'lucide-react'
import { cn } from '@/lib/utils/cn'
import { useState } from 'react'

interface ImagePreviewModalProps {
  isOpen: boolean
  onClose: () => void
  imageUrl: string | null
  alt?: string
}

export function ImagePreviewModal({
  isOpen,
  onClose,
  imageUrl,
  alt = 'Imagen',
}: ImagePreviewModalProps) {
  const [scale, setScale] = useState(1)
  const [rotation, setRotation] = useState(0)

  // Reset transforms when modal opens
  useEffect(() => {
    if (isOpen) {
      setScale(1)
      setRotation(0)
    }
  }, [isOpen])

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, onClose])

  const handleZoomIn = useCallback(() => {
    setScale((prev) => Math.min(prev + 0.25, 3))
  }, [])

  const handleZoomOut = useCallback(() => {
    setScale((prev) => Math.max(prev - 0.25, 0.5))
  }, [])

  const handleRotate = useCallback(() => {
    setRotation((prev) => (prev + 90) % 360)
  }, [])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isOpen || !imageUrl) return null

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-gray-800/80 text-white hover:bg-gray-700 transition-colors z-10"
      >
        <X className="w-6 h-6" />
      </button>

      {/* Controls */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 p-2 rounded-lg bg-gray-800/80 z-10">
        <button
          onClick={handleZoomOut}
          disabled={scale <= 0.5}
          className={cn(
            'p-2 rounded-lg text-white transition-colors',
            scale <= 0.5
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-gray-700'
          )}
        >
          <ZoomOut className="w-5 h-5" />
        </button>

        <span className="text-white text-sm min-w-[60px] text-center">
          {Math.round(scale * 100)}%
        </span>

        <button
          onClick={handleZoomIn}
          disabled={scale >= 3}
          className={cn(
            'p-2 rounded-lg text-white transition-colors',
            scale >= 3
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-gray-700'
          )}
        >
          <ZoomIn className="w-5 h-5" />
        </button>

        <div className="w-px h-6 bg-gray-600 mx-1" />

        <button
          onClick={handleRotate}
          className="p-2 rounded-lg text-white hover:bg-gray-700 transition-colors"
        >
          <RotateCw className="w-5 h-5" />
        </button>
      </div>

      {/* Image container */}
      <div className="relative max-w-[90vw] max-h-[85vh] overflow-hidden">
        <img
          src={imageUrl}
          alt={alt}
          className="max-w-full max-h-[85vh] object-contain transition-transform duration-200"
          style={{
            transform: `scale(${scale}) rotate(${rotation}deg)`,
          }}
          draggable={false}
        />
      </div>
    </div>
  )
}
