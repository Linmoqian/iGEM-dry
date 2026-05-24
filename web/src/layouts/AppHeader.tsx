import { Link, useLocation } from 'react-router-dom';
import { Bell, Home, MapPin, BarChart3, Cpu } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: '总览', icon: Home },
  { path: '/map', label: '地图监视', icon: MapPin },
  { path: '/data', label: '数据分析', icon: BarChart3 },
  { path: '/device', label: '设备配对', icon: Cpu },
] as const;

export default function AppHeader() {
  const { pathname } = useLocation();

  return (
    <header className="relative w-full h-[88px] flex-shrink-0 flex items-center justify-between bg-white rounded-[16px] border border-[#d0e3f5] px-[24px] box-border shadow-[0_2px_12px_rgba(14,165,233,0.04)] overflow-visible">
      {/* Left zone: Logo + title */}
      <div className="flex items-center gap-[12px] flex-shrink-0">
        <div className="w-[48px] h-[48px] bg-[#e6f2ff] border border-dashed border-[#0ea5e9] rounded-[12px] flex items-center justify-center text-[10px] text-sky-600 font-bold">LOGO</div>
        <span className="text-[20px] font-bold text-[#0f172a] tracking-wide whitespace-nowrap">水体藻毒素监测平台</span>
      </div>

      {/* Center zone: Capsule nav */}
      <div className="flex-1 flex justify-center max-w-[600px] mx-[24px] box-border">
        <nav className="flex items-center gap-[8px] bg-[#f0f7ff] border border-[#d0e3f5] p-[4px] rounded-full whitespace-nowrap">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
            const active = pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`
                  flex items-center justify-center gap-[6px]
                  px-[20px] py-[8px] rounded-full
                  text-[13px] font-medium whitespace-nowrap
                  transition-all duration-150
                  ${active
                    ? 'bg-white text-[#0ea5e9] font-bold shadow-[0_2px_8px_rgba(14,165,233,0.12)]'
                    : 'text-[#64748b] hover:text-[#0ea5e9] hover:bg-white/50'}
                `.trim()}
              >
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Right zone: Notification + User capsule — flex row, pr-[100px] for mascot */}
      <div className="flex items-center justify-end gap-[16px] flex-shrink-0 pr-[100px] box-border relative h-full">
        <button type="button" className="w-[40px] h-[40px] flex items-center justify-center text-[#64748b] hover:text-[#0ea5e9] hover:bg-[#f0f7ff] rounded-[12px] transition-colors cursor-pointer border border-transparent" aria-label="通知">
          <Bell size={20} />
        </button>
        <div className="flex items-center gap-[8px] flex-shrink-0 bg-[#f8fbff] border border-[#e8f1fa] py-[6px] px-[12px] rounded-full">
          <div className="w-[28px] h-[28px] bg-sky-200 rounded-full flex items-center justify-center text-[11px] font-bold text-sky-700">U</div>
          <span className="text-[13px] font-semibold text-[#0f172a] whitespace-nowrap">iGEM Team</span>
          <span className="text-[10px] text-[#64748b]">▼</span>
        </div>

        {/* Mascot — absolute at right edge, breaks out bottom */}
        <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[84px] h-[84px] z-30 pointer-events-none box-border">
          <div className="w-full h-full bg-[#e6f2ff] border border-dashed border-[#0ea5e9] rounded-[12px] flex flex-col items-center justify-center text-[10px] text-sky-600 font-bold shadow-md">
            <span>吉祥物</span>
            <span>84×84</span>
          </div>
        </div>
      </div>
    </header>
  );
}
