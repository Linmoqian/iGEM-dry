import { Outlet } from 'react-router-dom';
import AppHeader from './AppHeader';
import SidebarNav from './SidebarNav';

export default function AppShell() {
  return (
    <div className="app-frame flex flex-col">
      <AppHeader />
      <div className="flex min-h-0 flex-1">
        <SidebarNav />
        <main className="min-w-0 flex-1 overflow-hidden px-6 py-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
