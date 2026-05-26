import { Outlet } from 'react-router-dom';
import SidebarNav from './SidebarNav';

export default function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'linear-gradient(180deg, #F4F8FC 0%, #E6F0FA 100%)' }}>
      <SidebarNav />
      <main className="flex-1 overflow-y-auto p-5">
        <Outlet />
      </main>
    </div>
  );
}
