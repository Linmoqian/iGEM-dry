import AquaPanel from '@/components/common/AquaPanel';

interface P { summary: { totalDevices: number; onlineDevices: number; lowBatteryDevices: number; weakSignalDevices: number; }; }

export default function SystemStatusPanel({ summary }: P) {
  const onlineRate = Math.round((summary.onlineDevices / summary.totalDevices) * 100);
  const allGood = summary.lowBatteryDevices === 0 && summary.weakSignalDevices === 0;
  const dataOk = summary.onlineDevices > 0;
  const statusColor = allGood ? '#1db954' : '#ffb400';

  return (
    <AquaPanel title="系统状态" subtitle="整体运行概况">
      <div className="flex flex-col items-center gap-5">
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ backgroundColor: `${statusColor}14` }}>
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke={statusColor} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M9 12l2 2 4-4" />
            </svg>
          </div>
          <p className="text-[16px] font-bold mt-3" style={{ color: statusColor }}>{allGood ? '运行正常' : '需关注'}</p>
        </div>
        <div className="grid grid-cols-3 gap-3 w-full">
          {[
            { label: '数据采集', ok: dataOk },
            { label: '数据传输', ok: true },
            { label: '设备在线率', ok: onlineRate >= 50, value: `${onlineRate}%` },
          ].map((item) => (
            <div key={item.label} className="text-center p-3 rounded-2xl bg-[rgba(45,124,255,0.03)]">
              <p className="text-[10px] text-[var(--color-muted)] font-semibold uppercase tracking-wider">{item.label}</p>
              <p className={`text-[14px] font-bold mt-1 ${item.ok ? 'text-[#1db954]' : 'text-[#ff3b30]'}`}>
                {'value' in item ? item.value : item.ok ? '正常' : '中断'}
              </p>
            </div>
          ))}
        </div>
      </div>
    </AquaPanel>
  );
}
