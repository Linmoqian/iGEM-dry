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

export interface DiscoveredDevice {
  id: string;
  name: string;
  connectionType: Exclude<ConnectionType, 'none'>;
  signalDbm: number;
  paired: boolean;
}

export interface DeviceInput {
  name: string;
  connectionType: Exclude<ConnectionType, 'none'>;
  locationLabel: string;
  lat?: number;
  lng?: number;
}

export interface TrendPoint {
  time: string;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
}

export interface ApiEnvelope<T> {
  data: T;
  timestamp: string;
  requestId?: string;
}

export interface RealtimeEvent {
  event: 'sensor_update' | 'risk_alert' | 'device_status' | 'task_status';
  timestamp: string;
  payload: unknown;
}
