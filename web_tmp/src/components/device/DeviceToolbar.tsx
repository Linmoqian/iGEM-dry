import AppButton from '@/components/common/AppButton';

interface P { onAdd: () => void; onRefresh: () => void; }

export default function DeviceToolbar({ onAdd, onRefresh }: P) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <AppButton onClick={onAdd}
        icon={<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 4v16m8-8H4" /></svg>}>
        添加设备
      </AppButton>
      <AppButton variant="secondary" onClick={onRefresh}
        icon={<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" /></svg>}>
        刷新列表
      </AppButton>
      <AppButton variant="secondary" onClick={() => alert('批量操作功能将在后续版本中实现')}>
        批量操作
      </AppButton>
    </div>
  );
}
