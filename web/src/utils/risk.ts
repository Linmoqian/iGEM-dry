import type { RiskLevel, DeviceStatus } from '../types/domain';

// ── Risk level thresholds ──
export function getRiskLevel(toxin: number): RiskLevel {
  if (toxin > 5) return 'danger';
  if (toxin >= 1) return 'warning';
  if (toxin >= 0.5) return 'attention';
  return 'normal';
}

export function getRiskLabel(toxin: number): string {
  const labels: Record<RiskLevel, string> = {
    normal: '正常',
    attention: '关注',
    warning: '警戒',
    danger: '高风险',
  };
  return labels[getRiskLevel(toxin)];
}

export function getRiskColor(toxin: number): string {
  const colors: Record<RiskLevel, string> = {
    normal: '#22c55e',
    attention: '#f59e0b',
    warning: '#f97316',
    danger: '#ef4444',
  };
  return colors[getRiskLevel(toxin)];
}

// ── Status mapping ──
export function getStatusText(status: DeviceStatus): string {
  const labels: Record<DeviceStatus, string> = {
    online: '在线',
    idle: '待机',
    offline: '离线',
  };
  return labels[status];
}

export function getStatusColor(status: DeviceStatus): string {
  const colors: Record<DeviceStatus, string> = {
    online: '#22c55e',
    idle: '#f59e0b',
    offline: '#94a3b8',
  };
  return colors[status];
}

// ── Signal strength ──
export function getSignalLabel(signalDbm: number): string {
  if (signalDbm >= -70) return '良好';
  if (signalDbm >= -85) return '一般';
  return '弱信号';
}

// ── Heatmap normalization (0.12 - 1.0) ──
export function normalizeHeatValue(toxin: number): number {
  return Math.min(1, Math.max(0.12, toxin / 6.5));
}
