import { NavLink } from 'react-router-dom';
import { House, MapPin, Activity, LayoutGrid } from 'lucide-react';

const navItems = [
  { to: '/', label: '总览', icon: House },
  { to: '/map', label: '地图监视', icon: MapPin },
  { to: '/data', label: '数据分析', icon: Activity },
  { to: '/device', label: '设备配对', icon: LayoutGrid },
];

export default function SidebarNav() {
  return (
    <aside className="w-[240px] flex flex-col bg-white flex-shrink-0 px-4 py-0 gap-2">
      {/* Logo */}
      <div className="flex items-center gap-3 h-20 px-2">
        <div className="w-9 h-9 rounded-full bg-[#1A73E8] flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full" />
        </div>
        <span className="text-[#1A73E8] font-bold text-sm">OCEAN</span>
      </div>

      {/* Nav Items */}
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) =>
            `flex items-center gap-3 h-12 px-4 rounded-lg text-sm font-normal transition-colors ${
              isActive
                ? 'bg-[#E6F0FA] text-[#1A73E8]'
                : 'bg-transparent text-[#475569] hover:bg-[#F4F8FC]'
            }`
          }
        >
          <item.icon size={20} />
          <span>{item.label}</span>
        </NavLink>
      ))}

      {/* Spacer */}
      <div className="flex-1" />

      {/* Mascot Placeholder */}
      <div className="h-[220px] border border-dashed border-[#E2E8F0] rounded-lg flex items-center justify-center text-[#64748B] text-xs mb-4">
        [Mascot Character Asset]
      </div>
    </aside>
  );
}
