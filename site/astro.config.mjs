import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://zhuygln.github.io',
  base: '/cnyvslny',
  integrations: [tailwind()],
});
