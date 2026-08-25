import { useEffect, useRef, useState } from 'react';
import {
  Bell,
  CalendarDays,
  ChevronDown,
  Download,
  RefreshCw,
  Search,
  UserRound,
} from 'lucide-react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { demoReadings } from '../data/demoReadings';
import { materials } from '../data/materials';
import { monitoringService } from '../services/monitoringService';

function Pill({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`header-pill ${className}`}>{children}</div>;
}

function RouteSearch({ placeholder }: { placeholder: string }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [value, setValue] = useState(searchParams.get('q') || '');

  useEffect(() => setValue(searchParams.get('q') || ''), [searchParams]);

  const submit = () => {
    const next = new URLSearchParams(searchParams);
    if (value.trim()) next.set('q', value.trim());
    else next.delete('q');
    setSearchParams(next, { replace: true });
  };

  return (
    <label className="header-search" aria-label={placeholder}>
      <Search size={19} />
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => event.key === 'Enter' && submit()}
        onBlur={submit}
        placeholder={placeholder}
      />
    </label>
  );
}

function NoticeMenu() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  return (
    <div className="header-menu-root" ref={rootRef}>
      <button className="header-icon-button" type="button" aria-label="查看通知" onClick={() => setOpen((value) => !value)}>
        <Bell size={24} />
        <span className="notice-dot" />
      </button>
      {open ? (
        <div className="header-popover notice-popover">
          <b>最新通知</b>
          <p><span className="dot danger" />藻华预警浮标-06 超过高风险阈值</p>
          <p><span className="dot warning" />3 台设备需要检查电量或信号</p>
          <button type="button" onClick={() => setOpen(false)}>标记为已读</button>
        </div>
      ) : null}
    </div>
  );
}

function UserMenu() {
  const [open, setOpen] = useState(false);
  return (
    <div className="header-menu-root">
      <button className="user-pill" type="button" onClick={() => setOpen((value) => !value)}>
        <span className="avatar"><UserRound size={18} /></span>
        <span>iGEM Team</span>
        <ChevronDown size={16} />
      </button>
      {open ? (
        <div className="header-popover user-popover">
          <b>演示工作区</b>
          <span>当前为 Mock 数据模式</span>
          <button type="button" onClick={() => setOpen(false)}>关闭菜单</button>
        </div>
      ) : null}
    </div>
  );
}

function DataActions() {
  const [searchParams, setSearchParams] = useSearchParams();
  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next, { replace: true });
  };

  return (
    <>
      <label className="filter-stack date-filter">
        <span>时间范围</span>
        <Pill>
          <span>2025-05-20&nbsp; ~ &nbsp;2025-05-27</span>
          <CalendarDays size={18} />
        </Pill>
      </label>
      <label className="filter-stack">
        <span>设备筛选</span>
        <select value={searchParams.get('device') || ''} onChange={(event) => setParam('device', event.target.value)}>
          <option value="">全部设备</option>
          {demoReadings.slice(0, 6).map((device) => <option key={device.id} value={device.id}>{device.name}</option>)}
        </select>
      </label>
      <label className="filter-stack sensor-filter">
        <span>传感器筛选</span>
        <select value={searchParams.get('sensors') || 'all'} onChange={(event) => setParam('sensors', event.target.value)}>
          <option value="all">藻毒素 + 水温 + pH</option>
          <option value="toxin">仅藻毒素</option>
          <option value="water">藻毒素 + 水温</option>
          <option value="ph">藻毒素 + pH</option>
        </select>
      </label>
      <div className="header-spacer" />
      <button className="header-action-button secondary" type="button" onClick={() => window.dispatchEvent(new CustomEvent('igem:export-data'))}>
        <Download size={19} />导出数据
      </button>
    </>
  );
}

export default function AppHeader() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const [summaryText, setSummaryText] = useState('9 / 14 台');
  const [syncTime, setSyncTime] = useState('09:42');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    monitoringService.getDashboardSummary().then((summary) => setSummaryText(`${summary.onlineDevices} / ${summary.totalDevices} 台`));
  }, [pathname]);

  const refresh = async () => {
    setRefreshing(true);
    window.dispatchEvent(new CustomEvent('igem:refresh'));
    await monitoringService.getDashboardSummary();
    setSyncTime(new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }));
    setRefreshing(false);
  };

  return (
    <header className="app-header">
      <button className="brand" type="button" onClick={() => navigate('/')} aria-label="返回总览">
        <img src={materials.logo} alt="OCEAN 项目标志" />
        <strong>水体藻毒素监测平台</strong>
      </button>

      <div className="header-actions">
        {pathname === '/data' ? <DataActions /> : null}
        {pathname === '/' ? (
          <>
            <Pill className="live-pill"><span className="pulse-dot" />实时监测中</Pill>
            <Pill>最后同步&nbsp; {syncTime}</Pill>
            <RouteSearch placeholder="搜索设备、位置或告警" />
            <button className="square-button" type="button" aria-label="刷新数据" onClick={refreshing ? undefined : refresh}>
              <RefreshCw size={20} className={refreshing ? 'spin' : ''} />
            </button>
          </>
        ) : null}
        {pathname === '/map' ? (
          <>
            <Pill className="region-pill">东湖监测区</Pill>
            <Pill className="live-pill"><span className="pulse-dot" />热力图实时更新</Pill>
            <RouteSearch placeholder="搜索设备或地图位置" />
            <button className="square-button" type="button" aria-label="刷新地图" onClick={refresh}><RefreshCw size={20} className={refreshing ? 'spin' : ''} /></button>
          </>
        ) : null}
        {pathname === '/device' ? (
          <>
            <Pill className="live-pill"><span className="pulse-dot" />网关在线</Pill>
            <Pill>已连接&nbsp; {summaryText}</Pill>
            <RouteSearch placeholder="搜索设备名称或编号" />
          </>
        ) : null}
        <div className="header-spacer" />
        <NoticeMenu />
        <UserMenu />
      </div>
    </header>
  );
}
