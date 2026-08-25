import { BarChart3, House, MapPinned, Network } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { materials } from '../data/materials';

const navItems = [
  { to: '/', label: '总览', icon: House },
  { to: '/map', label: '地图监视', icon: MapPinned },
  { to: '/data', label: '数据分析', icon: BarChart3 },
  { to: '/device', label: '设备配对', icon: Network },
];

export default function SidebarNav() {
  return (
    <aside className="sidebar bubble-field">
      <nav>
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            <item.icon size={25} strokeWidth={2.15} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <img className="sidebar-mascot" src={materials.mascotHero} alt="项目吉祥物" />
      <div className="seaweed seaweed-left" />
      <div className="seaweed seaweed-right" />
      <div className="sidebar-water" />
    </aside>
  );
}
