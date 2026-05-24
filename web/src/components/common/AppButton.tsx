import type { ReactNode, ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface AppButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  icon?: ReactNode;
  className?: string;
  loading?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-primary text-text-inverse hover:bg-primary-strong shadow-card hover:shadow-hover',
  secondary:
    'bg-surface-strong text-text border border-border hover:bg-bg-soft',
  ghost:
    'bg-transparent text-muted hover:bg-bg-soft hover:text-text',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-[12px] gap-1 rounded-[8px]',
  md: 'h-10 px-5 text-[13px] gap-1.5 rounded-[10px]',
  lg: 'h-11 px-6 text-[14px] gap-2 rounded-[12px]',
};

export default function AppButton({
  variant = 'primary',
  size = 'md',
  children,
  icon,
  className = '',
  loading = false,
  disabled,
  ...rest
}: AppButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center justify-center
        font-semibold whitespace-nowrap
        transition-all duration-150
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `.trim()}
      disabled={disabled || loading}
      {...rest}
    >
      {loading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        icon
      )}
      {children}
    </button>
  );
}
