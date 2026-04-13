'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { id: 'overview', label: '总览', href: '/' },
  { id: 'map', label: '地图监视', href: '/map' },
  { id: 'data', label: '数据分析', href: '/data' },
  { id: 'device', label: '设备配对', href: '/device' },
] as const;

function splitLabel(label: string): string[] {
  if (label.length <= 2) return [label];
  const mid = Math.ceil(label.length / 2);
  return [label.slice(0, mid), label.slice(mid)];
}

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="w-full flex justify-center pt-6 px-4 pb-4">
      <div
        className="
          flex items-center justify-center gap-6
          bg-[#0B1221]/70 backdrop-blur-2xl
          rounded-full px-6 py-3
          shadow-[0_8px_32px_rgba(0,0,0,0.5)]
          border border-slate-700/50
          transition-all duration-300
        "
      >
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.id}
              href={item.href}
              className="
                relative flex items-center justify-center
                border border-transparent rounded-full
                cursor-pointer select-none
                hover:scale-[1.05] active:scale-[0.96] overflow-hidden group
              "
              style={{
                width: isActive ? 140 : 70,
                height: isActive ? 52 : 72,
                backgroundColor: isActive ? 'rgba(14, 165, 233, 0.1)' : 'transparent',
                borderColor: isActive ? 'rgba(14, 165, 233, 0.3)' : 'transparent',
                color: isActive ? '#38bdf8' : '#94a3b8',
                boxShadow: isActive ? '0 0 20px rgba(14, 165, 233, 0.1) inset' : 'none',
                transition:
                  'all 0.55s cubic-bezier(0.25, 1, 0.5, 1)',
              }}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 mix-blend-overlay"></div>
              )}
              {isActive ? (
                <span className="text-[13px] font-bold tracking-[0.18em] whitespace-nowrap z-10 drop-shadow-[0_0_8px_rgba(56,189,248,0.5)]">
                  {item.label}
                </span>
              ) : (
                <span className="flex flex-col items-center leading-[1.35] text-[13px] font-medium tracking-[0.18em] group-hover:text-slate-300 transition-colors">
                  {splitLabel(item.label).map((line, i) => (
                    <span key={i}>{line}</span>
                  ))}
                </span>
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
