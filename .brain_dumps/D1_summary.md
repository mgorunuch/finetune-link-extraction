# Brain Dump D1 Summary

## Project Goal
- Create custom dataset for link extraction instead of using predefined datasets

## Problem Statement
- Context-aware extraction is challenging (understanding what elements do without surrounding context)
- Need context around HTML elements for proper understanding

## Proposed Approach
1. Use headless browser in headful mode
2. Mark content with flags
3. Extract links with appropriate context including:
   - CSS classes on parent elements
   - SEO information
   - Tag names
   - Text from surrounding elements

## Current Status
- Basic workflow established:
  - Run Chromeless browser
  - Mark discovered links with tags
  - Extract information using XPath/CSS selectors
  - Capture words from surrounding elements (parent and siblings)

## Next Steps
- Refine extraction methodology
- Improve context collection