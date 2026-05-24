import { Link, useLocation } from 'react-router-dom';
import { Bell, Home, MapPin, BarChart3, Cpu } from 'lucide-react';
import ImagePlaceholder from '../components/common/ImagePlaceholder';

const NAV_ITEMS = [
  { path: '/', label: '总览', icon: Home },
  { path: '/map', label: '地图监视', icon: MapPin },
  { path: '/data', label: '数据分析', icon: BarChart3 },
  { path: '/device', label: '设备配对', icon: Cpu },
] as const;

export default function AppHeader() {
  const { pathname } = useLocation();

  return (
    <header className="relative shrink-0 flex items-center justify-between h-[88px] px-8 z-20">
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-3 shrink-0">
        <ImagePlaceholder
          name="LOGO"
          width={48}
          height={48}
          className="rounded-[12px]"
        />
        <span className="text-[18px] font-bold text-text whitespace-nowrap">
          水体藻毒素监测平台
        </span>
      </div>

      {/* Center: Capsule nav tabs — absolute centering */}
      <nav
        className="
          absolute left-1/2 flex items-center gap-1
          h-11 px-1.5
          rounded-[24px]
          bg-white/60 border border-border
          backdrop-blur-sm
        "
        style={{ transform: 'translateX(-50%)' }}
      >
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const active = pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center justify-center gap-1.5
                h-[38px] px-4 rounded-[10px]
                text-[13px] font-medium whitespace-nowrap
                transition-all duration-150
                ${active
                  ? 'bg-primary/12 text-primary font-semibold'
                  : 'text-muted hover:text-text hover:bg-primary/4'}
              `}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Right: Notification + User — pushed to end by justify-between */}
      <div className="flex items-center gap-3 shrink-0">
        <button
          className="
            flex items-center justify-center
            w-10 h-10 rounded-[10px]
            text-muted hover:bg-primary/4 hover:text-text
            transition-colors duration-150
          "
          aria-label="通知"
        >
          <Bell size={20} />
        </button>

        <div
          className="
            flex items-center gap-2
            h-10 px-3
            rounded-[20px]
            bg-white/60 border border-border
          "
        >
          <ImagePlaceholder
            name="头像"
            width={28}
            height={28}
            className="rounded-full"
          />
          <span className="text-[13px] font-medium text-text whitespace-nowrap">
            iGEM Team
          </span>
        </div>
      </div>

      {/* Mascot — inline styles for reliable absolute positioning */}
      <div
        className="absolute overflow-visible z-30 pointer-events-none"
        style={{ right: '16px', top: '24px', width: '84px', height: '84px' }}
      >
        <ImagePlaceholder
          name="吉祥物"
          width={84}
          height={84}
          className="rounded-[16px]"
        />
      </div>
    </header>
  );
}
