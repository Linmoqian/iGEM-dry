export type DeviceStatus = 'online' | 'idle' | 'offline';
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

export interface TrendPoint {
  date: string;
  toxin: number;
  maxToxin: number;
  temp: number;
  ph: number;
  isHighRisk: boolean;
}

export interface PredictionPoint {
  date: string;
  historical: number | null;
  predicted: number | null;
  upperBound: number | null;
  lowerBound: number | null;
}

export interface DiscoveredDevice {
  name: string;
  rssi: number;
  type: 'bluetooth' | 'wifi';
}

export interface FilterState {
  dateRange: string;
  device: string;
  metric: string;
}

export interface DeviceItem {
  id: string;
  deviceName: string;
  status: DeviceStatus;
  location: string;
  battery: number;
  signalDbm: number;
  toxinUgL: number;
  waterTempC: number;
  ph: number;
  updatedAt: string;
  connectionType: ConnectionType;
}

export type DeviceModalType = 'none' | 'details' | 'edit' | 'delete' | 'connecting' | 'adding';

export interface DeviceModalState {
  type: DeviceModalType;
  device?: DeviceItem;
  title?: string;
  message?: string;
  loading?: boolean;
}

export interface AlertSummaryData {
  criticalCount: number;
  warningCount: number;
  watchCount: number;
  offlineCount: number;
}
