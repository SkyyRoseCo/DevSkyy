/** Redacted evidence serialization in the template contents' inert document.
 * Pass this function to page.evaluate. It never rewrites the live DOM or handlers.
 * This utility is not wired into any controlled live checkpoint by this change.
 */
function inertSnapshot() {
  const inertDocument = document.createElement('template').content.ownerDocument;
  const root = inertDocument.importNode(document.documentElement, true);
  root.querySelectorAll('script').forEach(node => {
    if (!node.src) node.textContent = '[INLINE SCRIPT REDACTED]';
  });
  root.querySelectorAll('input,textarea').forEach(node => {
    node.setAttribute('value', '[REDACTED]');
    if (node.tagName === 'TEXTAREA') node.textContent = '[REDACTED]';
  });
  [root, ...root.querySelectorAll('*')].forEach(node => {
    for (const attr of [...node.attributes]) {
      if (/^on/i.test(attr.name) || attr.name === 'srcset') {
        node.removeAttribute(attr.name);
      } else if (/nonce|token|security|cart.?item.?key|cart.?hash|session/i.test(attr.name)) {
        node.setAttribute(attr.name, '[REDACTED]');
      } else if (['href', 'src', 'action', 'poster'].includes(attr.name)) {
        try {
          const url = new URL(attr.value, location.href);
          url.search = '';
          url.hash = '';
          node.setAttribute(attr.name, url.href);
        } catch {
          node.setAttribute(attr.name, attr.value.split(/[?#]/)[0]);
        }
      }
    }
  });
  return '<!doctype html>' + root.outerHTML;
}

module.exports = { inertSnapshot };
