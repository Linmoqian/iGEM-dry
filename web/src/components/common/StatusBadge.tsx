import type { DeviceStatus } from '../../types/domain';
import { getStatusColor, getStatusText } from '../../utils/risk';

interface StatusBadgeProps {
  status: DeviceStatus;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const color = getStatusColor(status);
  const label = getStatusText(status);

  return (
    <span
      className={`
        inline-flex items-center gap-1.5
        px-2.5 py-1 rounded-[6px]
        text-[11px] font-semibold leading-tight
        ${className}
      `.trim()}
      style={{
        color,
        backgroundColor: `${color}1f`,
      }}
    >
      <span
        className="inline-block w-2 h-2 rounded-full shrink-0"
        style={{ backgroundColor: color }}
      />
      {label}
    </span>
  );
}
