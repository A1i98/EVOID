export interface SidebarItem {
  label: string;
  slug: string;
}

export interface SidebarGroup {
  label: string;
  items: SidebarItem[];
}

export type SidebarEntry = SidebarGroup | SidebarItem;

function isGroup(entry: SidebarEntry): entry is SidebarGroup {
  return 'items' in entry;
}

export { isGroup };

export const sidebar: SidebarEntry[] = [
  {
    label: 'Getting Started',
    items: [
      { label: 'Installation', slug: 'getting-started/installation' },
      { label: 'Quick Start', slug: 'getting-started/quickstart' },
      { label: 'Why EVOID?', slug: 'getting-started/why-evoid' },
      { label: 'What is IOP?', slug: 'getting-started/what-is-iop' },
    ],
  },
  {
    label: 'Learn',
    items: [
      { label: 'Intent', slug: 'learn/intent' },
      { label: 'Pipeline', slug: 'learn/pipeline' },
      { label: 'Processors', slug: 'learn/processors' },
      { label: 'Plugins', slug: 'learn/plugins' },
      { label: 'Configuration', slug: 'learn/configuration' },
    ],
  },
  {
    label: 'Syntax Styles',
    items: [
      { label: '@route', slug: 'styles/route' },
      { label: '@controller', slug: 'styles/controller' },
      { label: 'Native', slug: 'styles/native' },
    ],
  },
  {
    label: 'Tutorial',
    items: [
      { label: 'First Steps', slug: 'tutorial/first-steps' },
      { label: 'Path Parameters', slug: 'tutorial/path-params' },
      { label: 'Request Body', slug: 'tutorial/request-body' },
      { label: 'Intent Levels', slug: 'tutorial/intent-levels' },
      { label: 'Pipeline Extensions', slug: 'tutorial/pipeline-extensions' },
      { label: 'Parallel Execution', slug: 'tutorial/parallel' },
      { label: 'Inter-Service Communication', slug: 'tutorial/messaging' },
      { label: 'Custom Processors', slug: 'tutorial/custom-processors' },
      { label: 'Controller Style', slug: 'tutorial/controller-style' },
      { label: 'Native IOP', slug: 'tutorial/native-iop' },
    ],
  },
  { label: 'API Reference', slug: 'api' },
  { label: 'Examples', slug: 'examples' },
];

/** Flatten all sidebar entries into an ordered list of slugs for prev/next */
export function getAllSlugs(): string[] {
  const slugs: string[] = [];
  for (const entry of sidebar) {
    if (isGroup(entry)) {
      for (const item of entry.items) {
        slugs.push(item.slug);
      }
    } else {
      slugs.push(entry.slug);
    }
  }
  return slugs;
}
