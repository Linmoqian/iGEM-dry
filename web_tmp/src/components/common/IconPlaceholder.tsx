import { useState } from 'react';
import { isAssetAvailable } from '@/assets/assetMap';

interface IconPlaceholderProps {
  size: number;
  label: string;
  src?: string;
  iconType?: 'wifi' | 'bluetooth' | 'battery' | 'signal' | 'warning' | 'check' | 'add' | 'refresh' | 'export' | 'location';
  color?: string;
  className?: string;
}

const iconPaths: Record<string, string> = {
  wifi: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0',
  bluetooth: 'M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7',
  battery: 'M21 10.5h.375c.621 0 1.125.504 1.125 1.125v4.5c0 .621-.504 1.125-1.125 1.125H21M4.5 9h12a2.25 2.25 0 012.25 2.25v6.75A2.25 2.25 0 0116.5 20.25h-12A2.25 2.25 0 012.25 18v-6.75A2.25 2.25 0 014.5 9z',
  signal: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0',
  warning: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z',
  check: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  add: 'M12 4v16m8-8H4',
  refresh: 'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182',
  export: 'M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3',
  location: 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0z M19.5 10.5c0 7.142-9.5 11.25-9.5 11.25S.5 17.642.5 10.5a9.5 9.5 0 0119 0z',
};

export default function IconPlaceholder({ size, label, src, iconType, color = '#5A7184', className = '' }: IconPlaceholderProps) {
  const [imgError, setImgError] = useState(false);
  const path = iconType ? iconPaths[iconType] : null;

  if (src && isAssetAvailable(src) && !imgError) {
    return (
      <img
        src={src}
        alt={label}
        className={className}
        style={{ width: size, height: size }}
        onError={() => setImgError(true)}
      />
    );
  }

  return (
    <div
      className={`flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      title={label}
      aria-label={label}
    >
      {path ? (
        <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d={path} />
        </svg>
      ) : (
        <div
          className="placeholder-box rounded-lg"
          style={{ width: size, height: size }}
        >
          <span className="text-[8px] text-[#5A7184]/60">{label}</span>
        </div>
      )}
    </div>
  );
}
