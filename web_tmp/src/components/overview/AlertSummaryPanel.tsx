import AquaPanel from '@/components/common/AquaPanel';
import type { AlertSummaryData } from '@/types/domain';

interface P { alerts: AlertSummaryData; }

const ROWS = [
  { key: 'criticalCount' as const, label: '高风险告警', color: '#ff3b30' },
  { key: 'warningCount' as const, label: '警戒告警', color: '#ff8a00' },
  { key: 'watchCount' as const, label: '关注告警', color: '#ffb400' },
  { key: 'offlineCount' as const, label: '设备离线', color: '#2d7cff' },
];

export default function AlertSummaryPanel({ alerts }: P) {
  return (
    <AquaPanel title="告警摘要" subtitle="需要关注的异常项">
      <div className="flex flex-col gap-3">
        {ROWS.map((row) => (
          <div key={row.key} className="flex items-center justify-between p-3 rounded-2xl cursor-pointer hover:bg-[rgba(45,124,255,0.03)] transition-colors"
            style={{ borderLeft: `4px solid ${row.color}`, backgroundColor: `${row.color}0A` }}>
            <span className="text-[13px] font-semibold text-[var(--color-text)]">{row.label}</span>
            <div className="flex items-center gap-2">
              <span className="text-[22px] font-extrabold" style={{ color: row.color }}>{alerts[row.key]}</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-muted)" strokeWidth="2"><path d="M9 18l6-6-6-6" /></svg>
            </div>
          </div>
        ))}
      </div>
    </AquaPanel>
  );
}
