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
      { label: 'Architecture', slug: 'getting-started/architecture' },
      { label: 'What is IOP?', slug: 'getting-started/what-is-iop' },
      { label: 'Why EVOID?', slug: 'getting-started/why-evoid' },
      { label: 'EVOID vs Others', slug: 'getting-started/comparison' },
      { label: 'Deployment', slug: 'getting-started/deployment' },
      { label: 'FAQ', slug: 'getting-started/faq' },
    ],
  },
  {
    label: 'Learn',
    items: [
      { label: 'Intent', slug: 'learn/intent' },
      { label: 'Pipeline', slug: 'learn/pipeline' },
      { label: 'Processors', slug: 'learn/processors' },
      { label: 'Schema Export', slug: 'learn/schema-export' },
      { label: 'Plugin Hooks', slug: 'learn/plugin-hooks' },
      { label: 'Plugins', slug: 'learn/plugins' },
      { label: 'Plugin Standard', slug: 'learn/plugin-standard' },
      { label: 'Testing', slug: 'learn/testing' },
      { label: 'Configuration', slug: 'learn/configuration' },
      { label: 'Python-Native Config', slug: 'learn/python-config' },
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
      { label: 'Path Parameters', slug: 'tutorial/path-params' },
      { label: 'Query Parameter Models', slug: 'tutorial/query-param-models' },
      { label: 'Body Multiple Parameters', slug: 'tutorial/body-multiple-params' },
      { label: 'Body Fields', slug: 'tutorial/body-fields' },
      { label: 'Body Nested Models', slug: 'tutorial/body-nested-models' },
      { label: 'Body Updates', slug: 'tutorial/body-updates' },
      { label: 'Response Status Code', slug: 'tutorial/response-status-code' },
      { label: 'Handling Errors', slug: 'tutorial/handling-errors' },
      { label: 'Path Operation Config', slug: 'tutorial/path-operation-config' },
      { label: 'Metadata', slug: 'tutorial/metadata' },
      { label: 'Testing', slug: 'tutorial/testing' },
      { label: 'Pipeline Inspection', slug: 'tutorial/pipeline-inspection' },
      { label: 'Parallel Execution', slug: 'tutorial/parallel' },
      { label: 'Microservices Without Overhead', slug: 'tutorial/microservices' },
      { label: 'Bigger Applications', slug: 'tutorial/bigger-applications' },
    ],
  },
  {
    label: 'Validation & Serialization',
    items: [
      { label: 'Schema Examples', slug: 'tutorial/schema-examples' },
      { label: 'Validation', slug: 'tutorial/validation' },
      { label: 'Serialization', slug: 'tutorial/serialization' },
      { label: 'Debugging', slug: 'tutorial/debugging' },
    ],
  },
  {
    label: 'Web Adapter Patterns',
    items: [
      { label: 'Custom Adapters', slug: 'tutorial/custom-adapters' },
      { label: 'Cookie Parameters', slug: 'tutorial/cookie-params' },
      { label: 'Header Parameters', slug: 'tutorial/header-params' },
      { label: 'Form Data', slug: 'tutorial/form-data' },
      { label: 'File Upload', slug: 'tutorial/file-upload' },
      { label: 'CORS', slug: 'tutorial/cors' },
      { label: 'Static Files', slug: 'tutorial/static-files' },
      { label: 'Streaming', slug: 'tutorial/streaming' },
    ],
  },
  {
    label: 'Patterns',
    items: [
      { label: 'Dependency Injection', slug: 'tutorial/dependency-injection' },
      { label: 'Middleware Patterns', slug: 'tutorial/middleware-patterns' },
      { label: 'Response Validation', slug: 'tutorial/response-validation' },
      { label: 'Testing Your API', slug: 'tutorial/testing-system' },
      { label: 'AI Agent Integration', slug: 'tutorial/ai-agent' },
      { label: 'Advanced Plugins', slug: 'tutorial/advanced-plugins' },
    ],
  },
  { label: 'API Reference', slug: 'api' },
  { label: 'Examples', slug: 'examples' },
  { label: 'Changelog', slug: 'changelog' },
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
