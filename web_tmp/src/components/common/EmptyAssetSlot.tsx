interface EmptyAssetSlotProps {
  label: string;
  variant?: 'mascot' | 'icon' | 'illustration' | 'logo' | 'device' | 'microscope' | 'water';
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = { sm: 56, md: 80, lg: 112 };

export default function EmptyAssetSlot({ label, variant = 'icon', size = 'md' }: EmptyAssetSlotProps) {
  const px = sizeMap[size];

  return (
    <div
      className="placeholder-box rounded-xl flex-col gap-1"
      style={{ width: px, height: px }}
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="rgba(13,125,242,0.2)" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <path d="M21 15l-5-5L5 21" />
      </svg>
      <span className="text-[8px] text-[#5A7184]/50">{label}</span>
      <span className="text-[7px] text-[#5A7184]/30">{variant}</span>
    </div>
  );
}
