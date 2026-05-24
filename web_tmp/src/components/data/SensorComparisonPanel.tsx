import AquaPanel from '@/components/common/AquaPanel';
import { getRiskColor } from '@/utils/risk';
import type { DeviceReading } from '@/types/domain';

interface P { readings: DeviceReading[]; }

export default function SensorComparisonPanel({ readings }: P) {
  const sorted = [...readings].sort((a, b) => b.toxinUgL - a.toxinUgL);
  return (
    <AquaPanel title="传感器对比" subtitle="按当前浓度排序">
      <div className="flex flex-col max-h-[360px] overflow-y-auto">
        {sorted.map((r, i) => {
          const color = getRiskColor(r.toxinUgL);
          return (
            <div key={r.id} className={`flex items-center justify-between py-3 ${i < sorted.length - 1 ? 'border-b border-[var(--color-border)]' : ''}`}>
              <div className="flex items-center gap-2.5 min-w-0">
                <span className="w-[9px] h-[9px] rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                <span className="text-[13px] font-semibold text-[var(--color-text)] truncate">{r.name}</span>
              </div>
              <span className="text-[15px] font-extrabold flex-shrink-0 ml-3" style={{ color }}>{r.toxinUgL.toFixed(2)}</span>
            </div>
          );
        })}
      </div>
    </AquaPanel>
  );
}
