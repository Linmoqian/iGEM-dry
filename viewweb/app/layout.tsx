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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#050714] text-slate-200 selection:bg-cyan-500/30 selection:text-cyan-100 relative">
        {/* Tech Grid Background and Particles */}
        <div className="fixed inset-0 bg-[#050714] -z-30"></div>
        <div className="fixed inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_40%,#000_10%,transparent_100%)] pointer-events-none -z-20"></div>
        
        {/* Ambient Dark Tech Glowing */}
        <div className="fixed top-[0%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/20 blur-[120px] pointer-events-none -z-10" />
        <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-900/15 blur-[120px] pointer-events-none -z-10" />
        
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
