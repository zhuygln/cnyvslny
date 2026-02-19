/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        surface: '#0d0221',
        'surface-raised': '#1a0a2e',
        'surface-card': '#150833',
        accent: '#e65100',
        'accent-light': '#ff8f00',
        'text-primary': '#f0e6ff',
        'text-muted': '#b8a9cc',
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        serif: ['DM Serif Display', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};
