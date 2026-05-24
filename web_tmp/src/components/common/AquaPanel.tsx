import type { ReactNode } from 'react';

interface AquaPanelProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export default function AquaPanel({ title, subtitle, children, className = '', action }: AquaPanelProps) {
  return (
    <div className={`aqua-panel p-6 ocean-wave ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between gap-4 mb-5">
          <div>
            {title && <h3 className="text-[16px] font-bold text-[var(--color-text)]">{title}</h3>}
            {subtitle && <p className="text-[12px] text-[var(--color-muted)] mt-1">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}
