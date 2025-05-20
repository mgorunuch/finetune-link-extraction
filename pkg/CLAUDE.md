# Package Directory Guidelines

This directory contains all packages created for the fine-tuning link extraction project.

## Package Structure
- Each package should have its own subdirectory
- Maintain consistent documentation across packages
- Follow modular design principles
- Include tests for all package functionality

## Package Standards
- Clear API interfaces
- Comprehensive error handling
- Performance optimization where needed
- Thorough documentation (README.md in each package)

## Packages

### html_extractor
A simple headless browser-based tool that:
- Opens web pages using Playwright
- Executes JavaScript on loaded pages to mark content
- Extracts and saves HTML content to specified file paths
- Provides both CLI and Python API interfaces