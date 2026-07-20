// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { unified } from '@astrojs/markdown-remark';
import remarkAdmonitions from './src/plugins/remark-admonitions.mjs';
import remarkTabs from './src/plugins/remark-tabs.mjs';
import mermaid from 'astro-mermaid';

export default defineConfig({
  site: 'https://evolvebeyond.github.io',
  base: '/EVOID/',
  markdown: {
    remarkPlugins: [remarkAdmonitions, remarkTabs],
    processor: unified(),
  },
  integrations: [
    mermaid({
      theme: 'dark',
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
});
