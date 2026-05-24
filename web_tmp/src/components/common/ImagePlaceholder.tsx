import { useState } from 'react';
import { isAssetAvailable } from '@/assets/assetMap';

interface ImagePlaceholderProps {
  width: number;
  height: number;
  label: string;
  src?: string;
  fileName?: string;
  variant?: 'mascot' | 'device' | 'illustration' | 'decoration';
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  className?: string;
}

const roundedMap = {
  sm: 'rounded-lg',
  md: 'rounded-xl',
  lg: 'rounded-2xl',
  full: 'rounded-full',
};

const variantRounded: Record<string, string> = {
  mascot: 'rounded-2xl',
  device: 'rounded-xl',
  illustration: 'rounded-xl',
  decoration: 'rounded-xl',
};

export default function ImagePlaceholder({
  width,
  height,
  label,
  src,
  fileName,
  variant = 'illustration',
  rounded,
  className = '',
}: ImagePlaceholderProps) {
  const [imgError, setImgError] = useState(false);
  const borderRadius = rounded ? roundedMap[rounded] : variantRounded[variant];

  if (src && isAssetAvailable(src) && !imgError) {
    return (
      <img
        src={src}
        alt={label}
        className={`object-cover ${borderRadius} ${className}`}
        style={{ width, height, minWidth: width, minHeight: height }}
        onError={() => setImgError(true)}
      />
    );
  }

  return (
    <div
      className={`placeholder-box ${borderRadius} ${className}`}
      style={{ width, height, minWidth: width, minHeight: height }}
    >
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(13,125,242,0.2)" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
      <span className="placeholder-label mt-1">{label}</span>
      {fileName && <span className="text-[8px] text-[#5A7184]/40 mt-0.5">{fileName}</span>}
    </div>
  );
}
