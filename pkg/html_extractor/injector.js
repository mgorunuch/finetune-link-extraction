/**
 * HTML Extractor and Enhancer
 *
 * This script is injected into HTML pages to extract and enhance HTML content.
 * It identifies various elements, adds metadata, and prepares the content
 * for further processing.
 */

(function () {
  // Configuration object to control behavior
  const config = {
    markHeadings: true,
    enhanceLinks: true,
    processTables: true,
    extractMetadata: true,
    addClassesToElements: true,
  };

  // Result object to store extraction data
  const extractionResult = {
    metadata: {},
    statistics: {
      headings: 0,
      links: 0,
      images: 0,
      tables: 0,
      paragraphs: 0,
    },
    enhancementApplied: false,
  };

  /**
   * Enhances links in the document
   * - Adds data attributes for link type
   * - Identifies external vs internal links
   * - Marks social media links
   */
  function enhanceLinks() {
    const links = document.getElementsByTagName('a');
    const currentDomain = window.location.hostname;

    // Social media domains
    const socialDomains = [
      'facebook.com',
      'twitter.com',
      'instagram.com',
      'linkedin.com',
      'youtube.com',
      'pinterest.com',
      'tiktok.com',
      'reddit.com',
    ];

    Array.from(links).forEach((link) => {
      // Skip links without href
      if (!link.hasAttribute('href')) return;

      const href = link.href;
      let linkType = 'unknown';

      // Check if link is external or internal
      try {
        const linkDomain = new URL(href).hostname;

        if (!linkDomain || linkDomain === currentDomain) {
          linkType = 'internal';
        } else {
          linkType = 'external';

          // Check if it's a social media link
          if (socialDomains.some((domain) => linkDomain.includes(domain))) {
            linkType = 'social';

            // Identify which social platform
            for (const domain of socialDomains) {
              if (linkDomain.includes(domain)) {
                link.setAttribute('data-social-platform', domain.split('.')[0]);
                break;
              }
            }
          }
        }
      } catch (_) { // eslint-disable-line no-unused-vars
        // If URL parsing fails, it's likely a relative link
        linkType = 'internal';
      }

      // Add data attribute for link type
      link.setAttribute('data-link-type', linkType);

      // Add class for styling
      link.classList.add(`html-extractor-${linkType}-link`);

      // Increment link counter
      extractionResult.statistics.links++;
    });
  }

  /**
   * Enhances headings in the document
   * - Adds IDs for navigation
   * - Adds level information
   */
  function enhanceHeadings() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');

    Array.from(headings).forEach((heading, index) => {
      const level = heading.tagName.charAt(1);
      const headingText = heading.textContent.trim();

      // Generate an ID if none exists
      if (!heading.id) {
        const idText = headingText
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/(^-|-$)/g, '');

        heading.id = `heading-${idText || index}`;
      }

      // Add data attributes
      heading.setAttribute('data-heading-level', level);
      heading.setAttribute('data-heading-index', index);

      // Add class
      heading.classList.add('html-extractor-heading');
      heading.classList.add(`html-extractor-h${level}`);

      // Increment heading counter
      extractionResult.statistics.headings++;
    });
  }

  /**
   * Enhances tables in the document
   * - Adds metadata
   * - Improves accessibility
   */
  function enhanceTables() {
    const tables = document.getElementsByTagName('table');

    Array.from(tables).forEach((table, index) => {
      // Add identifier
      table.setAttribute('data-table-index', index);
      table.classList.add('html-extractor-table');

      // Add caption if none exists
      if (!table.querySelector('caption')) {
        const caption = document.createElement('caption');
        caption.textContent = `Table ${index + 1}`;
        caption.style.display = 'none'; // Hide visually but keep for screen readers
        table.prepend(caption);
      }

      // Add header scope attributes if there's a thead
      const headerCells = table.querySelectorAll('thead th');
      headerCells.forEach((cell) => {
        if (!cell.hasAttribute('scope')) {
          cell.setAttribute('scope', 'col');
        }
      });

      // Increment table counter
      extractionResult.statistics.tables++;
    });
  }

  /**
   * Extracts metadata from the document
   */
  function extractMetadata() {
    const metadata = {};

    // Title
    metadata.title = document.title || '';

    // Meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    metadata.description = metaDesc ? metaDesc.getAttribute('content') : '';

    // Meta keywords
    const metaKeywords = document.querySelector('meta[name="keywords"]');
    metadata.keywords = metaKeywords ? metaKeywords.getAttribute('content') : '';

    // Open Graph data
    metadata.og = {};
    document.querySelectorAll('meta[property^="og:"]').forEach((meta) => {
      const property = meta.getAttribute('property').substring(3);
      metadata.og[property] = meta.getAttribute('content');
    });

    // Author
    const metaAuthor = document.querySelector('meta[name="author"]');
    metadata.author = metaAuthor ? metaAuthor.getAttribute('content') : '';

    // URL
    metadata.url = window.location.href;

    // Store in result
    extractionResult.metadata = metadata;
  }

  /**
   * Adds classes to other important elements
   */
  function enhanceOtherElements() {
    // Enhance paragraphs
    const paragraphs = document.getElementsByTagName('p');
    Array.from(paragraphs).forEach((p, index) => {
      p.classList.add('html-extractor-paragraph');
      p.setAttribute('data-paragraph-index', index);
      extractionResult.statistics.paragraphs++;
    });

    // Enhance images
    const images = document.getElementsByTagName('img');
    Array.from(images).forEach((img, index) => {
      img.classList.add('html-extractor-image');
      img.setAttribute('data-image-index', index);

      // Add alt text if missing
      if (!img.hasAttribute('alt')) {
        img.alt = img.src.split('/').pop() || `Image ${index}`;
      }

      extractionResult.statistics.images++;
    });

    // Mark main content area if it exists
    const mainSelectors = ['main', 'article', '[role="main"]', '#content', '.content'];
    for (const selector of mainSelectors) {
      const mainElement = document.querySelector(selector);
      if (mainElement) {
        mainElement.classList.add('html-extractor-main-content');
        break;
      }
    }
  }

  /**
   * Main function to enhance the HTML document
   */
  function enhanceDocument() {
    try {
      // Extract metadata first
      if (config.extractMetadata) {
        extractMetadata();
      }

      // Enhance various elements
      if (config.enhanceLinks) {
        enhanceLinks();
      }

      if (config.markHeadings) {
        enhanceHeadings();
      }

      if (config.processTables) {
        enhanceTables();
      }

      if (config.addClassesToElements) {
        enhanceOtherElements();
      }

      // Mark as enhanced
      document.documentElement.setAttribute('data-html-extractor', 'enhanced');
      extractionResult.enhancementApplied = true;

      // Add a hidden element with result data
      const resultElement = document.createElement('script');
      resultElement.id = 'html-extractor-data';
      resultElement.type = 'application/json';
      resultElement.textContent = JSON.stringify(extractionResult);
      resultElement.style.display = 'none';
      document.body.appendChild(resultElement);

      return true;
    } catch (error) {
      console.error('HTML Extractor error:', error);

      // Add error information to the document
      const errorElement = document.createElement('script');
      errorElement.id = 'html-extractor-error';
      errorElement.type = 'application/json';
      errorElement.textContent = JSON.stringify({ error: error.message });
      document.body.appendChild(errorElement);

      return false;
    }
  }

  // Execute enhancement
  return enhanceDocument();
})();
