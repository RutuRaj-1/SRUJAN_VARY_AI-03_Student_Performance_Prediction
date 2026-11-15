/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F7FAF9',
        surface: {
          DEFAULT: '#FFFFFF',
          subtle: '#EEF8F7',
          muted: '#EFF5F3',
        },
        brand: {
          primary: '#237277',
          deep: '#123E40',
          dark: '#18575A',
          accent: '#2D8E92',
          mint: '#D9F0EE',
        },
        content: {
          primary: '#172825',
          secondary: '#40524E',
          muted: '#687A75',
        },
        border: {
          DEFAULT: '#DCE6E2',
          strong: '#BDCEC8',
        },
        semantic: {
          success: '#169C73',
          'success-soft': '#E8F7F1',
          warning: '#D89B22',
          'warning-soft': '#FFF6DF',
          danger: '#D96559',
          'danger-soft': '#FDECEA',
          info: '#2563EB',
          'info-soft': '#EAF2FF',
          ai: '#7457C8',
          'ai-soft': '#F2EEFF',
        },
      },
      borderRadius: {
        xs: '2px',
        sm: '4px',
        md: '6px',
        lg: '8px',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(18, 62, 64, 0.05)',
        card: '0 1px 3px 0 rgba(18, 62, 64, 0.08), 0 1px 2px -1px rgba(18, 62, 64, 0.08)',
      },
    },
  },
  plugins: [],
}
