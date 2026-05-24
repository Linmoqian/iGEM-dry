import type { ReactNode } from 'react';

interface PageFrameProps {
  children: ReactNode;
}

export default function PageFrame({ children }: PageFrameProps) {
  return (
    <div className="relative w-full h-full bg-[#f0f7ff] overflow-hidden">
      {/* Bubble decorations — clipped by this container only */}
      {[...Array(6)].map((_, i) => (
        <div
          key={`bubble-${i}`}
          className="absolute rounded-full pointer-events-none"
          style={{
            width: 12 + (i % 3) * 4,
            height: 12 + (i % 3) * 4,
            backgroundColor: 'rgba(14, 165, 233, 0.15)',
            top: `${15 + i * 14}%`,
            right: `${2 + (i % 4) * 3}%`,
            opacity: 0.3,
            zIndex: 1,
          }}
        />
      ))}

      {/* Bottom wave decoration */}
      <div
        className="absolute bottom-0 left-1/2 -translate-x-1/2 pointer-events-none"
        style={{ width: 180, height: 40, zIndex: 1 }}
      >
        <svg viewBox="0 0 180 40" fill="none" className="w-full h-full opacity-30">
          <path d="M0 20 Q22 8 45 20 T90 20 T135 20 T180 20" stroke="rgba(14,165,233,0.4)" strokeWidth="2" fill="none" />
          <path d="M0 28 Q22 16 45 28 T90 28 T135 28 T180 28" stroke="rgba(14,165,233,0.25)" strokeWidth="1.5" fill="none" />
        </svg>
      </div>

      {/* Content layer — NO overflow-hidden, so mascots can break out */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </div>
  );
}
