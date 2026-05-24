import type { RiskLevel, DeviceStatus } from '@/types/domain';

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
    normal: '#1db954',
    watch: '#ffb400',
    warning: '#ff8a00',
    critical: '#ff3b30',
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
