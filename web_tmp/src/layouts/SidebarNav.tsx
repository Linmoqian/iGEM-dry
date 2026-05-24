import { NavLink, useLocation } from 'react-router-dom';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';

const NAV_ITEMS = [
  { id: 'overview', label: '总览', href: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { id: 'map', label: '地图监视', href: '/map', icon: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-4m-6 4V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' },
  { id: 'data', label: '数据分析', href: '/data', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { id: 'device', label: '设备配对', href: '/device', icon: 'M12 18v-6m0 0V6m0 6H6m6 0h6m-3 3a3 3 0 01-3 3H9a3 3 0 01-3-3V9a3 3 0 013-3h3a3 3 0 013 3v6z' },
];

export default function SidebarNav() {
  const location = useLocation();

  return (
    <aside className="sidebar-nav">
      <nav className="flex flex-col gap-1.5 px-3 pt-6">
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <NavLink key={item.id} to={item.href} className={`sidebar-nav-item ${isActive ? 'active' : ''}`}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                strokeWidth={isActive ? 2 : 1.5} strokeLinecap="round" strokeLinejoin="round">
                <path d={item.icon} />
              </svg>
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Ocean decoration */}
      <div className="mt-auto px-3 pb-5 flex flex-col items-center gap-4">
        {/* Bubbles */}
        <div className="flex gap-1.5 flex-wrap justify-center">
          {[10, 6, 14, 8, 12].map((size, i) => (
            <div key={i} className="bubble-dot rounded-full bg-[rgba(45,124,255,0.08)]"
              style={{ width: size, height: size, animationDelay: `${i * 0.4}s`, animationDuration: `${2.5 + i * 0.3}s` }} />
          ))}
        </div>
        {/* Kelp */}
        <div className="flex gap-1">
          {[44, 54, 38].map((h, i) => (
            <div key={i} className="w-[5px] rounded-full bg-[rgba(29,185,84,0.18)]" style={{ height: h }} />
          ))}
        </div>
        {/* Mascot */}
        <ImagePlaceholder width={130} height={180} label="萌物占位" fileName="藻类实验助手" variant="mascot" />
      </div>
    </aside>
  );
}
