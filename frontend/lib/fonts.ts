import { Cinzel } from 'next/font/google'

// Operator Console typography (frontend/app/admin) — see docs/handoff.
// Authorized per CLAUDE.md §6 (2026-07-10): Archivo, Hanken Grotesk, Anton, Cinzel, Inter
export const cinzel = Cinzel({
  subsets: ['latin'],
  variable: '--font-cinzel',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})
