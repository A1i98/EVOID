/**
 * Remark plugin to transform MyST-style tabs:
 *   === "Tab 1"
 *       Content 1
 *   === "Tab 2"
 *       Content 2
 *
 * Handles indented code blocks (``` markers become literal text
 * under 4-space indent) by reconstructing proper code block nodes.
 */
export default function remarkTabs() {
  return (tree) => {
    const newChildren = [];
    let i = 0;

    while (i < tree.children.length) {
      const node = tree.children[i];

      if (node.type === 'paragraph') {
        const firstChild = node.children?.[0];
        if (firstChild && firstChild.type === 'text') {
          const text = firstChild.value;
          const match = text.match(/^===\s*[\u0022\u201c]([^\u0022\u201d]*)[\u0022\u201d]/);
          if (match) {
            const tabs = [];
            let j = i;

            while (j < tree.children.length) {
              const current = tree.children[j];
              if (current.type === 'paragraph') {
                const currentText = current.children?.[0]?.value || '';
                const tabMatch = currentText.match(/^===\s*[\u0022\u201c]([^\u0022\u201d]*)[\u0022\u201d]/);
                if (tabMatch) {
                  j++;
                  const contentNodes = [];
                  while (j < tree.children.length) {
                    const next = tree.children[j];
                    if (next.type === 'paragraph') {
                      const nextText = next.children?.[0]?.value || '';
                      if (/^===\s*[\u0022\u201c]/.test(nextText)) break;
                      if (/^\s{4}/.test(nextText)) {
                        contentNodes.push({ type: 'text', value: nextText.replace(/^    /, '') });
                        j++;
                        continue;
                      }
                      if (nextText.trim() === '') { j++; continue; }
                    }
                    // Handle indented code blocks (``` as literal text)
                    if (next.type === 'code') {
                      const val = next.value || '';
                      const fenceMatch = val.match(/^```(\w*)\n([\s\S]*)\n```$/);
                      if (fenceMatch) {
                        contentNodes.push({
                          type: 'code',
                          lang: fenceMatch[1] || null,
                          value: fenceMatch[2],
                        });
                      } else {
                        contentNodes.push(next);
                      }
                      j++;
                      continue;
                    }
                    break;
                  }

                  let contentText = contentNodes
                    .filter(n => n.type === 'text')
                    .map(n => n.value)
                    .join('\n')
                    .trim();

                  tabs.push({
                    title: tabMatch[1],
                    contentText,
                    codeBlocks: contentNodes.filter(n => n.type === 'code'),
                  });
                  continue;
                }
              }
              break;
            }

            if (tabs.length >= 2) {
              const id = 'tabs-' + Math.random().toString(36).slice(2, 8);

              let navHtml = '<div class="tabs"><div class="tabs-nav">';
              tabs.forEach(function(tab, idx) {
                navHtml += '<button class="tab-btn' + (idx === 0 ? ' active' : '') + '" data-tab="' + id + '-' + idx + '">' + tab.title + '</button>';
              });
              navHtml += '</div>';

              newChildren.push({ type: 'html', value: navHtml });

              tabs.forEach(function(tab, idx) {
                newChildren.push({ type: 'html', value: '<div class="tab-panel' + (idx === 0 ? ' active' : '') + '" id="' + id + '-' + idx + '">' });
                if (tab.contentText) {
                  newChildren.push({ type: 'paragraph', children: [{ type: 'text', value: tab.contentText }] });
                }
                for (const cb of tab.codeBlocks) {
                  newChildren.push(cb);
                }
                newChildren.push({ type: 'html', value: '</div>' });
              });

              newChildren.push({ type: 'html', value: '</div>' });
              i = j;
              continue;
            }
          }
        }
      }

      newChildren.push(node);
      i++;
    }

    tree.children = newChildren;
  };
}
