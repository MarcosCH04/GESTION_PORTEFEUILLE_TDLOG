/** @type {import('tailwindcss').Config} */
export default {
  /* Content paths tell Tailwind which files to scan for class names */
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a4bcfd',
          400: '#8098f9',
          500: '#667eea',
          600: '#5568d3',
          700: '#4451b8',
          800: '#3a4294',
          900: '#333876',
        },
      },
    },
  },
  plugins: [],
}