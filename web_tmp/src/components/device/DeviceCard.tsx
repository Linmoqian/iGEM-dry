import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import StatusBadge from '@/components/common/StatusBadge';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';
import AppButton from '@/components/common/AppButton';
import { getRiskColor, getSignalLabel } from '@/utils/risk';
import type { DeviceItem } from '@/types/domain';

interface P { device: DeviceItem; onConnect: (t: 'bluetooth' | 'wifi') => void; onDisconnect: () => void; onDetails: () => void; onEdit: () => void; onDelete: () => void; }

export default function DeviceCard({ device, onConnect, onDisconnect, onDetails, onEdit, onDelete }: P) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: device.id });
  const style = { transform: CSS.Transform.toString(transform), transition, zIndex: isDragging ? 10 : 1, opacity: isDragging ? 0.85 : device.status === 'offline' ? 0.55 : 1 };
  const riskColor = getRiskColor(device.toxinUgL);
  const isHighRisk = device.toxinUgL > 5;
  const label = device.deviceName.includes('浮标') ? '浮标' : device.deviceName.includes('探针') ? '探针' : '设备';

  return (
    <div ref={setNodeRef} style={{ ...style, filter: device.status === 'offline' ? 'grayscale(35%)' : 'none' }}
      className={`aqua-card p-4 flex flex-col relative ${isHighRisk ? '!border-[rgba(255,59,48,0.2)]' : ''}`}>
      {/* Drag handle */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 w-10 h-1 rounded-full bg-[rgba(45,124,255,0.10)] hover:bg-[rgba(45,124,255,0.22)] cursor-grab active:cursor-grabbing z-20" {...attributes} {...listeners} />

      {/* Header */}
      <div className="flex items-start gap-3 mt-1.5 mb-4">
        <ImagePlaceholder width={44} height={44} label={label} variant="device" />
        <div className="flex-1 min-w-0">
          <h3 className="text-[14px] font-bold text-[var(--color-text)] truncate">{device.deviceName}</h3>
          <div className="flex items-center gap-2 mt-1"><StatusBadge status={device.status} /><span className="text-[11px] text-[var(--color-muted)]">{device.updatedAt}</span></div>
        </div>
        <div className="flex-shrink-0 mt-1">
          {device.connectionType === 'wifi' && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1db954" strokeWidth="2"><path d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" /></svg>}
          {device.connectionType === 'bluetooth' && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2d7cff" strokeWidth="2"><path d="M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7" /></svg>}
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        {[
          ['藻毒素', device.toxinUgL.toFixed(2), 'μg/L', riskColor],
          ['水温', device.waterTempC.toFixed(1), '°C', 'var(--color-text)'],
          ['pH', device.ph.toFixed(1), '', 'var(--color-text)'],
        ].map(([label, value, unit, color]) => (
          <div key={label} className="text-center p-2 rounded-2xl bg-[rgba(45,124,255,0.03)]">
            <p className="text-[9px] text-[var(--color-muted)] font-semibold uppercase tracking-wider">{label}</p>
            <p className="text-[16px] font-extrabold mt-0.5" style={{ color }}>
              {value}{unit && <span className="text-[9px] ml-0.5 font-normal text-[var(--color-muted)]">{unit}</span>}
            </p>
          </div>
        ))}
      </div>

      {/* Battery / Signal */}
      <div className="flex items-center justify-between text-[11px] mb-3 px-1">
        <span className={`font-semibold ${device.battery < 20 ? 'text-[#ff3b30]' : 'text-[var(--color-muted)]'}`}>电量 {device.battery}%</span>
        <span className={`font-semibold ${device.signalDbm < -85 ? 'text-[#ffb400]' : 'text-[var(--color-muted)]'}`}>信号 {getSignalLabel(device.signalDbm)}</span>
      </div>

      {/* Actions */}
      <div className="mt-auto flex items-center gap-1.5">
        {device.status === 'offline' ? (
          <>
            <button type="button" onClick={() => onConnect('bluetooth')}
              className="flex-1 flex items-center justify-center gap-1 py-2 rounded-full border border-[var(--color-border)] bg-[rgba(45,124,255,0.03)] text-[11px] font-semibold text-[#2d7cff] hover:bg-[rgba(45,124,255,0.08)] transition-colors">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7" /></svg>蓝牙
            </button>
            <button type="button" onClick={() => onConnect('wifi')}
              className="flex-1 flex items-center justify-center gap-1 py-2 rounded-full border border-[rgba(29,185,84,0.2)] bg-[rgba(29,185,84,0.03)] text-[11px] font-semibold text-[#1db954] hover:bg-[rgba(29,185,84,0.08)] transition-colors">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" /></svg>WiFi
            </button>
          </>
        ) : (
          <>
            <AppButton variant="secondary" onClick={onDetails} className="flex-1 text-[11px] py-2">详情</AppButton>
            <button type="button" onClick={onEdit} className="p-2 rounded-full border border-[var(--color-border)] bg-white text-[var(--color-muted)] hover:text-[#2d7cff] hover:border-[#2d7cff] transition-colors" aria-label="编辑">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" /></svg>
            </button>
            <button type="button" onClick={onDelete} className="p-2 rounded-full border border-[rgba(255,59,48,0.2)] bg-white text-[#ff3b30] hover:bg-[rgba(255,59,48,0.04)] transition-colors" aria-label="删除">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
            {device.connectionType !== 'none' && (
              <button type="button" onClick={onDisconnect}
                className="ml-auto py-2 px-3 rounded-full border border-[rgba(255,59,48,0.2)] bg-[rgba(255,59,48,0.03)] text-[11px] font-semibold text-[#ff3b30] hover:bg-[rgba(255,59,48,0.08)] transition-colors">
                断开
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
