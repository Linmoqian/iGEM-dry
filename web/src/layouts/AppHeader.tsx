import {
  AlertTriangle,
  Bell,
  CalendarDays,
  ChevronDown,
  Clock3,
  Download,
  FlaskConical,
  MapPin,
  Plus,
  RefreshCw,
  Search,
  UserRound,
  Wifi,
  Wind,
  XCircle,
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { materials } from '../data/materials';

function HeaderPill({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`glass-button flex shrink-0 items-center gap-2.5 whitespace-nowrap px-4 text-[16px] text-[#14213b] ${className}`}>{children}</div>;
}

function SearchBox({ placeholder }: { placeholder: string }) {
  return (
    <div className="glass-button flex w-[195px] shrink-0 items-center gap-3 px-4 text-[15px] text-[#7b8aa3]">
      <Search size={21} />
      <span className="flex-1">{placeholder}</span>
    </div>
  );
}

function NoticeButton({ icon, count }: { icon: React.ReactNode; count?: number }) {
  return (
    <button className="icon-button" type="button">
      {icon}
      {count ? <span className="badge-dot">{count}</span> : null}
    </button>
  );
}

function UserMenu() {
  return (
    <HeaderPill className="h-[48px] w-[128px] gap-2 px-3 text-[14px]">
      <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#dff2ff] text-[#0874ed]">
        <UserRound size={21} />
      </span>
      <span>iGEM Team</span>
      <ChevronDown size={18} />
    </HeaderPill>
  );
}

function PageActions() {
  const { pathname } = useLocation();

  if (pathname === '/map') {
    return (
      <>
        <HeaderPill className="w-[160px]">
          <MapPin size={26} className="text-[#168ce4]" />
          <span>东湖监测区域</span>
          <ChevronDown size={18} />
        </HeaderPill>
        <HeaderPill className="w-[180px]">
          <Clock3 size={25} className="text-[#0874ed]" />
          <span>热力图更新</span>
          <b className="font-semibold">09:42</b>
        </HeaderPill>
        <HeaderPill className="w-[160px]">
          <Wind size={27} className="text-[#0874ed]" />
          <span>风场</span>
          <b className="font-semibold">2.1 m/s</b>
        </HeaderPill>
        <SearchBox placeholder="搜索设备 / 坐标" />
        <div className="flex-1" />
        <NoticeButton icon={<Bell size={26} />} count={3} />
        <NoticeButton icon={<AlertTriangle size={29} className="text-[#ef1919]" />} count={2} />
        <UserMenu />
      </>
    );
  }

  if (pathname === '/data') {
    return (
      <>
        <div className="flex w-[300px] shrink-0 flex-col gap-1">
          <span className="text-[16px] font-semibold">时间范围</span>
          <HeaderPill className="h-[50px]">
            <span>2025-05-20 ~ 2025-05-27</span>
            <CalendarDays size={20} />
          </HeaderPill>
        </div>
        <div className="flex w-[185px] shrink-0 flex-col gap-1">
          <span className="text-[16px] font-semibold">设备筛选</span>
          <HeaderPill className="h-[50px] justify-between">
            <span>全部设备</span>
            <ChevronDown size={18} />
          </HeaderPill>
        </div>
        <div className="flex w-[230px] shrink-0 flex-col gap-1">
          <span className="text-[16px] font-semibold">传感器</span>
          <HeaderPill className="h-[50px] justify-between">
            <span>藻毒素 + 水温 + pH</span>
            <ChevronDown size={18} />
          </HeaderPill>
        </div>
        <div className="flex-1" />
        <button className="glass-button flex h-[50px] shrink-0 items-center gap-2 px-4 text-[15px] font-semibold" type="button">
          <Download size={21} />
          导出数据
        </button>
        <NoticeButton icon={<Bell size={26} />} count={3} />
        <UserMenu />
      </>
    );
  }

  if (pathname === '/device') {
    return (
      <>
        <HeaderPill className="w-[118px] text-[#068b4f]">
          <Wifi size={26} />
          <b>在线</b>
          <b>9</b>
        </HeaderPill>
        <HeaderPill className="w-[118px] bg-[#fff4ec] text-[#f97316]">
          <Clock3 size={25} />
          <b>待机</b>
          <b>2</b>
        </HeaderPill>
        <HeaderPill className="w-[118px] bg-[#f5f7fb] text-[#4b5563]">
          <XCircle size={25} />
          <b>离线</b>
          <b>3</b>
        </HeaderPill>
        <SearchBox placeholder="搜索设备编号" />
        <button className="flex h-[54px] shrink-0 items-center gap-2 rounded-[10px] bg-[#0874ed] px-5 text-[17px] font-semibold text-white" type="button">
          <Plus size={27} />
          添加设备
        </button>
        <HeaderPill className="w-[138px]">
          <span>批量操作</span>
          <ChevronDown size={18} />
        </HeaderPill>
        <div className="flex-1" />
        <NoticeButton icon={<Bell size={26} />} count={1} />
        <UserMenu />
      </>
    );
  }

  return (
    <>
      <HeaderPill className="w-[160px]">
        <MapPin size={26} />
        <span>东湖监测区域</span>
      </HeaderPill>
      <HeaderPill className="w-[190px]">
        <RefreshCw size={25} />
        <span>实时同步</span>
        <b className="font-semibold">09:42</b>
      </HeaderPill>
      <HeaderPill className="w-[170px]">
        <FlaskConical size={26} />
        <span>今日采样</span>
        <b className="font-semibold">14 / 14</b>
      </HeaderPill>
      <SearchBox placeholder="搜索设备 / 告警" />
      <div className="flex-1" />
      <NoticeButton icon={<Bell size={26} />} count={3} />
      <NoticeButton icon={<Bell size={26} />} count={12} />
      <UserMenu />
    </>
  );
}

export default function AppHeader() {
  return (
    <header className="flex h-[110px] shrink-0 items-center gap-5 border-b border-[#b8dcfb] bg-white/82 px-7">
      <div className="flex min-w-[410px] shrink-0 items-center gap-4">
        <img className="h-[68px] w-[68px] object-contain" src={materials.logo} alt="SCAU" />
        <div className="flex items-center gap-2 whitespace-nowrap text-[28px] font-black tracking-[0.05em] text-[#004236]">
          <span>水体藻毒素监测平台</span>
        </div>
      </div>
      <PageActions />
    </header>
  );
}
