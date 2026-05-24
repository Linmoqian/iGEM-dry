import AquaPanel from '@/components/common/AquaPanel';
import AppButton from '@/components/common/AppButton';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';
import DiscoveredDeviceItem from './DiscoveredDeviceItem';
import type { DiscoveredDevice } from '@/types/domain';

interface P { isScanning: boolean; scanDone: boolean; discoveredDevices: DiscoveredDevice[]; onStartScan: () => void; onPair: (d: DiscoveredDevice) => void; }

export default function PairingPanel({ isScanning, scanDone, discoveredDevices, onStartScan, onPair }: P) {
  return (
    <AquaPanel title="添加新设备">
      <div className="flex flex-col gap-5">
        <div className="flex justify-center">
          <div className="relative w-[120px] h-[120px] flex items-center justify-center">
            <div className="absolute inset-0 rounded-full border border-[rgba(45,124,255,0.06)]" />
            <div className="absolute inset-3 rounded-full border border-[rgba(45,124,255,0.08)]" />
            <div className="absolute inset-6 rounded-full border border-[rgba(45,124,255,0.12)]" />
            {isScanning && <div className="absolute inset-0 rounded-full border-2 border-[rgba(45,124,255,0.25)] animate-ping" />}
            <div className="w-10 h-10 rounded-2xl bg-[rgba(45,124,255,0.08)] flex items-center justify-center z-10">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2d7cff" strokeWidth="2"><path d="M12 2v20M12 2l4.5 5.5L12 12l-4.5 5.5L12 22M12 12l4.5-5.5L12 2M12 12H7" /></svg>
            </div>
          </div>
        </div>
        <p className="text-[12px] text-center text-[var(--color-muted)]">{isScanning ? '扫描附近设备...' : '扫描附近设备'}</p>
        {!isScanning && <AppButton onClick={onStartScan} className="w-full">{scanDone ? '重新扫描' : '开始扫描'}</AppButton>}
        {scanDone && discoveredDevices.length > 0 && (
          <div>
            <p className="text-[12px] font-bold text-[var(--color-text)] mb-3">已发现设备（{discoveredDevices.length}）</p>
            <div className="flex flex-col gap-2.5">{discoveredDevices.map((d) => <DiscoveredDeviceItem key={d.name} device={d} onPair={() => onPair(d)} />)}</div>
          </div>
        )}
        <ImagePlaceholder width={100} height={120} label="实验器材占位" variant="decoration" className="mx-auto" />
      </div>
    </AquaPanel>
  );
}
