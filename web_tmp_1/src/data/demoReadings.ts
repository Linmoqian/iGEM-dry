import type { DeviceReading, DeviceHistoryPoint, DemoSummary, DeviceStatus, ConnectionType, RiskLevel } from '../types/domain';

export type { DeviceReading, DeviceHistoryPoint, DemoSummary, DeviceStatus, ConnectionType, RiskLevel };

export const demoLake = {
  name: '东湖监测区',
  center: [30.5667, 114.3833] as [number, number],
  bounds: [[30.52, 114.33], [30.62, 114.44]] as [[number, number], [number, number]],
  description: '武汉东湖 — 全国最大的城中湖之一，面积约33平方公里，平均水深2.5米。该监测区域覆盖湖心区、北侧入水口、西侧岸线、后湖排水口等12个关键采样点。',
};

export const demoReadings: DeviceReading[] = [
  { id: 'aq-001', name: '湖心浮标-01', status: 'online', connectionType: 'wifi', locationLabel: '东湖湖心区', lat: 30.5667, lng: 114.3833, batteryPercent: 86, signalDbm: -61, toxinUgL: 0.42, waterTempC: 24.8, ph: 7.4, updatedAt: '2025-05-27 09:32' },
  { id: 'aq-002', name: '入水口探针-02', status: 'idle', connectionType: 'bluetooth', locationLabel: '北侧入水口', lat: 30.5712, lng: 114.3756, batteryPercent: 63, signalDbm: -74, toxinUgL: 1.36, waterTempC: 25.5, ph: 7.1, updatedAt: '2025-05-27 09:40' },
  { id: 'aq-003', name: '岸线巡检猫-03', status: 'online', connectionType: 'wifi', locationLabel: '西侧岸线浅水区', lat: 30.5598, lng: 114.3703, batteryPercent: 38, signalDbm: -83, toxinUgL: 0.78, waterTempC: 26.1, ph: 7.6, updatedAt: '2025-05-27 09:33' },
  { id: 'aq-004', name: '排水口监测-04', status: 'idle', connectionType: 'bluetooth', locationLabel: '后湖排水口', lat: 30.5776, lng: 114.3920, batteryPercent: 55, signalDbm: -72, toxinUgL: 1.05, waterTempC: 25.0, ph: 7.2, updatedAt: '2025-05-27 09:21' },
  { id: 'aq-005', name: '老旧探针-05', status: 'offline', connectionType: 'none', locationLabel: '废弃监测点', lat: 30.5540, lng: 114.4010, batteryPercent: 9, signalDbm: -98, toxinUgL: 0, waterTempC: 0, ph: 0, updatedAt: '2025-05-26 18:00' },
  { id: 'aq-006', name: '藻华预警浮标-06', status: 'online', connectionType: 'wifi', locationLabel: '东湖湖心区', lat: 30.5699, lng: 114.3864, batteryPercent: 86, signalDbm: -61, toxinUgL: 6.35, waterTempC: 24.8, ph: 7.4, updatedAt: '2025-05-27 09:42' },
  { id: 'aq-007', name: '岸线巡检猫-07', status: 'online', connectionType: 'wifi', locationLabel: '东湖东南角', lat: 30.5580, lng: 114.3948, batteryPercent: 72, signalDbm: -67, toxinUgL: 0.55, waterTempC: 25.8, ph: 7.3, updatedAt: '2025-05-27 09:28' },
  { id: 'aq-008', name: '湖心浮标-08', status: 'online', connectionType: 'wifi', locationLabel: '东湖湖心区', lat: 30.5650, lng: 114.3800, batteryPercent: 91, signalDbm: -56, toxinUgL: 0.60, waterTempC: 24.5, ph: 7.5, updatedAt: '2025-05-27 09:45' },
  { id: 'aq-009', name: '入水口探针-09', status: 'offline', connectionType: 'none', locationLabel: '西侧入水口', lat: 30.5615, lng: 114.3650, batteryPercent: 14, signalDbm: -105, toxinUgL: 0, waterTempC: 0, ph: 0, updatedAt: '2025-05-24 12:00' },
  { id: 'aq-010', name: '湖心浮标-10', status: 'online', connectionType: 'wifi', locationLabel: '东湖湖心区', lat: 30.5680, lng: 114.3850, batteryPercent: 78, signalDbm: -63, toxinUgL: 1.10, waterTempC: 25.2, ph: 7.0, updatedAt: '2025-05-27 09:38' },
  { id: 'aq-011', name: '岸线巡检猫-11', status: 'online', connectionType: 'wifi', locationLabel: '南侧岸线', lat: 30.5535, lng: 114.3820, batteryPercent: 67, signalDbm: -70, toxinUgL: 0.90, waterTempC: 26.4, ph: 7.8, updatedAt: '2025-05-27 09:30' },
  { id: 'aq-012', name: '排水口监测-12', status: 'idle', connectionType: 'bluetooth', locationLabel: '东侧排水口', lat: 30.5740, lng: 114.4000, batteryPercent: 44, signalDbm: -79, toxinUgL: 4.20, waterTempC: 25.1, ph: 6.9, updatedAt: '2025-05-27 09:15' },
  { id: 'aq-013', name: '湿地入口-13', status: 'online', connectionType: 'wifi', locationLabel: '东南湿地', lat: 30.5480, lng: 114.3900, batteryPercent: 93, signalDbm: -52, toxinUgL: 0.22, waterTempC: 23.9, ph: 7.7, updatedAt: '2025-05-27 09:48' },
  { id: 'aq-014', name: '湖心浮标-14', status: 'offline', connectionType: 'none', locationLabel: '北部浅滩', lat: 30.5780, lng: 114.3780, batteryPercent: 0, signalDbm: -110, toxinUgL: 0, waterTempC: 0, ph: 0, updatedAt: '2025-05-23 06:00' },
];

