/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        line: '#d8cfc1',
        sage: '#6f8f74',
        'sage-deep': '#59735d',
        'sage-tint': '#eaf2ea',
        alert: '#c65a4a',
        'alert-tint': '#f8e3de',
        amber: '#a87a3e',
        'amber-tint': '#f5ead7',
        cream: '#f6f2e8',
        apricot: '#ebd9bc',
        ink: '#2f2a24',
        'ink-sub': '#6f655b',
        'ink-hint': '#9a8f83',
      },
    },
  },
  plugins: [],
}
