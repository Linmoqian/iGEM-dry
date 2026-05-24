const ITEMS = [
  { color: '#1db954', label: '正常', range: '< 0.5 μg/L' },
  { color: '#ffb400', label: '关注', range: '0.5 - 1.0 μg/L' },
  { color: '#ff8a00', label: '警戒', range: '1.0 - 5.0 μg/L' },
  { color: '#ff3b30', label: '高风险', range: '> 5.0 μg/L' },
];

export default function RiskLegend() {
  return (
    <div className="flex items-center gap-5 px-5 py-2.5 rounded-full bg-white/92 backdrop-blur border border-[var(--color-border)] shadow-[0_2px_12px_rgba(45,124,255,0.04)]">
      {ITEMS.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span className="w-[10px] h-[10px] rounded-full" style={{ backgroundColor: item.color }} />
          <span className="text-[11px] font-semibold text-[var(--color-text)]">{item.label}</span>
          <span className="text-[11px] text-[var(--color-muted)]">{item.range}</span>
        </div>
      ))}
    </div>
  );
}
