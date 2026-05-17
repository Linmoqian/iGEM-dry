export type DeviceStatus = 'online' | 'offline' | 'idle';
export type ConnectionType = 'bluetooth' | 'wifi' | 'none';
export type RiskLevel = 'normal' | 'watch' | 'warning' | 'critical';

export interface DeviceReading {
  id: string;
  name: string;
  status: DeviceStatus;
  connectionType: ConnectionType;
  locationLabel: string;
  lat: number;
  lng: number;
  batteryPercent: number;
  signalDbm: number;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
  updatedAt: string;
}

export interface DeviceHistoryPoint {
  time: string;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
  batteryPercent: number;
  signalDbm: number;
}

export const demoLake = {
  name: '演示湖泊',
  description: '蓝色湖泊与绿色陆地示意水域',
  center: [30.5667, 114.3833] as [number, number],
  bounds: [
    [30.528, 114.352],
    [30.586, 114.438],
  ] as [[number, number], [number, number]],
};

export const demoReadings: DeviceReading[] = [
  {
    id: 'aq-001',
    name: '湖心浮标-01',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东湖湖心采样点',
    lat: 30.5558,
    lng: 114.3991,
    batteryPercent: 86,
    signalDbm: -61,
    toxinUgL: 0.42,
    waterTempC: 24.8,
    ph: 7.4,
    updatedAt: '09:42',
  },
  {
    id: 'aq-002',
    name: '入水口探针-02',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '北侧入水口',
    lat: 30.5632,
    lng: 114.3914,
    batteryPercent: 63,
    signalDbm: -74,
    toxinUgL: 1.36,
    waterTempC: 25.5,
    ph: 7.1,
    updatedAt: '09:40',
  },
  {
    id: 'aq-003',
    name: '岸线巡检器-03',
    status: 'idle',
    connectionType: 'bluetooth',
    locationLabel: '西南岸线浅水区',
    lat: 30.5497,
    lng: 114.3857,
    batteryPercent: 38,
    signalDbm: -83,
    toxinUgL: 0.78,
    waterTempC: 26.1,
    ph: 7.6,
    updatedAt: '09:33',
  },
  {
    id: 'aq-004',
    name: '排水口监测-04',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东南排水口',
    lat: 30.5459,
    lng: 114.4099,
    batteryPercent: 71,
    signalDbm: -69,
    toxinUgL: 4.72,
    waterTempC: 27.3,
    ph: 8.0,
    updatedAt: '09:41',
  },
  {
    id: 'aq-005',
    name: '补给站传感器-05',
    status: 'offline',
    connectionType: 'none',
    locationLabel: '南岸补给站',
    lat: 30.5418,
    lng: 114.3973,
    batteryPercent: 14,
    signalDbm: -96,
    toxinUgL: 2.18,
    waterTempC: 25.9,
    ph: 7.8,
    updatedAt: '09:12',
  },
  {
    id: 'aq-006',
    name: '藻华预警浮标-06',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东侧湾区',
    lat: 30.5572,
    lng: 114.4141,
    batteryPercent: 92,
    signalDbm: -57,
    toxinUgL: 6.35,
    waterTempC: 28.0,
    ph: 8.2,
    updatedAt: '09:43',
  },
  {
    id: 'aq-007',
    name: '西北浅滩-07',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '西北浅滩芦苇区',
    lat: 30.5668,
    lng: 114.3818,
    batteryPercent: 77,
    signalDbm: -72,
    toxinUgL: 0.64,
    waterTempC: 25.1,
    ph: 7.5,
    updatedAt: '09:39',
  },
  {
    id: 'aq-008',
    name: '北岸巡检-08',
    status: 'idle',
    connectionType: 'bluetooth',
    locationLabel: '北岸亲水平台',
    lat: 30.5701,
    lng: 114.4056,
    batteryPercent: 54,
    signalDbm: -81,
    toxinUgL: 1.92,
    waterTempC: 25.8,
    ph: 7.7,
    updatedAt: '09:31',
  },
  {
    id: 'aq-009',
    name: '东岸浮标-09',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '东岸近岸水域',
    lat: 30.5519,
    lng: 114.4215,
    batteryPercent: 89,
    signalDbm: -58,
    toxinUgL: 5.46,
    waterTempC: 28.3,
    ph: 8.3,
    updatedAt: '09:44',
  },
  {
    id: 'aq-010',
    name: '中心航线-10',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '中心巡航航线',
    lat: 30.5596,
    lng: 114.4037,
    batteryPercent: 68,
    signalDbm: -67,
    toxinUgL: 2.84,
    waterTempC: 26.9,
    ph: 7.9,
    updatedAt: '09:45',
  },
  {
    id: 'aq-011',
    name: '西岸涵洞-11',
    status: 'offline',
    connectionType: 'none',
    locationLabel: '西岸涵洞附近',
    lat: 30.5461,
    lng: 114.3749,
    batteryPercent: 9,
    signalDbm: -101,
    toxinUgL: 0.31,
    waterTempC: 24.3,
    ph: 7.3,
    updatedAt: '09:05',
  },
  {
    id: 'aq-012',
    name: '南侧湾口-12',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '南侧湾口交换区',
    lat: 30.5366,
    lng: 114.4118,
    batteryPercent: 82,
    signalDbm: -64,
    toxinUgL: 3.58,
    waterTempC: 27.1,
    ph: 8.1,
    updatedAt: '09:42',
  },
  {
    id: 'aq-013',
    name: '湿地入口-13',
    status: 'online',
    connectionType: 'wifi',
    locationLabel: '湿地净化入口',
    lat: 30.5742,
    lng: 114.3869,
    batteryPercent: 96,
    signalDbm: -55,
    toxinUgL: 0.22,
    waterTempC: 23.9,
    ph: 7.2,
    updatedAt: '09:46',
  },
  {
    id: 'aq-014',
    name: '东南暗渠-14',
    status: 'idle',
    connectionType: 'bluetooth',
    locationLabel: '东南暗渠汇入口',
    lat: 30.5394,
    lng: 114.4247,
    batteryPercent: 47,
    signalDbm: -86,
    toxinUgL: 4.18,
    waterTempC: 27.8,
    ph: 8.0,
    updatedAt: '09:28',
  },
];

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function round(value: number, digits = 2): number {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function buildHistory(reading: DeviceReading, index: number): DeviceHistoryPoint[] {
  return Array.from({ length: 24 }, (_, hour) => {
    const progress = hour / 23;
    const dailyWave = Math.sin((hour / 24) * Math.PI * 2 + index * 0.7);
    const bloomPulse = Math.max(0, Math.sin(((hour - 10 - index) / 24) * Math.PI * 2));
    const lateDrift = (progress - 0.5) * (reading.toxinUgL > 1 ? 0.55 : 0.2);
    const toxin = reading.toxinUgL * (0.72 + bloomPulse * 0.32) + dailyWave * 0.12 + lateDrift;
    const temp = reading.waterTempC - 1.3 + progress * 1.9 + dailyWave * 0.35;
    const ph = reading.ph - 0.16 + bloomPulse * 0.22 - dailyWave * 0.06;
    const battery = reading.batteryPercent + (23 - hour) * 0.42;
    const signal = reading.signalDbm + Math.sin(hour * 0.85 + index) * 3.8;

    return {
      time: `${String(hour).padStart(2, '0')}:00`,
      toxinUgL: round(clamp(toxin, 0.05, 8.5)),
      waterTempC: round(clamp(temp, 18, 34), 1),
      ph: round(clamp(ph, 6.4, 8.8), 1),
      batteryPercent: Math.round(clamp(battery, 0, 100)),
      signalDbm: Math.round(clamp(signal, -105, -45)),
    };
  });
}

export const demoDeviceHistory: Record<string, DeviceHistoryPoint[]> = Object.fromEntries(
  demoReadings.map((reading, index) => [reading.id, buildHistory(reading, index)])
);

export function getDeviceHistory(deviceId: string): DeviceHistoryPoint[] {
  return demoDeviceHistory[deviceId] ?? [];
}

export function getLatestReading(deviceId: string): DeviceReading | undefined {
  return demoReadings.find((reading) => reading.id === deviceId);
}

export function getRiskLevel(toxinUgL: number): RiskLevel {
  if (toxinUgL > 5) return 'critical';
  if (toxinUgL >= 1) return 'warning';
  if (toxinUgL >= 0.5) return 'watch';
  return 'normal';
}

export function getRiskLabel(toxinUgL: number): string {
  const labels: Record<RiskLevel, string> = {
    normal: '正常',
    watch: '关注',
    warning: '警戒',
    critical: '高风险',
  };
  return labels[getRiskLevel(toxinUgL)];
}

export function getRiskColor(toxinUgL: number): string {
  const colors: Record<RiskLevel, string> = {
    normal: '#34d399',
    watch: '#facc15',
    warning: '#fb923c',
    critical: '#f43f5e',
  };
  return colors[getRiskLevel(toxinUgL)];
}

export function getSignalLabel(signalDbm: number): string {
  if (signalDbm >= -70) return '良好';
  if (signalDbm >= -85) return '一般';
  return '弱信号';
}

export function getStatusText(status: DeviceStatus): string {
  const labels: Record<DeviceStatus, string> = {
    online: '在线采样',
    idle: '待机',
    offline: '离线',
  };
  return labels[status];
}

export function normalizeHeatValue(toxinUgL: number): number {
  return Math.min(1, Math.max(0.12, toxinUgL / 6.5));
}

export const demoSummary = {
  totalDevices: demoReadings.length,
  onlineDevices: demoReadings.filter((reading) => reading.status === 'online').length,
  lowBatteryDevices: demoReadings.filter((reading) => reading.batteryPercent < 20).length,
  weakSignalDevices: demoReadings.filter((reading) => reading.signalDbm < -85).length,
  averageToxinUgL:
    demoReadings.reduce((sum, reading) => sum + reading.toxinUgL, 0) / demoReadings.length,
  maxToxinReading: demoReadings.reduce((max, reading) =>
    reading.toxinUgL > max.toxinUgL ? reading : max
  ),
};
