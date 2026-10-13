/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: { glow: '0 0 0 1px rgba(34,197,94,0.2), 0 20px 40px rgba(15,23,42,0.35)' },
    },
  },
  plugins: [],
};
