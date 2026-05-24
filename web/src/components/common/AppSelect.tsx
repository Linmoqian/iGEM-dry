import { useState, useRef, useEffect, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
  icon?: ReactNode;
}

interface AppSelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  icon?: ReactNode;
  className?: string;
}

export default function AppSelect({
  options,
  value,
  onChange,
  placeholder = '请选择',
  icon,
  className = '',
}: AppSelectProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((o) => o.value === value);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`
          inline-flex items-center gap-2
          h-10 px-3 min-w-[180px]
          bg-surface border border-border rounded-[10px]
          text-[13px] text-left
          transition-colors duration-150
          hover:border-primary
          ${open ? 'border-primary ring-1 ring-primary/20' : ''}
        `.trim()}
      >
        {icon && <span className="shrink-0 text-muted">{icon}</span>}
        <span className={`flex-1 truncate ${selectedOption ? 'text-text' : 'text-muted'}`}>
          {selectedOption?.label ?? placeholder}
        </span>
        <ChevronDown
          size={16}
          className={`shrink-0 text-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div
          className="
            absolute z-50 top-full left-0 mt-1 w-full
            bg-surface border border-border rounded-[10px]
            shadow-float py-1 max-h-60 overflow-y-auto
          "
        >
          {options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value);
                setOpen(false);
              }}
              className={`
                w-full flex items-center gap-2
                px-3 py-2 text-[13px] text-left
                transition-colors duration-100
                ${option.value === value
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-text hover:bg-bg-soft'}
              `.trim()}
            >
              {option.icon && <span className="shrink-0">{option.icon}</span>}
              <span className="truncate">{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
