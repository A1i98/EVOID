const ADMONITION_TYPES = ['tip', 'info', 'note', 'warning', 'danger'];

/**
 * Remark plugin to transform MyST-style admonitions:
 *   !!! tip "Title"
 *       Content here
 */
export default function remarkAdmonitions() {
  return (tree) => {
    const newChildren = [];
    for (const node of tree.children) {
      if (node.type === 'paragraph') {
        const firstChild = node.children?.[0];
        if (firstChild && firstChild.type === 'text') {
          const text = firstChild.value;
          // Match both ASCII quotes and smart/curly quotes (\u201c \u201d)
          const match = text.match(/^!!!\s+(\w+)\s*[\u0022\u201c]([^\u0022\u201d]*)[\u0022\u201d]/);
          if (match) {
            const [, type, title] = match;
            if (ADMONITION_TYPES.includes(type)) {
              const afterMatch = text.slice(match[0].length);
              const contentText = afterMatch.replace(/^\n\s{4}/, '\n').replace(/\n\s{4}/g, '\n').trim();
              newChildren.push({ type: 'html', value: '<aside class="admonition admonition--' + type + '"><div class="admonition-title">' + title + '</div>' });
              if (contentText) {
                newChildren.push({ type: 'paragraph', children: [{ type: 'text', value: contentText }] });
              }
              newChildren.push({ type: 'html', value: '</aside>' });
              continue;
            }
          }
        }
      }
      newChildren.push(node);
    }
    tree.children = newChildren;
  };
}
