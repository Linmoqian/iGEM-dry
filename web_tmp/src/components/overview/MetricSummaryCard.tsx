import type { ReactNode } from 'react';
import AquaCard from '@/components/common/AquaCard';

interface MetricSummaryCardProps {
  label: string; value: string; suffix?: string; description?: string; color: string; icon: ReactNode;
}

export default function MetricSummaryCard({ label, value, suffix, description, color, icon }: MetricSummaryCardProps) {
  return (
    <AquaCard className="p-5 flex items-center gap-5 min-h-[108px]">
      <div className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${color}14`, color }}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] font-semibold text-[var(--color-muted)] mb-1">{label}</p>
        <p className="text-[32px] font-extrabold tracking-[-0.02em] leading-none" style={{ color }}>
          {value}
          {suffix && <span className="text-[13px] font-semibold ml-1.5 align-baseline" style={{ color }}>{suffix}</span>}
        </p>
        {description && <p className="text-[11px] text-[var(--color-muted)] mt-1.5 truncate">{description}</p>}
      </div>
    </AquaCard>
  );
}
