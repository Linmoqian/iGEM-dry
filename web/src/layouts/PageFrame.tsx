import type { ReactNode } from 'react';

interface PageFrameProps {
  children: ReactNode;
}

export default function PageFrame({ children }: PageFrameProps) {
  return (
    <div
      className="
        relative min-h-screen w-full
        bg-bg text-text
        border border-border rounded-[24px]
        p-2
        overflow-hidden
      "
    >
      {/* Bubble decorations — scattered in background */}
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
        <svg
          viewBox="0 0 180 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full opacity-30"
        >
          <path
            d="M0 20 Q22 8 45 20 T90 20 T135 20 T180 20"
            stroke="rgba(14,165,233,0.4)"
            strokeWidth="2"
            fill="none"
          />
          <path
            d="M0 28 Q22 16 45 28 T90 28 T135 28 T180 28"
            stroke="rgba(14,165,233,0.25)"
            strokeWidth="1.5"
            fill="none"
          />
        </svg>
      </div>

      {/* Main content layer */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {children}
      </div>
    </div>
  );
}
