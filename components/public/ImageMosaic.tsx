'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'
import { ImageIcon } from 'lucide-react'

interface MosaicImage {
  src: string
  alt: string
  span?: 'normal' | 'wide' | 'tall' | 'large'
}

const defaultImages: MosaicImage[] = [
  { src: '/images/mosaic/img-1.jpg', alt: 'Robotica Industrial', span: 'large' },
  { src: '/images/mosaic/img-2.jpg', alt: 'Desarrollo Web', span: 'normal' },
  { src: '/images/mosaic/img-3.jpg', alt: 'IoT Solutions', span: 'tall' },
  { src: '/images/mosaic/img-4.jpg', alt: 'Cloud Computing', span: 'normal' },
  { src: '/images/mosaic/img-5.jpg', alt: 'Automatizacion', span: 'wide' },
  { src: '/images/mosaic/img-6.jpg', alt: 'Software a Medida', span: 'normal' },
  { src: '/images/mosaic/img-7.jpg', alt: 'Consultoria Tech', span: 'normal' },
  { src: '/images/mosaic/img-8.jpg', alt: 'Integracion de Sistemas', span: 'tall' },
]

interface ImageMosaicProps {
  images?: MosaicImage[]
  title?: string
  subtitle?: string
}

export function ImageMosaic({
  images = defaultImages,
  title = 'Nuestros Proyectos',
  subtitle = 'Una muestra de nuestro trabajo y dedicacion en cada proyecto',
}: ImageMosaicProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const [loadedImages, setLoadedImages] = useState<Set<number>>(new Set())
  const [errorImages, setErrorImages] = useState<Set<number>>(new Set())

  const getSpanClasses = (span?: string) => {
    switch (span) {
      case 'wide':
        return 'md:col-span-2'
      case 'tall':
        return 'md:row-span-2'
      case 'large':
        return 'md:col-span-2 md:row-span-2'
      default:
        return ''
    }
  }

  const handleImageLoad = (index: number) => {
    setLoadedImages((prev) => new Set(prev).add(index))
  }

  const handleImageError = (index: number) => {
    setErrorImages((prev) => new Set(prev).add(index))
  }

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {title.split(' ').map((word, i, arr) =>
              i === arr.length - 1 ? (
                <span key={i} className="text-gradient">{word}</span>
              ) : (
                <span key={i}>{word} </span>
              )
            )}
          </h2>
          <p className="text-gray-400 max-w-2xl mx-auto">{subtitle}</p>
        </div>

        {/* Mosaic Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 auto-rows-[150px] md:auto-rows-[200px]">
          {images.map((image, index) => (
            <div
              key={index}
              className={cn(
                'group relative overflow-hidden rounded-2xl cursor-pointer',
                'bg-gray-900/50 backdrop-blur-sm',
                'transition-all duration-500 ease-out',
                getSpanClasses(image.span),
                hoveredIndex === index && 'z-10 scale-[1.02]',
                hoveredIndex !== null && hoveredIndex !== index && 'opacity-70 scale-[0.98]'
              )}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* Gradient Border Effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-orange-500/20 via-transparent to-amber-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              {/* Image Container */}
              <div className="absolute inset-[1px] rounded-2xl overflow-hidden bg-gray-900">
                {/* Placeholder when no image or error */}
                {errorImages.has(index) ? (
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-800 via-gray-900 to-gray-800 flex flex-col items-center justify-center">
                    <div className="relative">
                      <div className="absolute inset-0 bg-orange-500/20 blur-xl rounded-full" />
                      <ImageIcon className="w-10 h-10 md:w-16 md:h-16 text-gray-600 relative z-10" />
                    </div>
                    <span className="text-xs md:text-sm text-gray-500 mt-3 font-medium">
                      {image.alt}
                    </span>
                  </div>
                ) : (
                  <>
                    {/* Loading State */}
                    <div
                      className={cn(
                        'absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900',
                        'flex items-center justify-center transition-opacity duration-500',
                        loadedImages.has(index) ? 'opacity-0 pointer-events-none' : 'opacity-100'
                      )}
                    >
                      <div className="w-8 h-8 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
                    </div>

                    {/* Actual Image */}
                    <img
                      src={image.src}
                      alt={image.alt}
                      className={cn(
                        'absolute inset-0 w-full h-full object-cover transition-all duration-700 ease-out',
                        'group-hover:scale-110',
                        loadedImages.has(index) ? 'opacity-100' : 'opacity-0'
                      )}
                      onLoad={() => handleImageLoad(index)}
                      onError={() => handleImageError(index)}
                    />
                  </>
                )}

                {/* Overlay Gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Shine Effect */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
                </div>

                {/* Content Overlay */}
                <div className="absolute inset-0 flex flex-col justify-end p-4 md:p-6 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-500">
                  <span className="text-xs md:text-sm text-orange-400 font-medium mb-1">
                    Proyecto {String(index + 1).padStart(2, '0')}
                  </span>
                  <h3 className="text-sm md:text-lg font-bold text-white line-clamp-2">
                    {image.alt}
                  </h3>
                </div>

                {/* Corner Accent */}
                <div className="absolute top-3 right-3 w-2 h-2 md:w-3 md:h-3 rounded-full bg-orange-500 opacity-0 group-hover:opacity-100 transition-all duration-500 group-hover:scale-100 scale-0" />
              </div>

              {/* Glow Effect */}
              <div className="absolute -inset-1 bg-gradient-to-r from-orange-600 to-amber-600 rounded-2xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-500 -z-10" />
            </div>
          ))}
        </div>

        {/* Bottom Accent Line */}
        <div className="mt-12 flex justify-center">
          <div className="h-1 w-32 bg-gradient-to-r from-transparent via-orange-500 to-transparent rounded-full" />
        </div>
      </div>
    </section>
  )
}
