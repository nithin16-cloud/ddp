tailwind.config = {
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        body: ['Inter', -apple-system, 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Inter', -apple-system, 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      },
      colors: {
        app: {
          bg: 'var(--bg-app)',
          surface: 'var(--surface)',
          'surface-raised': 'var(--surface-raised)',
          'surface-subtle': 'var(--surface-subtle)',
          border: 'var(--border)',
          'border-subtle': 'var(--border-subtle)',
          'border-strong': 'var(--border-strong)',
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)'
        },
        brand: {
          DEFAULT: 'var(--accent)',
          hover: 'var(--accent-hover)',
          subtle: 'var(--accent-subtle)',
          text: 'var(--accent-text)'
        }
      }
    }
  }
};
