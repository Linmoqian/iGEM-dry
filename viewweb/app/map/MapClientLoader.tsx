'use client';

import dynamic from 'next/dynamic';
import { DeviceReading } from '../lib/demoReadings';

const MonitoringMap = dynamic(() => import('./MonitoringMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-[#050714] text-cyan-100">
      <span className="text-sm font-bold tracking-[0.2em] uppercase animate-pulse">地图加载中...</span>
    </div>
  ),
});

interface MapClientLoaderProps {
  readings: DeviceReading[];
  selectedDeviceId?: string | null;
  onSelectDevice?: (deviceId: string) => void;
}

export default function MapClientLoader({
  readings,
  selectedDeviceId,
  onSelectDevice,
}: MapClientLoaderProps) {
  return (
    <MonitoringMap
      readings={readings}
      selectedDeviceId={selectedDeviceId}
      onSelectDevice={onSelectDevice}
    />
  );
}
