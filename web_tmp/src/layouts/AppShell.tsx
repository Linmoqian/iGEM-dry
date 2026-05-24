import { Outlet } from 'react-router-dom';
import AppHeader from './AppHeader';
import SidebarNav from './SidebarNav';

export default function AppShell() {
  return (
    <div className="app-shell">
      <AppHeader />
      <div className="app-body">
        <SidebarNav />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
