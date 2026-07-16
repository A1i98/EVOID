# EvolveBeyond Organization Site — Design Spec

## [S1] Overview

Build a Modern Bento + Astro site for the EvolveBeyond organization at `/home/ali/Templates/Project/python/EvolveBeyond-Profile/`. The site serves as the parent brand for all projects (EVOID, XRayMOD, NvPak).

## [S2] Design Language

**Concept:** "Evolution Map" — the site should feel like a technical blueprint or evolution diagram. Clean, minimal, with subtle hand-drawn/sketch aesthetics.

**Color Palette (neutral, no project-specific colors):**
- Background: `#0a0a0a` (near-black)
- Text: `#e5e5e5` (light gray)
- Borders/lines: `#333333` (dark gray)
- Accent (logo glow only): `#8b5cf6` (muted purple)

**Typography:**
- Body: Inter
- Code/mono: JetBrains Mono (Nerd Font)

**Logo:** Minimalist black axolotl silhouette with subtle purple glow emanating from head. AI-generated image, optimized for web.

## [S3] Site Structure

Astro-based, single-page bento layout:

```
├── index.astro (landing)
│   ├── Hero: Logo + "EvolveBeyond" title + tagline
│   ├── Projects Grid: Bento cards for EVOID, XRayMOD, NvPak
│   └── About: Vision statement
├── blog/
│   └── index.astro (blog listing with language filter)
│   └── [slug].astro (individual post)
├── src/content/blog/ (markdown posts with `lang` field)
└── src/layouts/BaseLayout.astro
```

## [S4] Blog System (Multilingual)

- Content collection: `blog/`
- Each post has frontmatter: `title`, `description`, `lang` (`en` | `fa` | `mixed`), `date`
- Blog listing page filters by language via URL params (`?lang=en`, `?lang=fa`)
- Default shows all posts
- No separate directories per language

## [S5] SEO Standards

- `robots.txt` with sitemap reference
- Dynamic `sitemap.xml` via Astro endpoint
- Open Graph + Twitter Card meta tags
- Canonical URLs
- Semantic HTML (proper heading hierarchy)

## [S6] Rename docs-astro → docs

Rename the EVOID documentation folder from `docs-astro/` to `docs/` in the EVOID repo. Update all internal references.
