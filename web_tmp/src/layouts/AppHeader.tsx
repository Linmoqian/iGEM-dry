import { NavLink } from 'react-router-dom';
import ImagePlaceholder from '@/components/common/ImagePlaceholder';

const NAV_ITEMS = [
  { id: 'overview', label: '总览', href: '/' },
  { id: 'map', label: '地图监视', href: '/map' },
  { id: 'data', label: '数据分析', href: '/data' },
  { id: 'device', label: '设备配对', href: '/device' },
];

export default function AppHeader() {
  return (
    <header className="app-header">
      {/* Logo */}
      <div className="flex items-center gap-3" style={{ width: '150px' }}>
        <div className="w-[42px] h-[42px] rounded-full bg-gradient-to-br from-[#2d7cff] to-[#34b3d9] flex items-center justify-center shadow-[0_2px_10px_rgba(45,124,255,0.18)]">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L6 8C3.5 11 3 13 3 15a9 9 0 0018 0c0-2-.5-4-3-7l-6-6z" />
            <path d="M12 6v4" opacity="0.5" />
          </svg>
        </div>
        <div className="flex flex-col leading-tight">
          <span className="text-[16px] font-extrabold text-[var(--color-text)] tracking-[-0.02em]">水体藻毒素监测平台</span>
          <span className="text-[10px] text-[var(--color-muted)] tracking-[0.04em]">Water Algal Toxin Monitoring</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex items-center gap-2">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.id} to={item.href}
            className={({ isActive }) => `header-nav-btn ${isActive ? 'active' : ''}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Right */}
      <div className="flex items-center gap-3" style={{ width: '150px', justifyContent: 'flex-end' }}>
        <button type="button" className="w-9 h-9 rounded-full border border-[var(--color-border)] flex items-center justify-center hover:bg-[var(--color-primary-light)] transition-colors" aria-label="通知">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-muted)" strokeWidth="1.5"><path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
        </button>
        <div className="flex items-center gap-1.5 px-3 py-2 rounded-full bg-[var(--color-primary-light)] text-[13px] font-semibold text-[var(--color-primary)]">
          <span>iGEM Team</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6" /></svg>
        </div>
        <ImagePlaceholder width={56} height={56} label="萌物" variant="mascot" rounded="full" />
      </div>
    </header>
  );
}
