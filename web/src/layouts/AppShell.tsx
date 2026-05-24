import AppHeader from './AppHeader';
import SidebarNav from './SidebarNav';
import { Outlet } from 'react-router-dom';

export default function AppShell() {
  return (
    <div className="w-full h-full flex flex-col p-[24px] box-border min-h-0 overflow-hidden">
      <AppHeader />

      <div className="flex flex-1 w-full h-full min-h-0 mt-[20px] overflow-hidden box-border">
        <SidebarNav />

        <main className="flex-1 min-w-0 h-full ml-[24px] bg-white rounded-[24px] shadow-[0_4px_24px_rgba(14,165,233,0.06)] border border-[#d0e3f5] p-[24px] overflow-y-auto box-border">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
