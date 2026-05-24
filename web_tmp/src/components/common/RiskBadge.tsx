import { getRiskLabel, getRiskColor } from '@/utils/risk';

interface RiskBadgeProps { toxinUgL: number; showValue?: boolean; }

export default function RiskBadge({ toxinUgL, showValue = false }: RiskBadgeProps) {
  const color = getRiskColor(toxinUgL);
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold"
      style={{ color, background: `${color}14`, border: `1px solid ${color}30` }}>
      <span className="w-[7px] h-[7px] rounded-full" style={{ backgroundColor: color }} />
      {getRiskLabel(toxinUgL)}
      {showValue && <span className="ml-1">{toxinUgL.toFixed(2)}</span>}
    </span>
  );
}
