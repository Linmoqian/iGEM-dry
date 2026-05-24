import type { RiskLevel } from '../../types/domain';
import { getRiskLevel, getRiskColor, getRiskLabel } from '../../utils/risk';

interface RiskBadgeProps {
  toxin?: number;
  level?: RiskLevel;
  className?: string;
}

const levelColors: Record<RiskLevel, string> = {
  normal: '#22c55e',
  attention: '#f59e0b',
  warning: '#f97316',
  danger: '#ef4444',
};

const levelLabels: Record<RiskLevel, string> = {
  normal: '正常',
  attention: '关注',
  warning: '警戒',
  danger: '高风险',
};

export default function RiskBadge({ toxin, level, className = '' }: RiskBadgeProps) {
  const resolvedLevel = level ?? (toxin !== undefined ? getRiskLevel(toxin) : 'normal');
  const color = toxin !== undefined ? getRiskColor(toxin) : levelColors[resolvedLevel];
  const label = toxin !== undefined ? getRiskLabel(toxin) : levelLabels[resolvedLevel];

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
      {label}
    </span>
  );
}
