import AppButton from '@/components/common/AppButton';
import type { DeviceModalState, DeviceItem } from '@/types/domain';

interface P { modal: DeviceModalState; editForm?: Partial<DeviceItem>; onClose: () => void; onSave?: () => void; onDelete?: () => void; onChange?: (f: string, v: string) => void; }

export default function DeviceFormModal({ modal, editForm, onClose, onSave, onDelete, onChange }: P) {
  if (modal.type === 'none') return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[rgba(26,37,51,0.25)] backdrop-blur-[4px] px-4">
      <div className="aqua-panel p-6 max-w-md w-full shadow-[0_8px_40px_rgba(45,124,255,0.06)]">

        {/* Details */}
        {modal.type === 'details' && modal.device && (
          <>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-[17px] font-extrabold text-[var(--color-text)]">采样详情</h3>
              <button type="button" onClick={onClose} className="text-[var(--color-muted)] hover:text-[var(--color-text)]" aria-label="关闭">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="flex flex-col gap-1.5">
              {[['设备名称',modal.device.deviceName],['位置',modal.device.location],['藻毒素',`${modal.device.toxinUgL.toFixed(2)} μg/L`],['水温',`${modal.device.waterTempC.toFixed(1)} °C`],['pH',modal.device.ph.toFixed(1)],['电量',`${modal.device.battery}%`],['信号',`${modal.device.signalDbm} dBm`],['更新时间',modal.device.updatedAt]].map(([label,value]) => (
                <div key={label} className="flex justify-between py-2.5 border-b border-[var(--color-border)] text-[13px]">
                  <span className="text-[var(--color-muted)]">{label}</span>
                  <span className="font-semibold text-[var(--color-text)]">{value}</span>
                </div>
              ))}
            </div>
            <AppButton onClick={onClose} className="w-full mt-5">确认</AppButton>
          </>
        )}

        {/* Edit */}
        {modal.type === 'edit' && modal.device && (
          <>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-[17px] font-extrabold text-[var(--color-text)]">编辑设备</h3>
              <button type="button" onClick={onClose} className="text-[var(--color-muted)] hover:text-[var(--color-text)]" aria-label="关闭">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="flex flex-col gap-4">
              {[{ label:'设备名称',key:'deviceName',type:'text' },{ label:'位置名称',key:'location',type:'text' }].map(({label,key,type}) => (
                <div key={key}>
                  <label className="text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wider">{label}</label>
                  <input type={type} value={editForm?.[key as keyof typeof editForm] ?? ''} onChange={(e) => onChange?.(key, e.target.value)}
                    className="w-full mt-1.5 py-2 px-3 rounded-[14px] border border-[var(--color-border)] text-[13px] outline-none focus:border-[#2d7cff] transition-colors" />
                </div>
              ))}
              {[
                { label:'设备类型', key:'deviceType', opts:['浮标','探针','岸线巡检器','其他'] },
                { label:'连接方式', key:'connectionType', opts:[{value:'none',label:'未连接'},{value:'wifi',label:'WiFi'},{value:'bluetooth',label:'蓝牙'}] },
              ].map(({label,key,opts}) => {
                const selectOpts: {value:string;label:string}[] = Array.isArray(opts) ? (typeof opts[0]==='string' ? (opts as string[]).map(o=>({value:o,label:o})) : opts as {value:string;label:string}[]) : [];
                const cur = String(editForm?.[key as keyof typeof editForm] ?? selectOpts[0]?.value ?? '');
                return (
                  <div key={key}>
                    <label className="text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wider">{label}</label>
                    <select value={cur} onChange={(e) => onChange?.(key, e.target.value)}
                      className="w-full mt-1.5 py-2 px-3 rounded-[14px] border border-[var(--color-border)] text-[13px] outline-none focus:border-[#2d7cff] bg-white transition-colors">
                      {selectOpts.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </div>
                );
              })}
            </div>
            <div className="flex gap-3 mt-5">
              <AppButton variant="secondary" onClick={onClose} className="flex-1">取消</AppButton>
              <AppButton onClick={onSave} className="flex-1">保存</AppButton>
            </div>
          </>
        )}

        {/* Delete */}
        {modal.type === 'delete' && modal.device && (
          <>
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-2xl bg-[rgba(255,59,48,0.08)] flex items-center justify-center mb-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ff3b30" strokeWidth="2"><path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>
              </div>
              <h3 className="text-[16px] font-bold text-[var(--color-text)] mb-1">确认删除</h3>
              <p className="text-[13px] text-[var(--color-muted)]">确定要删除设备 {modal.device.deviceName} 吗？</p>
            </div>
            <div className="flex gap-3 mt-5">
              <AppButton variant="secondary" onClick={onClose} className="flex-1">取消</AppButton>
              <AppButton variant="danger" onClick={onDelete} className="flex-1">确认删除</AppButton>
            </div>
          </>
        )}

        {/* Connecting / Adding */}
        {(modal.type === 'connecting' || modal.type === 'adding') && (
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full border-2 border-[#2d7cff] border-t-transparent animate-spin mb-5" />
            <h3 className="text-[16px] font-bold text-[var(--color-text)] mb-1.5">{modal.title}</h3>
            <p className="text-[13px] text-[var(--color-muted)]">{modal.message}</p>
            <AppButton variant="secondary" onClick={onClose} className="mt-5">中断</AppButton>
          </div>
        )}
      </div>
    </div>
  );
}
