import type { DeviceItem, DiscoveredDevice } from '@/types/domain';
import { demoReadings } from '@/data/demoReadings';

export async function fetchDevices(): Promise<DeviceItem[]> {
  return new Promise((resolve) => {
    const devices: DeviceItem[] = demoReadings.map((r) => ({
      id: r.id,
      deviceName: r.name,
      status: r.status,
      location: r.locationLabel,
      battery: r.batteryPercent,
      signalDbm: r.signalDbm,
      toxinUgL: r.toxinUgL,
      waterTempC: r.waterTempC,
      ph: r.ph,
      updatedAt: r.updatedAt,
      connectionType: r.connectionType,
    }));
    setTimeout(() => resolve(devices), 80);
  });
}

export async function scanDevices(): Promise<DiscoveredDevice[]> {
  return new Promise((resolve) => {
    const discovered: DiscoveredDevice[] = [
      { name: 'WaterProbe-7F2A', rssi: -48, type: 'bluetooth' },
      { name: 'Buoy-3C91', rssi: -62, type: 'wifi' },
    ];
    setTimeout(() => resolve(discovered), 2000);
  });
}
