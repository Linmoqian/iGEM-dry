interface AppSelectProps { label: string; value: string; options: { value: string; label: string }[]; onChange: (v: string) => void; }

export default function AppSelect({ label, value, options, onChange }: AppSelectProps) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-[11px] font-semibold text-[var(--color-muted)]">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}
        className="text-[13px] py-2 px-3 rounded-[14px] border border-[var(--color-border)] bg-white text-[var(--color-text)] outline-none focus:border-[var(--color-primary)] transition-colors">
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}
