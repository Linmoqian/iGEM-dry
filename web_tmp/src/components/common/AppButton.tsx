import type { ReactNode, ButtonHTMLAttributes } from 'react';

interface AppButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  children: ReactNode;
  icon?: ReactNode;
}

export default function AppButton({ variant = 'primary', children, icon, className = '', ...props }: AppButtonProps) {
  const cls = variant === 'primary' ? 'aqua-button' : variant === 'secondary' ? 'aqua-button-secondary' : 'aqua-button-danger';
  return <button className={`${cls} ${className}`} {...props}>{icon}{children}</button>;
}
