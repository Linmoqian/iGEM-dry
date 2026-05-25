import { NavLink, useLocation } from 'react-router-dom';
import { Bell, House, MapPin, Activity, LayoutGrid, Download, Calendar, ChevronDown } from 'lucide-react';

const navItems = [
  { to: '/', label: '总览', icon: House },
  { to: '/map', label: '地图监视', icon: MapPin },
  { to: '/data', label: '数据分析', icon: Activity },
  { to: '/device', label: '设备配对', icon: LayoutGrid },
];

function DataHeaderFilters() {
  return (
    <>
      {/* Filter Area */}
      <div className="flex items-center gap-6">
        <div className="flex flex-col gap-1">
          <span className="text-xs text-[#64748B]">时间范围</span>
          <div className="flex items-center gap-2 h-9 px-3 rounded-lg border border-[#E2E8F0] text-sm text-[#0F172A]">
            <span>2025-05-20 ~ 2025-05-27</span>
            <Calendar size={16} className="text-[#64748B]" />
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-xs text-[#64748B]">设备筛选</span>
          <div className="flex items-center justify-between gap-2 h-9 px-3 rounded-lg border border-[#E2E8F0] text-sm text-[#0F172A]" style={{ width: 140 }}>
            <span>全部设备</span>
            <ChevronDown size={16} className="text-[#64748B]" />
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-xs text-[#64748B]">传感器筛选</span>
          <div className="flex items-center justify-between gap-2 h-9 px-3 rounded-lg border border-[#E2E8F0] text-sm text-[#0F172A]" style={{ width: 180 }}>
            <span>藻毒素 + 水温 + pH</span>
            <ChevronDown size={16} className="text-[#64748B]" />
          </div>
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Export Button */}
      <button className="flex items-center gap-2 h-9 px-4 rounded-lg bg-white border border-[#E2E8F0] text-sm font-medium text-[#0F172A] hover:bg-[#F8FAFC] transition-colors">
        <Download size={16} />
        导出数据
      </button>
    </>
  );
}

export default function AppHeader() {
  const location = useLocation();
  const isDataPage = location.pathname === '/data';

  return (
    <header className="h-20 bg-white border-b border-[#E2E8F0] flex items-center px-8 gap-6 flex-shrink-0">
      {/* Brand */}
      <div className="flex items-center gap-3 flex-shrink-0">
        <div className="w-10 h-10 rounded-full bg-[#1A73E8] flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full" />
        </div>
        <span className="text-[#0D47A1] font-bold text-[22px]">水体藻毒素监测平台</span>
      </div>

      {isDataPage ? (
        <DataHeaderFilters />
      ) : (
        <>
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
        </>
      )}
    </header>
  );
}
