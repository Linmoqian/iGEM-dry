import type {
  ConnectionType,
  DemoSummary,
  DeviceHistoryPoint,
  DeviceReading,
  DeviceStatus,
  RiskLevel,
} from '../types/domain';

export type { ConnectionType, DemoSummary, DeviceHistoryPoint, DeviceReading, DeviceStatus, RiskLevel };

export const demoLake = {
  name: '东湖监测区域',
  center: [30.5667, 114.3833] as [number, number],
  bounds: [
    [30.52, 114.33],
    [30.62, 114.44],
  ] as [[number, number], [number, number]],
  description:
    '武汉东湖重点水域藻毒素风险模拟监测区，覆盖湖心区、入水口、岸线浅水区、排水口与生态湿地等采样点。',
};

export const demoReadings: DeviceReading[] = [
  {
    id: 'aq-006',
    name: '藻华预警浮标-06',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖湖心区',
    lat: 30.5699,
    lng: 114.3864,
    batteryPercent: 86,
    signalDbm: -61,
    toxinUgL: 6.35,
    waterTempC: 24.8,
    ph: 7.4,
    updatedAt: '2025-05-27 09:42',
  },
  {
    id: 'aq-002',
    name: '入水口探针-02',
    status: 'idle',
    connectionType: 'bluetooth',
    locationLabel: '北侧入水口',
    lat: 30.5712,
    lng: 114.3756,
    batteryPercent: 63,
    signalDbm: -74,
    toxinUgL: 1.36,
    waterTempC: 25.5,
    ph: 7.1,
    updatedAt: '2025-05-27 09:40',
  },
  {
    id: 'aq-003',
    name: '岸线巡检锚-03',
    status: 'idle',
    connectionType: 'wifi',
    locationLabel: '西侧岸线浅水区',
    lat: 30.5598,
    lng: 114.3703,
    batteryPercent: 38,
    signalDbm: -83,
    toxinUgL: 0.78,
    waterTempC: 26.1,
    ph: 7.6,
    updatedAt: '2025-05-27 09:33',
  },
  {
    id: 'aq-001',
    name: '湖心浮标-01',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖湖心区',
    lat: 30.5667,
    lng: 114.3833,
    batteryPercent: 86,
    signalDbm: -61,
    toxinUgL: 0.42,
    waterTempC: 24.8,
    ph: 7.4,
    updatedAt: '2025-05-27 09:32',
  },
  {
    id: 'aq-004',
    name: '排水口监测-04',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '后湖排水口',
    lat: 30.5776,
    lng: 114.392,
    batteryPercent: 55,
    signalDbm: -72,
    toxinUgL: 1.05,
    waterTempC: 25.0,
    ph: 7.2,
    updatedAt: '2025-05-27 09:21',
  },
  {
    id: 'aq-005',
    name: '老旧探针-05',
    status: 'offline',
    connectionType: 'none',
    locationLabel: '废弃监测点',
    lat: 30.554,
    lng: 114.401,
    batteryPercent: 9,
    signalDbm: -98,
    toxinUgL: 0,
    waterTempC: 0,
    ph: 0,
    updatedAt: '2025-05-26 18:00',
  },
  {
    id: 'aq-007',
    name: '岸线巡检锚-07',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖东南角',
    lat: 30.558,
    lng: 114.3948,
    batteryPercent: 72,
    signalDbm: -67,
    toxinUgL: 0.55,
    waterTempC: 25.8,
    ph: 7.3,
    updatedAt: '2025-05-27 09:28',
  },
  {
    id: 'aq-008',
    name: '湖心浮标-08',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖湖心区',
    lat: 30.565,
    lng: 114.38,
    batteryPercent: 91,
    signalDbm: -56,
    toxinUgL: 0.60,
    waterTempC: 24.5,
    ph: 7.5,
    updatedAt: '2025-05-27 09:45',
  },
  {
    id: 'aq-009',
    name: '入水口探针-09',
    status: 'offline',
    connectionType: 'none',
    locationLabel: '西侧入水口',
    lat: 30.5615,
    lng: 114.365,
    batteryPercent: 14,
    signalDbm: -105,
    toxinUgL: 0,
    waterTempC: 0,
    ph: 0,
    updatedAt: '2025-05-24 12:00',
  },
  {
    id: 'aq-010',
    name: '湖心浮标-10',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖湖心区',
    lat: 30.568,
    lng: 114.385,
    batteryPercent: 78,
    signalDbm: -63,
    toxinUgL: 1.10,
    waterTempC: 25.2,
    ph: 7.0,
    updatedAt: '2025-05-27 09:38',
  },
  {
    id: 'aq-011',
    name: '岸线巡检锚-11',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '南侧岸线',
    lat: 30.5535,
    lng: 114.382,
    batteryPercent: 67,
    signalDbm: -70,
    toxinUgL: 0.90,
    waterTempC: 26.4,
    ph: 7.8,
    updatedAt: '2025-05-27 09:30',
  },
  {
    id: 'aq-012',
    name: '排水口监测-12',
    status: 'idle',
    connectionType: 'bluetooth',
    locationLabel: '东侧排水口',
    lat: 30.574,
    lng: 114.4,
    batteryPercent: 44,
    signalDbm: -79,
    toxinUgL: 4.20,
    waterTempC: 25.1,
    ph: 6.9,
    updatedAt: '2025-05-27 09:15',
  },
  {
    id: 'aq-013',
    name: '湿地入口-13',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东南湿地',
    lat: 30.548,
    lng: 114.39,
    batteryPercent: 93,
    signalDbm: -52,
    toxinUgL: 0.22,
    waterTempC: 23.9,
    ph: 7.7,
    updatedAt: '2025-05-27 09:48',
  },
  {
    id: 'aq-014',
    name: '湖心浮标-14',
    status: 'offline',
    connectionType: 'none',
    locationLabel: '北部浅滩',
    lat: 30.578,
    lng: 114.378,
    batteryPercent: 0,
    signalDbm: -110,
    toxinUgL: 0,
    waterTempC: 0,
    ph: 0,
    updatedAt: '2025-05-23 06:00',
  },
];

