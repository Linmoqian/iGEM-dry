import { Link, useLocation } from 'react-router-dom';
import { Home, MapPin, BarChart3, Cpu } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: '总览', icon: Home },
  { path: '/map', label: '地图监视', icon: MapPin },
  { path: '/data', label: '数据分析', icon: BarChart3 },
  { path: '/device', label: '设备配对', icon: Cpu },
] as const;

export default function SidebarNav() {
  const { pathname } = useLocation();

  return (
    <aside className="relative w-[210px] h-full flex-shrink-0 flex flex-col justify-between overflow-visible box-border">
      <nav className="flex flex-col gap-[8px] w-full box-border pt-[16px] px-[12px]">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const active = pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`
                flex items-center gap-[10px]
                h-[48px] px-[16px]
                text-[14px] font-medium
                transition-all duration-150 cursor-pointer
                ${active
                  ? 'bg-[rgba(14,165,233,0.08)] border-l-[3px] border-[#0ea5e9] text-[#0ea5e9] font-bold rounded-[0_10px_10px_0] pl-[13px]'
                  : 'text-[#64748b] hover:bg-[rgba(14,165,233,0.04)] hover:text-[#0f172a] rounded-[0_10px_10px_0] border-l-[3px] border-transparent'}
              `.trim()}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom mascot — absolute anchored at bottom center */}
      <div className="absolute bottom-[16px] left-1/2 -translate-x-1/2 w-[160px] h-[220px] z-20 overflow-visible pointer-events-none box-border">
        <div className="w-full h-full bg-[#e6f2ff] border border-dashed border-[#0ea5e9] rounded-[16px] flex flex-col items-center justify-center text-[10px] text-sky-600 font-bold shadow-sm">
          <span>大吉祥物</span>
          <span>160×220</span>
        </div>
      </div>
    </aside>
  );
}
