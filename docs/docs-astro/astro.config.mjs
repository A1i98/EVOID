// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { unified } from '@astrojs/markdown-remark';
import remarkAdmonitions from './src/plugins/remark-admonitions.mjs';
import remarkTabs from './src/plugins/remark-tabs.mjs';

export default defineConfig({
  site: 'https://evolvebeyond.github.io/EVOID/',
  markdown: {
    remarkPlugins: [remarkAdmonitions, remarkTabs],
    processor: unified(),
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
