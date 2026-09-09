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
        // 家属小程序（移动端原型配色，青绿系，对应 Ardot 家属小程序页）
        fam: {
          teal: '#10B9A8', // 主色青绿
          deep: '#0B8C80', // 深青
          green: '#07C160', // 微信绿
          red: '#FF5C5C', // 预警红
          orange: '#F0973B', // 提醒橙
          blue: '#4C8DFF', // 信息蓝
          bg: '#F4F6F8', // 页面底
          arrow: '#C4C9D2', // 列表箭头灰
        },
      },
    },
  },
  plugins: [],
}
