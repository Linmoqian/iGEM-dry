import { Activity, House, LayoutGrid, MapPinned } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { materials } from '../data/materials';

const navItems = [
  { to: '/', label: '总览', icon: House },
  { to: '/map', label: '地图监视', icon: MapPinned },
  { to: '/data', label: '数据分析', icon: Activity },
  { to: '/device', label: '设备配对', icon: LayoutGrid },
];

export default function SidebarNav() {
  return (
    <aside className="bubble-field relative w-[238px] shrink-0 overflow-hidden border-r border-[#b8dcfb] bg-white/72 px-4 pt-10">
      <nav className="relative z-10 flex flex-col gap-7">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              [
                'flex h-[62px] items-center gap-4 rounded-[12px] px-5 text-[20px] font-semibold transition',
                isActive
                  ? 'border-l-[4px] border-[#0874ed] bg-[#eaf5ff] text-[#0874ed] shadow-[0_8px_16px_rgba(28,121,222,0.08)]'
                  : 'text-[#1c2c4a] hover:bg-[#f0f8ff]',
              ].join(' ')
            }
          >
            <item.icon size={30} strokeWidth={2.2} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <img
        className="pointer-events-none absolute bottom-1 left-5 z-10 w-[190px] object-contain"
        src={materials.mascotScientist}
        alt=""
      />
      <div className="pointer-events-none absolute -bottom-9 left-0 h-[120px] w-full bg-[radial-gradient(ellipse_at_center,_rgba(113,205,244,0.28),_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-2 left-6 h-[150px] w-[36px] rounded-t-full bg-[#91e2d4]/45 blur-[1px]" />
      <div className="pointer-events-none absolute bottom-0 right-8 h-[118px] w-[30px] rounded-t-full bg-[#8de4df]/50 blur-[1px]" />
    </aside>
  );
}