function buildHistory(deviceId: string): DeviceHistoryPoint[] {
  const points: DeviceHistoryPoint[] = [];
  const reading = demoReadings.find((r) => r.id === deviceId);
  const baseToxin = reading?.toxinUgL ?? 1.0;
  const baseTemp = reading?.waterTempC ?? 25.0;
  const basePh = reading?.ph ?? 7.2;
  const baseBatt = reading?.batteryPercent ?? 70;
  const baseSignal = reading?.signalDbm ?? -70;
  const now = new Date('2025-05-27T10:00:00');
  for (let i = 23; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 3600000);
    const hourFraction = t.getHours() / 24;
    const diurnal = Math.sin(hourFraction * Math.PI * 2) * 0.3;
    const noise = (Math.random() - 0.5) * 0.2;
    points.push({
      time: t.toISOString().replace('T', ' ').slice(0, 16),
      toxinUgL: Math.max(0.05, +(baseToxin + diurnal + noise).toFixed(2)),
      waterTempC: Math.min(34, Math.max(18, +(baseTemp + diurnal * 1.5 + noise).toFixed(1))),
      ph: Math.min(8.8, Math.max(6.4, +(basePh + noise * 0.2).toFixed(1))),
      batteryPercent: Math.min(100, Math.max(0, Math.round(baseBatt - i * 0.3 + (Math.random() - 0.5) * 2))),
      signalDbm: Math.min(-45, Math.max(-105, Math.round(baseSignal + (Math.random() - 0.5) * 6))),
    });
  }
  return points;
}

export const demoDeviceHistory: Record<string, DeviceHistoryPoint[]> = {};
demoReadings.forEach((r) => {
  demoDeviceHistory[r.id] = buildHistory(r.id);
});

export const demoSummary: DemoSummary = {
  totalDevices: demoReadings.length,
  onlineDevices: demoReadings.filter((r) => r.status === 'online').length,
  idleDevices: demoReadings.filter((r) => r.status === 'idle').length,
  offlineDevices: demoReadings.filter((r) => r.status === 'offline').length,
  lowBatteryDevices: demoReadings.filter((r) => r.batteryPercent < 20).length,
  weakSignalDevices: demoReadings.filter((r) => r.signalDbm < -85).length,
  averageToxinUgL: +((demoReadings.filter((r) => r.status !== 'offline').reduce((s, r) => s + r.toxinUgL, 0) / demoReadings.filter((r) => r.status !== 'offline').length) || 0).toFixed(2),
  maxToxinReading: demoReadings.reduce((max, r) => (r.toxinUgL > (max?.toxinUgL ?? 0) ? r : max), null as DeviceReading | null),
};

export function getDeviceHistory(id: string): DeviceHistoryPoint[] {
  return demoDeviceHistory[id] ?? [];
}

export function getLatestReading(id: string): DeviceReading | undefined {
  return demoReadings.find((r) => r.id === id);
}

export function getRiskLevel(v: number): RiskLevel {
  if (v > 5) return 'critical';
  if (v >= 1) return 'warning';
  if (v >= 0.5) return 'watch';
  return 'normal';
}

export function getRiskLabel(v: number): string {
  const map: Record<RiskLevel, string> = { normal: '正常', watch: '关注', warning: '警戒', critical: '高风险' };
  return map[getRiskLevel(v)];
}

export function getRiskColor(v: number): string {
  const map: Record<RiskLevel, string> = { normal: '#22C55E', watch: '#F59E0B', warning: '#FF7A00', critical: '#EF4444' };
  return map[getRiskLevel(v)];
}

export function getSignalLabel(v: number): string {
  if (v >= -70) return '良好';
  if (v >= -85) return '一般';
  return '弱信号';
}

export function getStatusText(s: DeviceStatus): string {
  const map: Record<DeviceStatus, string> = { online: '在线采样', idle: '待机', offline: '离线' };
  return map[s];
}