const dailyToxin = [1.5, 1.9, 2.6, 5.2, 2.6, 3.3, 2.1, 3.3];
const dayLabels = ['2025-05-20', '2025-05-21', '2025-05-22', '2025-05-23', '2025-05-24', '2025-05-25', '2025-05-26', '2025-05-27'];

function buildHistory(deviceId: string): DeviceHistoryPoint[] {
  const reading = demoReadings.find((r) => r.id === deviceId) ?? demoReadings[0];
  const severityBoost = reading.toxinUgL > 5 ? 1.4 : reading.toxinUgL >= 1 ? 0.35 : -0.15;

  return dayLabels.map((day, index) => {
    const toxinUgL = Math.max(0.08, +(dailyToxin[index] + severityBoost + Math.sin(index * 1.7) * 0.16).toFixed(2));
    return {
      time: `${day} 09:40`,
      toxinUgL,
      waterTempC: +(22 + index * 0.72 + Math.sin(index * 1.5) * 1.2 + (reading.status === 'idle' ? 0.4 : 0)).toFixed(1),
      ph: +(7.1 + Math.sin(index * 0.85) * 0.45 + (reading.ph - 7.3) * 0.12).toFixed(1),
      batteryPercent: Math.max(0, reading.batteryPercent - Math.max(0, 7 - index)),
      signalDbm: reading.signalDbm + Math.round(Math.cos(index) * 3),
    };
  });
}

export const demoDeviceHistory: Record<string, DeviceHistoryPoint[]> = {};
demoReadings.forEach((reading) => {
  demoDeviceHistory[reading.id] = buildHistory(reading.id);
});

export const demoSummary: DemoSummary = {
  totalDevices: demoReadings.length,
  onlineDevices: demoReadings.filter((r) => r.status === 'online').length,
  idleDevices: demoReadings.filter((r) => r.status === 'idle').length,
  offlineDevices: demoReadings.filter((r) => r.status === 'offline').length,
  lowBatteryDevices: demoReadings.filter((r) => r.batteryPercent < 20).length,
  weakSignalDevices: demoReadings.filter((r) => r.signalDbm < -85).length,
  averageToxinUgL: 2.5,
  maxToxinReading: demoReadings.reduce((max, reading) => (reading.toxinUgL > (max?.toxinUgL ?? 0) ? reading : max), null as DeviceReading | null),
};

export function getDeviceHistory(id: string): DeviceHistoryPoint[] {
  return demoDeviceHistory[id] ?? [];
}

export function getLatestReading(id: string): DeviceReading | undefined {
  return demoReadings.find((reading) => reading.id === id);
}

export function getRiskLevel(value: number): RiskLevel {
  if (value > 5) return 'critical';
  if (value >= 1) return 'warning';
  if (value >= 0.5) return 'watch';
  return 'normal';
}

export function getRiskLabel(value: number): string {
  const labels: Record<RiskLevel, string> = {
    normal: '正常',
    watch: '关注',
    warning: '警戒',
    critical: '高风险',
  };
  return labels[getRiskLevel(value)];
}

export function getRiskColor(value: number): string {
  const colors: Record<RiskLevel, string> = {
    normal: '#059669',
    watch: '#f59e0b',
    warning: '#f97316',
    critical: '#ef1919',
  };
  return colors[getRiskLevel(value)];
}

export function getSignalLabel(value: number): string {
  if (value >= -70) return '良好';
  if (value >= -85) return '一般';
  return '弱信号';
}

export function getStatusText(status: DeviceStatus): string {
  const labels: Record<DeviceStatus, string> = {
    online: '在线',
    idle: '待机',
    offline: '离线',
  };
  return labels[status];
}
