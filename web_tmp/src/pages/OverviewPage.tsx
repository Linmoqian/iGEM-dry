import { useMemo } from 'react';
import { demoReadings, demoSummary, demoDeviceHistory } from '@/data/demoReadings';
import { getRiskLevel } from '@/utils/risk';
import { generateTrendData } from '@/utils/chart';
import MetricSummaryCard from '@/components/overview/MetricSummaryCard';
import SystemStatusPanel from '@/components/overview/SystemStatusPanel';
import AlertSummaryPanel from '@/components/overview/AlertSummaryPanel';
import OverviewTrendChart from '@/components/overview/OverviewTrendChart';
import LatestReadingsTable from '@/components/overview/LatestReadingsTable';
import type { AlertSummaryData } from '@/types/domain';

const svgI = (d: string, color: string) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d={d} /></svg>
);

export default function OverviewPage() {
  const max = demoSummary.maxToxinReading;
  const trendData = useMemo(() => generateTrendData(demoReadings, demoDeviceHistory), []);
  const alerts: AlertSummaryData = useMemo(() => {
    const criticalCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'critical').length;
    const warningCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'warning').length;
    const watchCount = demoReadings.filter((r) => getRiskLevel(r.toxinUgL) === 'watch').length;
    const offlineCount = demoReadings.filter((r) => r.status === 'offline').length;
    return { criticalCount, warningCount, watchCount, offlineCount };
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricSummaryCard label="在线设备" value={`${demoSummary.onlineDevices}`} suffix={`/ ${demoSummary.totalDevices} 台`} color="#1db954"
          icon={svgI('M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0', '#1db954')} />
        <MetricSummaryCard label="空闲设备" value={`${demoSummary.idleDevices}`} suffix={`/ ${demoSummary.totalDevices} 台`} color="#ffb400"
          icon={svgI('M12 6v6l4 2m6 12a9 9 0 11-18 0 9 9 0 0118 0z', '#ffb400')} />
        <MetricSummaryCard label="离线设备" value={`${demoSummary.offlineDevices}`} suffix={`/ ${demoSummary.totalDevices} 台`} color="#ff3b30"
          icon={svgI('M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636', '#ff3b30')} />
        <MetricSummaryCard label="平均藻毒素" value={demoSummary.averageToxinUgL.toFixed(2)} suffix="μg/L" color="#2d7cff"
          icon={svgI('M12 2L6 8C3.5 11 3 13 3 15a9 9 0 0018 0c0-2-.5-4-3-7l-6-6z', '#2d7cff')} />
        <MetricSummaryCard label="最高风险" value={max.toxinUgL.toFixed(2)} suffix="μg/L" color="#ff3b30"
          description={`${max.name} · ${getRiskLevel(max.toxinUgL) === 'critical' ? '高风险' : getRiskLevel(max.toxinUgL) === 'warning' ? '警戒' : '关注'}`}
          icon={svgI('M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z', '#ff3b30')} />
      </div>

      {/* Mid panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <SystemStatusPanel summary={demoSummary} />
        <AlertSummaryPanel alerts={alerts} />
        <OverviewTrendChart data={trendData} currentValue={max.toxinUgL} deviceName={max.name} />
      </div>

      {/* Table */}
      <LatestReadingsTable readings={demoReadings} />
    </div>
  );
}
