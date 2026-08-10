import { demoDeviceHistory, demoSummary } from '../data/demoReadings';
import { generatePredictions } from '../data/mockPredictions';
import type { DemoSummary, DeviceHistoryPoint, DeviceReading, PredictionPoint, TrendPoint } from '../types/domain';
import { request } from './apiClient';
import { mockDelay, serviceConfig } from './config';
import { getMockDevices } from './mockStore';

function createSummary(devices: DeviceReading[]): DemoSummary {
  const maxToxinReading = devices.reduce<DeviceReading | null>(
    (maximum, item) => (!maximum || item.toxinUgL > maximum.toxinUgL ? item : maximum),
    null,
  );
  const active = devices.filter((device) => device.status !== 'offline');
  return {
    totalDevices: devices.length,
    onlineDevices: devices.filter((device) => device.status === 'online').length,
    idleDevices: devices.filter((device) => device.status === 'idle').length,
    offlineDevices: devices.filter((device) => device.status === 'offline').length,
    lowBatteryDevices: devices.filter((device) => device.batteryPercent < 20).length,
    weakSignalDevices: devices.filter((device) => device.signalDbm < -85).length,
    averageToxinUgL: active.length
      ? active.reduce((sum, device) => sum + device.toxinUgL, 0) / active.length
      : demoSummary.averageToxinUgL,
    maxToxinReading,
  };
}

export const monitoringService = {
  async getLatestReadings(): Promise<DeviceReading[]> {
    if (!serviceConfig.useMocks) return request<DeviceReading[]>('/readings/latest');
    await mockDelay();
    return getMockDevices();
  },

  async getDashboardSummary(): Promise<DemoSummary> {
    if (!serviceConfig.useMocks) return request<DemoSummary>('/dashboard/summary');
    await mockDelay(120);
    return createSummary(getMockDevices());
  },

  async getDeviceHistory(deviceId: string): Promise<DeviceHistoryPoint[]> {
    if (!serviceConfig.useMocks) return request<DeviceHistoryPoint[]>(`/devices/${encodeURIComponent(deviceId)}/history`);
    await mockDelay(120);
    const fallback = demoDeviceHistory[Object.keys(demoDeviceHistory)[0]];
    return (demoDeviceHistory[deviceId] || fallback).map((point) => ({ ...point }));
  },

  async getTrends(deviceId?: string): Promise<TrendPoint[]> {
    if (!serviceConfig.useMocks) {
      const query = deviceId ? `?deviceId=${encodeURIComponent(deviceId)}` : '';
      return request<TrendPoint[]>(`/analytics/trends${query}`);
    }
    const history = await this.getDeviceHistory(deviceId || 'aq-006');
    return history.flatMap((point, index) => [
      {
        time: point.time.slice(5, 10),
        toxinUgL: point.toxinUgL,
        waterTempC: point.waterTempC,
        ph: point.ph,
      },
      ...(index < history.length - 1
        ? [{
            time: `${point.time.slice(5, 10)} 午后`,
            toxinUgL: +(point.toxinUgL * (0.9 + (index % 3) * 0.08)).toFixed(2),
            waterTempC: +(point.waterTempC + 0.7).toFixed(1),
            ph: +(point.ph + 0.1).toFixed(1),
          }]
        : []),
    ]);
  },

  async getPredictions(days = 7): Promise<PredictionPoint[]> {
    if (!serviceConfig.useMocks) {
      return request<PredictionPoint[]>('/predict', {
        method: 'POST',
        body: JSON.stringify({ region: 'east-lake', forecastDays: days }),
      });
    }
    await mockDelay(140);
    const points = generatePredictions();
    const historyCount = points.filter((point) => !point.isPrediction).length;
    return points.slice(0, Math.min(points.length, historyCount + days));
  },
};
