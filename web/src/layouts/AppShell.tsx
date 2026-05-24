import { Outlet } from 'react-router-dom';
import PageFrame from './PageFrame';
import AppHeader from './AppHeader';
import SidebarNav from './SidebarNav';

export default function AppShell() {
  return (
    <PageFrame>
      <AppHeader />

      <div className="flex flex-1 min-h-0">
        <SidebarNav />

        {/* Main content — independent vertical scroll */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </PageFrame>
  );
}
