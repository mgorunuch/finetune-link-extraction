# HTML Extractor

## Purpose
A simple headless browser-based tool that extracts and enhances HTML content.

## File Structure
- `injector.js`: JavaScript code to be injected into HTML pages for enhancement
- `runner.py`: Main script that loads HTML, injects JavaScript, and exports the processed HTML
- `package.json`: NPM package configuration with script commands
- `taskfile.yml`: Task runner configuration for common operations

Linting and formatting configurations are located in the shared `/pkg/configs` directory:
- `eslint.config.js`: ESLint configuration for JavaScript linting
- `prettier.config.json`: Prettier configuration for JavaScript formatting
- `pylint.config`: Pylint configuration for Python linting
- `pyproject.toml`: Black configuration for Python formatting

## Functionality
- Opens web pages using Playwright
- Executes JavaScript on loaded pages to mark content
- Extracts and saves HTML content to specified file paths
- Provides both CLI and Python API interfaces

## Usage Guidelines
1. The runner script handles both local HTML files and remote URLs
2. JavaScript injector focuses on extracting and enhancing HTML elements
3. Always use proper error handling for browser automation
4. Export enhanced HTML to specified file paths

## Development Guidelines
1. Keep JavaScript code clean and focused on HTML enhancement
2. Ensure compatibility with various browser environments
3. Minimize external dependencies
4. Document all functions and methods properly

## Code Quality Guidelines
1. Always run linters before submitting code:
   - For JavaScript: `task lint:js` (uses ESLint)
   - For Python: `task lint:py` (uses Pylint)
   - For all files: `task lint`

2. Keep code properly formatted:
   - For JavaScript: `task format:js` (uses Prettier)
   - For Python: `task format:py` (uses Black)
   - For all files: `task format`
   
3. Install development dependencies:
   - Run `task install-dev` to install all necessary tools
   
4. JavaScript standards:
   - Use single quotes for strings
   - 2 spaces for indentation
   - Maximum line length of 100 characters
   - Add semicolons at the end of statements
   - Use appropriate ESLint disabling comments when necessary

5. Python standards:
   - Follow PEP 8 guidelines with Black formatting
   - Black enforces 4 spaces for indentation (PEP 8 standard)
   - Pylint is configured for 2-space indentation but Black overrides this
   - Maximum line length of 100 characters
   - Use proper type hints
   - Document functions and classes with docstrings