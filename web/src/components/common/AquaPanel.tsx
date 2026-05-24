import type { ReactNode } from 'react';

interface AquaPanelProps {
  children: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}

export default function AquaPanel({ children, className = '', title, subtitle }: AquaPanelProps) {
  return (
    <section
      className={`
        bg-surface rounded-2xl border border-border-subtle
        shadow-card p-5
        ${className}
      `.trim()}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title && (
            <h3 className="text-[16px] font-bold text-text leading-snug">{title}</h3>
          )}
          {subtitle && (
            <p className="text-[12px] text-muted mt-0.5">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </section>
  );
}
