import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import Navbar from './components/Navbar';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'iGEM Dry Lab',
  description: 'iGEM Dry Lab Monitor',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 selection:bg-blue-100 selection:text-blue-900 relative">
        {/* Ambient Background Gradient for modern aesthetic */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-100/40 blur-[100px] pointer-events-none -z-10" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-teal-100/30 blur-[100px] pointer-events-none -z-10" />
        
        <div className="fixed top-0 inset-x-0 z-50">
          <Navbar />
        </div>
        
        <main className="flex-1 w-full max-w-[1400px] mx-auto mt-32 px-6 pb-12 relative z-0">
          {children}
        </main>
      </body>
    </html>
  );
}
