/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      colors: {
        bg:      '#0A0E1A',
        surface: '#111827',
        border:  '#1F2937',
        high:    '#EF4444',
        medium:  '#F59E0B',
        low:     '#10B981',
        accent:  '#6366F1',
        muted:   '#6B7280',
      },
      animation: {
        'fade-in':  'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.4s ease forwards',
      },
      keyframes: {
        fadeIn:  { from: { opacity: '0' },                           to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(12px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}