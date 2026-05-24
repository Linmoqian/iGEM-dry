import AppButton from '@/components/common/AppButton';
import type { DiscoveredDevice } from '@/types/domain';

interface P { device: DiscoveredDevice; onPair: () => void; }

export default function DiscoveredDeviceItem({ device, onPair }: P) {
  return (
    <div className="aqua-card p-3 flex items-center justify-between">
      <div>
        <p className="text-[13px] font-semibold text-[var(--color-text)]">{device.name}</p>
        <p className="text-[11px] text-[var(--color-muted)] mt-0.5">RSSI {device.rssi} dBm</p>
      </div>
      <AppButton variant="secondary" onClick={onPair}>
        {device.type === 'bluetooth' ? '蓝牙配对' : 'WiFi连接'}
      </AppButton>
    </div>
  );
}
