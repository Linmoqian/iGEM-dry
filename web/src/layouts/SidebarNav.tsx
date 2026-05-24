import { Link, useLocation } from 'react-router-dom';
import { Home, MapPin, BarChart3, Cpu } from 'lucide-react';
import ImagePlaceholder from '../components/common/ImagePlaceholder';

const NAV_ITEMS = [
  { path: '/', label: '总览', icon: Home },
  { path: '/map', label: '地图监视', icon: MapPin },
  { path: '/data', label: '数据分析', icon: BarChart3 },
  { path: '/device', label: '设备配对', icon: Cpu },
] as const;

export default function SidebarNav() {
  const { pathname } = useLocation();

  return (
    <aside
      className="
        shrink-0 flex flex-col w-[210px]
        bg-white/50 backdrop-blur-sm
        border-r border-border
      "
    >
      {/* Nav items */}
      <nav className="flex flex-col gap-1.5 px-3 pt-4 flex-1">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const active = pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-2.5
                h-[50px] px-3
                text-[14px] font-medium
                transition-all duration-150
                ${active
                  ? 'border-l-[3px] border-primary bg-primary/8 text-primary rounded-r-[10px] pl-[9px]'
                  : 'text-muted hover:bg-primary/4 hover:text-text rounded-[10px] border-l-[3px] border-transparent'}
              `}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom decoration zone — overflow-visible for mascot overflow */}
      <div className="relative shrink-0 flex flex-col items-center pb-6 overflow-visible">
        {/* Bubble decorations */}
        {[16, 14, 18, 12].map((size, i) => (
          <div
            key={`sidebar-bubble-${i}`}
            className="absolute rounded-full pointer-events-none"
            style={{
              width: size,
              height: size,
              backgroundColor: 'rgba(14, 165, 233, 0.2)',
              bottom: `${60 + i * 28}px`,
              left: `${20 + (i % 3) * 24}px`,
              opacity: 0.3,
            }}
          />
        ))}

        {/* Large mascot placeholder */}
        <div className="relative z-20">
          <ImagePlaceholder
            name="吉祥物"
            width={160}
            height={220}
            className="rounded-[16px]"
          />
        </div>

        {/* Wave decoration below mascot */}
        <div className="mt-2" style={{ width: 180, height: 40 }}>
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
      </div>
    </aside>
  );
}
