import type {
  MonitoringDevice,
  DeviceReading,
  DeviceHistoryPoint,
  DeviceType,
} from '../types/domain';
// ── Type inference from device name ──
export function inferDeviceType(name: string): DeviceType {
  if (name.includes('浮标')) return 'buoy';
  if (name.includes('探针') || name.includes('巡检器')) return 'probe';
  if (name.includes('传感器') || name.includes('监测')) return 'sensor';
  return 'other';
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

// ── 14 monitoring devices ──
export const demoDevices: MonitoringDevice[] = [
  {
    id: 'aq-001',
    name: '湖心浮标-01',
    type: 'buoy',
    locationName: '东湖湖心采样点',
    latitude: 30.5558,
    longitude: 114.3991,
    status: 'online',
    connectionType: 'wifi',
    battery: 86,
    signalDbm: -61,
    lastUpdated: '09:42',
  },
  {
    id: 'aq-002',
    name: '入水口探针-02',
    type: 'probe',
    locationName: '北侧入水口',
    latitude: 30.5632,
    longitude: 114.3914,
    status: 'online',
    connectionType: 'wifi',
    battery: 63,
    signalDbm: -74,
    lastUpdated: '09:40',
  },
  {
    id: 'aq-003',
    name: '岸线巡检器-03',
    type: 'probe',
    locationName: '西南岸线浅水区',
    latitude: 30.5497,
    longitude: 114.3857,
    status: 'idle',
    connectionType: 'bluetooth',
    battery: 38,
    signalDbm: -83,
    lastUpdated: '09:33',
  },
  {
    id: 'aq-004',
    name: '排水口监测-04',
    type: 'sensor',
    locationName: '东南排水口',
    latitude: 30.5459,
    longitude: 114.4099,
    status: 'online',
    connectionType: 'wifi',
    battery: 71,
    signalDbm: -69,
    lastUpdated: '09:41',
  },
  {
    id: 'aq-005',
    name: '补给站传感器-05',
    type: 'sensor',
    locationName: '南岸补给站',
    latitude: 30.5418,
    longitude: 114.3973,
    status: 'offline',
    connectionType: 'none',
    battery: 14,
    signalDbm: -96,
    lastUpdated: '09:12',
  },
  {
    id: 'aq-006',
    name: '藻华预警浮标-06',
    type: 'buoy',
    locationName: '东侧湾区',
    latitude: 30.5572,
    longitude: 114.4141,
    status: 'online',
    connectionType: 'wifi',
    battery: 92,
    signalDbm: -57,
    lastUpdated: '09:43',
  },
  {
    id: 'aq-007',
    name: '西北浅滩-07',
    type: 'other',
    locationName: '西北浅滩芦苇区',
    latitude: 30.5668,
    longitude: 114.3818,
    status: 'online',
    connectionType: 'wifi',
    battery: 77,
    signalDbm: -72,
    lastUpdated: '09:39',
  },
  {
    id: 'aq-008',
    name: '北岸巡检-08',
    type: 'other',
    locationName: '北岸亲水平台',
    latitude: 30.5701,
    longitude: 114.4056,
    status: 'idle',
    connectionType: 'bluetooth',
    battery: 54,
    signalDbm: -81,
    lastUpdated: '09:31',
  },
  {
    id: 'aq-009',
    name: '东岸浮标-09',
    type: 'buoy',
    locationName: '东岸近岸水域',
    latitude: 30.5519,
    longitude: 114.4215,
    status: 'online',
    connectionType: 'wifi',
    battery: 89,
    signalDbm: -58,
    lastUpdated: '09:44',
  },
  {
    id: 'aq-010',
    name: '中心航线-10',
    type: 'other',
    locationName: '中心巡航航线',
    latitude: 30.5596,
    longitude: 114.4037,
    status: 'online',
    connectionType: 'wifi',
    battery: 68,
    signalDbm: -67,
    lastUpdated: '09:45',
  },
  {
    id: 'aq-011',
    name: '西岸涵洞-11',
    type: 'other',
    locationName: '西岸涵洞附近',
    latitude: 30.5461,
    longitude: 114.3749,
    status: 'offline',
    connectionType: 'none',
    battery: 9,
    signalDbm: -101,
    lastUpdated: '09:05',
  },
  {
    id: 'aq-012',
    name: '南侧湾口-12',
    type: 'other',
    locationName: '南侧湾口交换区',
    latitude: 30.5366,
    longitude: 114.4118,
    status: 'online',
    connectionType: 'wifi',
    battery: 82,
    signalDbm: -64,
    lastUpdated: '09:42',
  },
  {
    id: 'aq-013',
    name: '湿地入口-13',
    type: 'other',
    locationName: '湿地净化入口',
    latitude: 30.5742,
    longitude: 114.3869,
    status: 'online',
    connectionType: 'wifi',
    battery: 96,
    signalDbm: -55,
    lastUpdated: '09:46',
  },
  {
    id: 'aq-014',
    name: '东南暗渠-14',
    type: 'other',
    locationName: '东南暗渠汇入口',
    latitude: 30.5394,
    longitude: 114.4247,
    status: 'idle',
    connectionType: 'bluetooth',
    battery: 47,
    signalDbm: -86,
    lastUpdated: '09:28',
  },
];

// ── Latest readings (one per device) ──
export const demoReadings: DeviceReading[] = demoDevices.map((device, index) => {
  const toxinValues = [0.42, 1.36, 0.78, 4.72, 2.18, 6.35, 0.64, 1.92, 5.46, 2.84, 0.31, 3.58, 0.22, 4.18];
  const tempValues = [24.8, 25.5, 26.1, 27.3, 25.9, 28.0, 25.1, 25.8, 28.3, 26.9, 24.3, 27.1, 23.9, 27.8];
  const phValues = [7.4, 7.1, 7.6, 8.0, 7.8, 8.2, 7.5, 7.7, 8.3, 7.9, 7.3, 8.1, 7.2, 8.0];

  return {
    id: `reading-${device.id}`,
    deviceId: device.id,
    deviceName: device.name,
    sampledAt: device.lastUpdated,
    toxin: toxinValues[index],
    waterTemp: tempValues[index],
    ph: phValues[index],
    battery: device.battery,
    signalDbm: device.signalDbm,
    status: device.status,
    locationName: device.locationName,
    latitude: device.latitude,
    longitude: device.longitude,
  };
});

// ── Helpers ──
function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function round(value: number, digits = 2): number {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

// ── 24-hour history per device ──
function buildHistory(device: MonitoringDevice, toxin: number, index: number): DeviceHistoryPoint[] {
  return Array.from({ length: 24 }, (_, hour) => {
    const progress = hour / 23;
    const dailyWave = Math.sin((hour / 24) * Math.PI * 2 + index * 0.7);
    const bloomPulse = Math.max(0, Math.sin(((hour - 10 - index) / 24) * Math.PI * 2));
    const lateDrift = (progress - 0.5) * (toxin > 1 ? 0.55 : 0.2);
    const t = toxin * (0.72 + bloomPulse * 0.32) + dailyWave * 0.12 + lateDrift;
    const temp = 25 - 1.3 + progress * 1.9 + dailyWave * 0.35;
    const ph = 7.5 - 0.16 + bloomPulse * 0.22 - dailyWave * 0.06;
    const battery = device.battery + (23 - hour) * 0.42;
    const signal = device.signalDbm + Math.sin(hour * 0.85 + index) * 3.8;

    return {
      time: `${String(hour).padStart(2, '0')}:00`,
      toxin: round(clamp(t, 0.05, 8.5)),
      waterTemp: round(clamp(temp, 18, 34), 1),
      ph: round(clamp(ph, 6.4, 8.8), 1),
      battery: Math.round(clamp(battery, 0, 100)),
      signalDbm: Math.round(clamp(signal, -105, -45)),
    };
  });
}

export const demoDeviceHistory: Record<string, DeviceHistoryPoint[]> = Object.fromEntries(
  demoDevices.map((device, i) => [device.id, buildHistory(device, demoReadings[i].toxin, i)])
);

export function getDeviceHistory(deviceId: string): DeviceHistoryPoint[] {
  return demoDeviceHistory[deviceId] ?? [];
}

export function getLatestReading(deviceId: string): DeviceReading | undefined {
  return demoReadings.find((r) => r.deviceId === deviceId);
}

export function getDevice(deviceId: string): MonitoringDevice | undefined {
  return demoDevices.find((d) => d.id === deviceId);
}

export const demoSummary = {
  totalDevices: demoDevices.length,
  onlineDevices: demoDevices.filter((d) => d.status === 'online').length,
  idleDevices: demoDevices.filter((d) => d.status === 'idle').length,
  offlineDevices: demoDevices.filter((d) => d.status === 'offline').length,
  lowBatteryDevices: demoDevices.filter((d) => d.battery < 20).length,
  weakSignalDevices: demoDevices.filter((d) => d.signalDbm < -85).length,
  averageToxin:
    round(demoReadings.reduce((sum, r) => sum + r.toxin, 0) / demoReadings.length),
  maxToxinReading: demoReadings.reduce((max, r) => (r.toxin > max.toxin ? r : max)),
};
