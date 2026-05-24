import AquaPanel from '@/components/common/AquaPanel';
import RiskBadge from '@/components/common/RiskBadge';
import StatusBadge from '@/components/common/StatusBadge';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';
import AppButton from '@/components/common/AppButton';
import { getSignalLabel } from '@/utils/risk';
import type { DeviceReading } from '@/types/domain';

interface P { reading: DeviceReading; onViewHistory?: () => void; }

export default function SelectedDevicePanel({ reading, onViewHistory }: P) {
  return (
    <AquaPanel title="选中设备">
      <div className="flex flex-col gap-5">
        <div>
          <h2 className="text-[18px] font-extrabold text-[var(--color-text)]">{reading.name}</h2>
          <p className="text-[12px] text-[var(--color-muted)] mt-1">{reading.locationLabel}</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <RiskBadge toxinUgL={reading.toxinUgL} />
          <StatusBadge status={reading.status} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {[
            ['藻毒素浓度', `${reading.toxinUgL.toFixed(2)} μg/L`, reading.toxinUgL > 5 ? '#ff3b30' : 'var(--color-text)'],
            ['更新时间', reading.updatedAt, 'var(--color-text)'],
            ['电量', `${reading.batteryPercent}%`, reading.batteryPercent < 20 ? '#ff3b30' : 'var(--color-text)'],
            ['信号强度', `${reading.signalDbm} dBm`, 'var(--color-text)'],
            ['水温', `${reading.waterTempC.toFixed(1)} °C`, 'var(--color-text)'],
            ['pH', reading.ph.toFixed(1), 'var(--color-text)'],
          ].map(([label, value, color]) => (
            <div key={label} className="p-3 rounded-2xl bg-[rgba(45,124,255,0.03)]">
              <p className="text-[10px] text-[var(--color-muted)] font-semibold uppercase tracking-wider">{label}</p>
              <p className="text-[15px] font-extrabold mt-0.5" style={{ color }}>{value}</p>
            </div>
          ))}
        </div>
        <div className="border-t border-[var(--color-border)] pt-4 flex flex-col gap-1.5">
          {[
            ['设备类型', '水质监测浮标'],
            ['连接方式', reading.connectionType === 'wifi' ? 'WiFi' : reading.connectionType === 'bluetooth' ? '蓝牙' : '未连接'],
            ['信号质量', getSignalLabel(reading.signalDbm)],
          ].map(([label, value]) => (
            <div key={label} className="flex items-center justify-between text-[12px]">
              <span className="text-[var(--color-muted)]">{label}</span>
              <span className="font-semibold text-[var(--color-text)]">{value}</span>
            </div>
          ))}
        </div>
        {onViewHistory && (
          <AppButton variant="secondary" onClick={onViewHistory} className="w-full">
            查看历史数据 <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
          </AppButton>
        )}
        <ImagePlaceholder width={120} height={100} label="设备插画占位" variant="device" className="mx-auto" />
      </div>
    </AquaPanel>
  );
}
