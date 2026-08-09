/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f3ff',
          100: '#d9e2ff',
          200: '#b3c6ff',
          300: '#809fff',
          400: '#4d73ff',
          500: '#165DFF',
          600: '#0e4bd9',
          700: '#093aa6',
          800: '#062b73',
          900: '#031a40',
        },
        secondary: {
          50: '#f9f0ff',
          100: '#efd9ff',
          200: '#ddb3ff',
          300: '#c680ff',
          400: '#ad4dff',
          500: '#722ED1',
          600: '#5a23a8',
          700: '#431a7d',
          800: '#2d1152',
          900: '#170728',
        },
        accent: {
          orange: '#FF7D00',
          green: '#00B42A',
        },
        dark: {
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}

