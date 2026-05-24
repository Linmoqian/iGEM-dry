import { useNavigate } from 'react-router-dom';
import AquaPanel from '@/components/common/AquaPanel';
import StatusBadge from '@/components/common/StatusBadge';
import AppButton from '@/components/common/AppButton';
import { getRiskColor } from '@/utils/risk';
import type { DeviceReading } from '@/types/domain';

interface P { readings: DeviceReading[]; }

export default function LatestReadingsTable({ readings }: P) {
  const navigate = useNavigate();
  const recent = readings.slice().sort((a, b) => b.updatedAt.localeCompare(a.updatedAt)).slice(0, 5);

  return (
    <AquaPanel title="最新采样" subtitle="设备端回传的藻毒素浓度、电量和信号质量"
      action={<AppButton variant="secondary" onClick={() => navigate('/map')}>查看全部 <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg></AppButton>}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-[rgba(45,124,255,0.03)]">
              {['设备名称','采样时间','藻毒素','电量','信号强度','状态','位置'].map((h) => (
                <th key={h} className="text-left py-3 px-4 text-[11px] font-semibold text-[var(--color-muted)] first:rounded-tl-2xl last:rounded-tr-2xl">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {recent.map((r) => {
              const rc = getRiskColor(r.toxinUgL);
              return (
                <tr key={r.id} className="border-b border-[rgba(45,124,255,0.04)] hover:bg-[rgba(45,124,255,0.02)] transition-colors">
                  <td className="py-3 px-4"><div className="flex items-center gap-2"><span className="w-[9px] h-[9px] rounded-full flex-shrink-0" style={{ backgroundColor: rc }} /><span className="text-[13px] font-semibold text-[var(--color-text)] truncate">{r.name}</span></div></td>
                  <td className="py-3 px-4 text-[13px] text-[var(--color-muted)]">{r.updatedAt}</td>
                  <td className="py-3 px-4"><span className="text-[15px] font-extrabold" style={{ color: rc }}>{r.toxinUgL.toFixed(2)} <span className="text-[11px] font-normal text-[var(--color-muted)]">μg/L</span></span></td>
                  <td className="py-3 px-4"><span className={`text-[13px] font-semibold ${r.batteryPercent < 20 ? 'text-[#ff3b30]' : 'text-[var(--color-text)]'}`}>{r.batteryPercent}%</span></td>
                  <td className="py-3 px-4 text-[13px] text-[var(--color-muted)]">{r.signalDbm} dBm</td>
                  <td className="py-3 px-4"><StatusBadge status={r.status} /></td>
                  <td className="py-3 px-4 text-[13px] text-[var(--color-muted)] truncate max-w-[150px]">{r.locationLabel}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </AquaPanel>
  );
}
