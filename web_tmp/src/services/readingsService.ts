import { demoReadings, demoSummary, demoDeviceHistory, getDeviceHistory, getLatestReading } from '@/data/demoReadings';
import type { DeviceReading, DeviceHistoryPoint, AlertSummaryData } from '@/types/domain';
import { getRiskLevel } from '@/utils/risk';

export async function fetchAllReadings(): Promise<DeviceReading[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve([...demoReadings]), 100);
  });
}

export async function fetchLatestReading(deviceId: string): Promise<DeviceReading | undefined> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(getLatestReading(deviceId)), 50);
  });
}

export async function fetchDeviceHistory(deviceId: string): Promise<DeviceHistoryPoint[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(getDeviceHistory(deviceId)), 80);
  });
}

export async function fetchDemoSummary() {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ ...demoSummary }), 60);
  });
}

export async function fetchAlertSummary(): Promise<AlertSummaryData> {
  return new Promise((resolve) => {
    const criticalCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'critical').length;
    const warningCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'warning').length;
    const watchCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'watch').length;
    const offlineCount = demoReadings.filter((r) => r.status === 'offline').length;
    setTimeout(() => resolve({ criticalCount, warningCount, watchCount, offlineCount }), 60);
  });
}

export { demoReadings, demoSummary, demoDeviceHistory };
