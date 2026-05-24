interface P { showDevices: boolean; showHeat: boolean; onToggleDevices: () => void; onToggleHeat: () => void; }

export default function MapLayerToggle({ showDevices, showHeat, onToggleDevices, onToggleHeat }: P) {
  return (
    <div className="flex gap-1 p-1 rounded-full bg-white/92 backdrop-blur border border-[var(--color-border)] shadow-[0_2px_12px_rgba(45,124,255,0.04)]">
      <button onClick={onToggleDevices}
        className={`px-4 py-2 rounded-full text-[12px] font-semibold transition-colors ${showDevices ? 'bg-[#2d7cff] text-white' : 'text-[var(--color-muted)] hover:text-[#2d7cff]'}`}>
        设备图层
      </button>
      <button onClick={onToggleHeat}
        className={`px-4 py-2 rounded-full text-[12px] font-semibold transition-colors ${showHeat ? 'bg-[#2d7cff] text-white' : 'text-[var(--color-muted)] hover:text-[#2d7cff]'}`}>
        热力图层
      </button>
    </div>
  );
}
