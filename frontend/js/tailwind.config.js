tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['Plus Jakarta Sans', 'Inter', 'Segoe UI', 'Roboto', 'sans-serif'],
        body: ['Inter', 'Plus Jakarta Sans', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'monospace']
      },
      colors: {
        space: {
          950: '#04070D',
          900: '#07090E',
          850: '#0C111C',
          800: '#121826',
          700: '#1A2234'
        },
        tealAccent: {
          400: '#00F0FF',
          500: '#00E5A3',
          600: '#00B380'
        },
        amberAccent: {
          400: '#FFB340',
          500: '#FF9F0A',
          600: '#D97706'
        },
        indigoAccent: {
          400: '#7579FF',
          500: '#5E5CE6',
          600: '#4F46E5'
        }
      }
    }
  }
};
