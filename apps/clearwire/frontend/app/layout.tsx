import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = { title: 'Clearwire | Authorized Wireless Intelligence', description: 'Passive, permission-based wireless telemetry dashboard.' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
