import { useState, type ReactNode } from 'react';
import { Image as ImageIcon } from 'lucide-react';

interface ImagePlaceholderProps {
  name?: string;
  width: number | string;
  height: number | string;
  src?: string;
  fallback?: ReactNode;
  className?: string;
  alt?: string;
}

export default function ImagePlaceholder({
  name,
  width,
  height,
  src,
  fallback,
  className = '',
  alt,
}: ImagePlaceholderProps) {
  const [imgError, setImgError] = useState(false);

  const w = typeof width === 'number' ? `${width}px` : width;
  const h = typeof height === 'number' ? `${height}px` : height;

  // Show real image if src is provided and no error
  if (src && !imgError) {
    return (
      <div
        className={`relative shrink-0 ${className}`}
        style={{ width: w, height: h }}
      >
        <img
          src={src}
          alt={alt ?? name ?? ''}
          className="w-full h-full object-contain rounded-[12px]"
          onError={() => setImgError(true)}
        />
      </div>
    );
  }

  // Fallback placeholder
  if (fallback) {
    return (
      <div className={`shrink-0 ${className}`} style={{ width: w, height: h }}>
        {fallback}
      </div>
    );
  }

  return (
    <div
      className={`
        shrink-0 flex flex-col items-center justify-center gap-1
        rounded-[12px] border border-dashed
        ${className}
      `.trim()}
      style={{
        width: w,
        height: h,
        borderColor: 'rgba(14, 165, 233, 0.3)',
        backgroundColor: 'rgba(14, 165, 233, 0.06)',
      }}
    >
      <ImageIcon size={16} className="text-muted opacity-40" />
      {name && (
        <span className="text-[10px] text-muted text-center leading-tight px-1 truncate max-w-full">
          {name}
        </span>
      )}
      <span className="text-[9px] text-muted opacity-50">
        {typeof width === 'number' && typeof height === 'number'
          ? `${width}×${height}`
          : ''}
      </span>
    </div>
  );
}
