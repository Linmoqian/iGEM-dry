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

export interface DemoSummary {
  totalDevices: number;
  onlineDevices: number;
  idleDevices: number;
  offlineDevices: number;
  lowBatteryDevices: number;
  weakSignalDevices: number;
  averageToxinUgL: number;
  maxToxinReading: DeviceReading | null;
}

export interface PredictionPoint {
  time: string;
  value: number;
  upperBound: number;
  lowerBound: number;
  isPrediction: boolean;
}
