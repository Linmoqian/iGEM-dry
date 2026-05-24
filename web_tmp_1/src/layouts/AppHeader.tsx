import { NavLink } from 'react-router-dom';
import { Bell, House, MapPin, Activity, LayoutGrid } from 'lucide-react';

const navItems = [
  { to: '/', label: '总览', icon: House },
  { to: '/map', label: '地图监视', icon: MapPin },
  { to: '/data', label: '数据分析', icon: Activity },
  { to: '/device', label: '设备配对', icon: LayoutGrid },
];

export default function AppHeader() {
  return (
    <header className="h-20 bg-white border-b border-[#E2E8F0] flex items-center px-8 gap-6 flex-shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-[#1A73E8] flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full" />
        </div>
        <span className="text-[#0D47A1] font-bold text-[22px]">水体藻毒素监测平台</span>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2 h-10 px-5 rounded-[20px] text-sm font-normal transition-colors ${
                isActive
                  ? 'bg-[#E0F2FE] text-[#1A73E8]'
                  : 'bg-transparent text-[#475569] hover:bg-[#F4F8FC]'
              }`
            }
          >
            <item.icon size={16} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-[#F4F8FC] transition-colors">
          <Bell size={20} className="text-[#475569]" />
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-[#E6F0FA] flex items-center justify-center text-[#1A73E8] text-xs font-bold">
            A
          </div>
          <span className="text-sm text-[#475569]">Admin</span>
        </div>
      </div>
    </header>
  );
}
