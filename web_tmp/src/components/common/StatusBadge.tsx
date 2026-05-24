import type { DeviceStatus } from '@/types/domain';
import { getStatusText } from '@/utils/risk';

interface StatusBadgeProps {
  status: DeviceStatus;
}

const statusConfig: Record<DeviceStatus, { dot: string; text: string; bg: string }> = {
  online:  { dot: '#1db954', text: '#1db954', bg: 'rgba(29,185,84,0.08)' },
  idle:    { dot: '#ffb400', text: '#ffb400', bg: 'rgba(255,180,0,0.08)' },
  offline: { dot: '#ff3b30', text: '#ff3b30', bg: 'rgba(255,59,48,0.08)' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const c = statusConfig[status];
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold" style={{ color: c.text, background: c.bg }}>
      <span className={`w-[7px] h-[7px] rounded-full ${status === 'online' ? 'animate-pulse' : ''}`} style={{ backgroundColor: c.dot }} />
      {getStatusText(status)}
    </span>
  );
}
