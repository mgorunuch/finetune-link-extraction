/**
 * HTML Extractor and Enhancer
 *
 * This script is injected into HTML pages to extract and enhance HTML content.
 * It identifies various elements, adds metadata, and prepares the content
 * for further processing.
 */

(function () {
  function *prefixId(prefix) {
    let i = 0;
    while (true) {
      i += 1;
      yield `${prefix}-${i}`;
    }
  }

  const idGen = prefixId('node');

  function isPreSkipped(el) {
    return [
      'script',
      'style',
      'link',
      'meta',
      'title',
      'svg',
      'path',
      'rect',
      'circle',
      'ellipse',
      'line',
      'polygon',
    ].includes(el.tagName.toLowerCase());
  }

  function processDeep(el) {
    if (isPreSkipped(el)) {
      return;
    }

    for (let i = 0; i < el.children.length; i++) {
      const child = el.children[i];
      processDeep(child);
    }

    if (!!getEventListeners(el)?.click?.length) {
      const id = idGen.next().value;
      el.setAttribute('data-node-id', id);
      el.setAttribute('data-node-type', 'event');
      return;
    }

    if (el.getAttribute('href')) {
      const id = idGen.next().value;
      el.setAttribute('data-node-id', id);
      el.setAttribute('data-node-type', 'link');
      return;
    }
  }

  processDeep(document.body);
})();
