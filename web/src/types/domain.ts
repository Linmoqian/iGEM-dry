// ── Device status ──
export type DeviceStatus = 'online' | 'idle' | 'offline';

// ── Connection type ──
export type ConnectionType = 'bluetooth' | 'wifi' | 'none';

// ── Risk level (new naming: watch→attention, critical→danger) ──
export type RiskLevel = 'normal' | 'attention' | 'warning' | 'danger';

// ── Device type (for card illustration routing) ──
export type DeviceType = 'buoy' | 'probe' | 'sensor' | 'other';

// ── Monitoring device ──
export interface MonitoringDevice {
  id: string;
  name: string;
  type: DeviceType;
  locationName: string;
  latitude: number;
  longitude: number;
  status: DeviceStatus;
  connectionType: ConnectionType;
  battery: number;
  signalDbm: number;
  lastUpdated: string;
  note?: string;
}

// ── Device reading (latest sample per device) ──
export interface DeviceReading {
  id: string;
  deviceId: string;
  deviceName: string;
  sampledAt: string;
  toxin: number;
  waterTemp: number;
  ph: number;
  battery: number;
  signalDbm: number;
  status: DeviceStatus;
  locationName: string;
  latitude: number;
  longitude: number;
}

// ── Device history point (24h trend) ──
export interface DeviceHistoryPoint {
  time: string;
  toxin: number;
  waterTemp: number;
  ph: number;
  battery: number;
  signalDbm: number;
}

// ── Alert summary (overview page) ──
export interface AlertSummary {
  level: RiskLevel;
  label: string;
  count: number;
  deviceIds: string[];
}

// ── Trend point (7-day aggregation) ──
export interface TrendPoint {
  date: string;
  toxin: number;
  waterTemp?: number;
  ph?: number;
}

// ── Prediction point (AI forecast) ──
export interface PredictionPoint {
  date: string;
  value: number;
  isPrediction: boolean;
  upperBound?: number;
  lowerBound?: number;
}

// ── Discovered device (pairing page scan) ──
export interface DiscoveredDevice {
  id: string;
  name: string;
  rssi: number;
  connectionType: 'bluetooth' | 'wifi';
}

// ── Filter state (data analysis page) ──
export interface FilterState {
  timeRangeStart: string;
  timeRangeEnd: string;
  deviceIds: string[];
  sensors: ('toxin' | 'waterTemp' | 'ph')[];
}

// ── Device action (CRUD operations) ──
export interface DeviceAction {
  type: 'add' | 'edit' | 'delete' | 'connect' | 'disconnect' | 'sort';
  deviceId?: string;
  payload?: Partial<MonitoringDevice>;
}
