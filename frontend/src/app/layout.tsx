import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Ludo AI - Generative Boards & Smart Agents',
  description: 'Play Ludo with AI opponents, custom themes, and Hinglish commentary',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}