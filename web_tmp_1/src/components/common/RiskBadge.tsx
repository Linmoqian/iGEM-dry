import type { RiskLevel } from '../../types/domain';

interface RiskBadgeProps {
  level: RiskLevel;
  value: number;
  showValue?: boolean;
}

const riskConfig: Record<RiskLevel, { label: string; color: string }> = {
  normal: { label: '正常', color: '#22C55E' },
  watch: { label: '关注', color: '#F59E0B' },
  warning: { label: '警戒', color: '#FF7A00' },
  critical: { label: '高风险', color: '#EF4444' },
};

export default function RiskBadge({ level, value, showValue = false }: RiskBadgeProps) {
  const cfg = riskConfig[level];
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
      <span className="text-xs font-medium" style={{ color: cfg.color }}>
        {cfg.label}
      </span>
      {showValue && (
        <span className="text-xs ml-1" style={{ color: cfg.color }}>
          {value.toFixed(2)} µg/L
        </span>
      )}
    </div>
  );
}
