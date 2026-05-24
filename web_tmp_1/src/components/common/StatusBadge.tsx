import type { DeviceStatus } from '../../types/domain';

interface StatusBadgeProps {
  status: DeviceStatus;
  size?: 'sm' | 'md';
}

const statusConfig: Record<DeviceStatus, { label: string; color: string; bg: string }> = {
  online: { label: '在线采样', color: '#22C55E', bg: '#22C55E1A' },
  idle: { label: '待机', color: '#F59E0B', bg: '#F59E0B1A' },
  offline: { label: '离线', color: '#94A3B8', bg: '#94A3B81A' },
};

export default function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
  const cfg = statusConfig[status];
  const dotSize = size === 'sm' ? 'w-2 h-2' : 'w-2.5 h-2.5';
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm';

  return (
    <div className="flex items-center gap-1.5">
      <div className={`${dotSize} rounded-full`} style={{ backgroundColor: cfg.color }} />
      <span className={`${textSize}`} style={{ color: cfg.color }}>{cfg.label}</span>
    </div>
  );
}
