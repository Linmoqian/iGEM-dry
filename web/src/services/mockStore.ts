import { demoReadings } from '../data/demoReadings';
import type { DeviceReading, DiscoveredDevice } from '../types/domain';

const STORAGE_KEY = 'igem-water-monitor-devices-v1';

function readInitialDevices(): DeviceReading[] {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    if (value) return JSON.parse(value) as DeviceReading[];
  } catch {
    // localStorage may be unavailable in private or embedded contexts.
  }
  return demoReadings.map((device) => ({ ...device }));
}

let devices = readInitialDevices();

export function getMockDevices(): DeviceReading[] {
  return devices.map((device) => ({ ...device }));
}

export function setMockDevices(nextDevices: DeviceReading[]): DeviceReading[] {
  devices = nextDevices.map((device) => ({ ...device }));
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(devices));
  } catch {
    // Keep in-memory data even when persistence is unavailable.
  }
  return getMockDevices();
}

export const mockDiscoveredDevices: DiscoveredDevice[] = [
  { id: 'scan-7f2a', name: 'WaterProbe-7F2A', connectionType: 'bluetooth', signalDbm: -48, paired: false },
  { id: 'scan-3c91', name: 'Buoy-3C91', connectionType: 'wifi', signalDbm: -62, paired: false },
];
