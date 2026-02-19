import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://cnyvslny.info',
  base: '/',
  integrations: [tailwind()],
});
