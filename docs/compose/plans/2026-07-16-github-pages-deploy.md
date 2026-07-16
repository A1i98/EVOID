# GitHub Pages Deployment Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task.

**Goal:** Deploy EVOID documentation to GitHub Pages on a dedicated branch, with proper SEO and no AI artifact traces.

**Architecture:** Documentation site (Astro + Starlight) lives in `docs-astro/` subfolder. Deployed via GitHub Actions to `gh-pages` branch. AI-related files excluded from git entirely.

**Tech Stack:** Astro 7, GitHub Actions, GitHub Pages, Pagefind (search)

---

## Global Constraints

- Site URL: `https://evolvebeyond.github.io/EVOID/`
- Branch for pages: `gh-pages`
- No AI files in git: `.agents/`, `.claude/`, `.mimocode/`, `AGENTS.md`, `CLAUDE.md`, `skills-lock.json`
- SEO requirements: meta tags, sitemap, robots.txt, Open Graph
- Node.js 20 for build

---

## Task 1: Clean AI Files from Git

**Files:**
- Modify: `.gitignore`
- Delete: `docs-astro/AGENTS.md`, `docs-astro/CLAUDE.md`
- Delete: `skills-lock.json`

**Steps:**

- [ ] **Step 1: Update .gitignore**

Add to `.gitignore`:
```
# AI Agent Files
.agents/
.claude/
.mimocode/
AGENTS.md
CLAUDE.md
skills-lock.json
```

- [ ] **Step 2: Remove AI files from tracking**

```bash
git rm --cached docs-astro/AGENTS.md docs-astro/CLAUDE.md skills-lock.json
git rm --cached -r .agents/ .claude/ .mimocode/ 2>/dev/null || true
```

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: remove AI agent files from tracking"
```

---

## Task 2: Add GitHub Pages Workflow

**Files:**
- Create: `.github/workflows/deploy-docs.yml`

**Steps:**

- [ ] **Step 1: Create workflow file**

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'docs-astro/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: docs-astro/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: docs-astro

      - name: Build
        run: npm run build
        working-directory: docs-astro

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs-astro/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy-docs.yml
git commit -m "ci: add GitHub Pages deployment workflow"
```

---

## Task 3: Add SEO Essentials

**Files:**
- Create: `docs-astro/public/robots.txt`
- Create: `docs-astro/public/sitemap.xml`
- Modify: `docs-astro/src/layouts/DocsLayout.astro` (meta tags)
- Modify: `docs-astro/src/layouts/MainLayout.astro` (meta tags)

**Steps:**

- [ ] **Step 1: Create robots.txt**

```txt
User-agent: *
Allow: /
Sitemap: https://evolvebeyond.github.io/EVOID/sitemap.xml
```

- [ ] **Step 2: Create dynamic sitemap via Astro endpoint**

Create `docs-astro/src/pages/sitemap.xml.ts`:
```ts
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const docs = await getCollection('docs');
  const urls = docs.map(doc =>
    `<url><loc>https://evolvebeyond.github.io/EVOID/docs/${doc.id}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>`
  );

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://evolvebeyond.github.io/EVOID/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>
  ${urls.join('\n  ')}
</urlset>`;

  return new Response(sitemap, {
    headers: { 'Content-Type': 'application/xml' },
  });
};
```

- [ ] **Step 3: Add SEO meta tags to DocsLayout**

In `DocsLayout.astro`, ensure `<head>` has:
```html
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:type" content="website" />
<meta property="og:url" content={`https://evolvebeyond.github.io/EVOID/docs/${Astro.url.pathname}`} />
<meta name="twitter:card" content="summary" />
<link rel="canonical" href={`https://evolvebeyond.github.io/EVOID${Astro.url.pathname}`} />
```

- [ ] **Step 4: Add SEO meta tags to MainLayout**

Same pattern for the landing page.

- [ ] **Step 5: Commit**

```bash
git add docs-astro/public/robots.txt docs-astro/src/pages/sitemap.xml.ts
git add docs-astro/src/layouts/DocsLayout.astro docs-astro/src/layouts/MainLayout.astro
git commit -m "feat: add SEO essentials (robots.txt, sitemap, meta tags)"
```

---

## Task 4: Configure GitHub Pages Branch

**Steps:**

- [ ] **Step 1: Enable GitHub Pages via Actions**

In GitHub repo Settings → Pages → Source → Select "GitHub Actions"

- [ ] **Step 2: Verify deployment**

Push to main, check Actions tab for successful deployment.

- [ ] **Step 3: Verify site**

Visit `https://evolvebeyond.github.io/EVOID/` and check:
- Landing page loads
- Docs pages load with sidebar
- Search works
- Dark/light theme toggle works
- Mobile responsive

---

## Task 5: Clean Up and Final Commit

**Files:**
- Modify: `docs-astro/.gitignore` (add dist/)

**Steps:**

- [ ] **Step 1: Ensure docs-astro/.gitignore has dist/**

```
dist/
.astro/
node_modules/
```

- [ ] **Step 2: Final commit**

```bash
git add -A
git commit -m "chore: final cleanup for GitHub Pages deployment"
git push origin main
```

---

## Verification Checklist

- [ ] No AI files in git history after cleanup
- [ ] GitHub Actions workflow runs on push to main
- [ ] Site deploys to `https://evolvebeyond.github.io/EVOID/`
- [ ] All 24 docs pages load correctly
- [ ] Landing page loads correctly
- [ ] Search functionality works
- [ ] Dark/light theme toggle works
- [ ] Mobile responsive
- [ ] SEO: sitemap.xml accessible
- [ ] SEO: robots.txt accessible
- [ ] SEO: meta tags present in HTML
