import type { ReactNode } from 'react';
import { Image as ImageIcon } from 'lucide-react';

interface IconPlaceholderProps {
  name?: string;
  size?: number;
  fallback?: ReactNode;
  className?: string;
}

export default function IconPlaceholder({
  name,
  size = 24,
  fallback,
  className = '',
}: IconPlaceholderProps) {
  if (fallback) {
    return (
      <div className={`shrink-0 ${className}`} style={{ width: size, height: size }}>
        {fallback}
      </div>
    );
  }

  return (
    <div
      className={`
        shrink-0 flex flex-col items-center justify-center
        rounded-[8px] border border-dashed
        ${className}
      `.trim()}
      style={{
        width: size,
        height: size,
        borderColor: 'rgba(14, 165, 233, 0.3)',
        backgroundColor: 'rgba(14, 165, 233, 0.06)',
      }}
    >
      {size >= 32 ? (
        <>
          <ImageIcon size={Math.min(size * 0.35, 16)} className="text-muted opacity-40" />
          {name && (
            <span
              className="text-muted text-center leading-tight px-0.5 truncate max-w-full"
              style={{ fontSize: Math.max(8, size * 0.16) }}
            >
              {name}
            </span>
          )}
        </>
      ) : (
        <span
          className="text-muted opacity-60 leading-none"
          style={{ fontSize: Math.max(7, size * 0.35) }}
        >
          {name?.charAt(0) ?? '?'}
        </span>
      )}
    </div>
  );
}
