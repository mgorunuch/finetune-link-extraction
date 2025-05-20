#!/usr/bin/env python3
"""
HTML Extractor and Enhancer Runner

This script loads HTML content from files or URLs, injects JavaScript to enhance
the content, and exports the enhanced HTML to specified file paths.
"""

import argparse
import json
import os
import sys
from urllib.parse import urlparse
import logging
from typing import Dict, Any, Optional, Union, Tuple

# Browser automation libraries
try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Fallback to requests if Playwright is not available
import requests
from bs4 import BeautifulSoup


class HTMLExtractor:
    """
    HTML Extractor and Enhancer

    Loads HTML content, injects JavaScript for enhancement, and exports the result.
    """

    def __init__(self, use_playwright: bool = True, headless: bool = True):
        """
        Initialize the HTML extractor.

        Args:
            use_playwright: Whether to use Playwright for browser automation
            headless: Whether to run the browser in headless mode
        """
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.headless = headless

        # Get the path to the injector.js file
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.injector_path = os.path.join(self.script_dir, "injector.js")

        # Check if injector script exists
        if not os.path.exists(self.injector_path):
            raise FileNotFoundError(f"JavaScript injector not found at {self.injector_path}")

        # Read the injector script
        with open(self.injector_path, "r", encoding="utf-8") as f:
            self.injector_script = f.read()

        # Set up logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("HTMLExtractor")

    def is_url(self, source: str) -> bool:
        """
        Check if the source is a URL.

        Args:
            source: The source to check

        Returns:
            bool: True if the source is a URL, False otherwise
        """
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def read_html_file(self, file_path: str) -> str:
        """
        Read HTML content from a file.

        Args:
            file_path: Path to the HTML file

        Returns:
            str: The HTML content

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        self.logger.info(f"Reading HTML from file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def fetch_url(self, url: str) -> str:
        """
        Fetch HTML content from a URL using requests.

        Args:
            url: The URL to fetch

        Returns:
            str: The HTML content

        Raises:
            requests.RequestException: If the request fails
        """
        self.logger.info(f"Fetching HTML from URL: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def process_with_playwright(self, source: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process HTML using Playwright.

        Args:
            source: The HTML source or URL

        Returns:
            Tuple[str, Dict[str, Any]]: Enhanced HTML and extraction data

        Raises:
            Exception: If Playwright processing fails
        """
        self.logger.info("Processing with Playwright")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                # Load the content
                if self.is_url(source):
                    page.goto(source, wait_until="networkidle")
                else:
                    page.set_content(source)

                # Inject and execute the script
                result = page.evaluate(self.injector_script)

                if not result:
                    self.logger.warning("JavaScript injection did not complete successfully")

                # Extract the data from the hidden element
                extraction_data_json = page.evaluate(
                    """() => {
                    const dataEl = document.getElementById('html-extractor-data');
                    return dataEl ? dataEl.textContent : '{}';
                }"""
                )

                try:
                    extraction_data = json.loads(extraction_data_json)
                except json.JSONDecodeError:
                    self.logger.warning("Could not parse extraction data JSON")
                    extraction_data = {}

                # Get the enhanced HTML
                enhanced_html = page.content()

                return enhanced_html, extraction_data

            finally:
                browser.close()

    def process_with_basic(self, html: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process HTML using basic techniques (without browser automation).

        Args:
            html: The HTML content

        Returns:
            Tuple[str, Dict[str, Any]]: Modified HTML and basic extraction data
        """
        self.logger.info("Processing with basic HTML parser")
        soup = BeautifulSoup(html, "html.parser")

        # Basic extraction data
        extraction_data = {
            "metadata": {"title": soup.title.text if soup.title else ""},
            "statistics": {
                "headings": len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])),
                "links": len(soup.find_all("a")),
                "images": len(soup.find_all("img")),
                "tables": len(soup.find_all("table")),
                "paragraphs": len(soup.find_all("p")),
            },
            "enhancementApplied": False,
        }

        # Insert the extraction data into the HTML
        script_tag = soup.new_tag("script")
        script_tag["id"] = "html-extractor-data"
        script_tag["type"] = "application/json"
        script_tag.string = json.dumps(extraction_data)

        if soup.body:
            soup.body.append(script_tag)
        else:
            soup.html.append(soup.new_tag("body"))
            soup.body.append(script_tag)

        return str(soup), extraction_data

    def process_html(self, source: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process HTML from a source (file or URL).

        Args:
            source: HTML content, file path, or URL

        Returns:
            Tuple[str, Dict[str, Any]]: Enhanced HTML and extraction data
        """
        # Check if source is a file path or URL
        if os.path.isfile(source):
            html = self.read_html_file(source)
        elif self.is_url(source):
            if self.use_playwright:
                # Let Playwright handle the URL directly
                return self.process_with_playwright(source)
            html = self.fetch_url(source)
        else:
            # Assume source is HTML content
            html = source

        # Process the HTML
        if self.use_playwright:
            return self.process_with_playwright(html)
        return self.process_with_basic(html)

    def save_html(self, html: str, output_path: str) -> None:
        """
        Save HTML content to a file.

        Args:
            html: The HTML content
            output_path: Where to save the HTML

        Raises:
            IOError: If writing to the file fails
        """
        self.logger.info(f"Saving HTML to: {output_path}")
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def save_extraction_data(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Save extraction data to a JSON file.

        Args:
            data: The extraction data
            output_path: Where to save the data

        Raises:
            IOError: If writing to the file fails
        """
        self.logger.info(f"Saving extraction data to: {output_path}")
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def extract_and_enhance(
        self, source: str, output_html: str, output_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract and enhance HTML from source and save to output files.

        Args:
            source: HTML content, file path, or URL
            output_html: Where to save the enhanced HTML
            output_data: Where to save the extraction data (optional)

        Returns:
            Dict[str, Any]: The extraction data

        Raises:
            Exception: If extraction or saving fails
        """
        try:
            # Process the HTML
            enhanced_html, extraction_data = self.process_html(source)

            # Save the enhanced HTML
            self.save_html(enhanced_html, output_html)

            # Save the extraction data if requested
            if output_data:
                self.save_extraction_data(extraction_data, output_data)

            return extraction_data

        except Exception as e:
            self.logger.error(f"Error processing HTML: {str(e)}")
            raise


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="HTML Extractor and Enhancer")
    parser.add_argument("source", help="HTML content, file path, or URL")
    parser.add_argument("output", help="Output file path for the enhanced HTML")
    parser.add_argument("--data", help="Output file path for extraction data (JSON)")
    parser.add_argument(
        "--no-playwright", action="store_true", help="Disable Playwright browser automation"
    )
    parser.add_argument(
        "--no-headless", action="store_true", help="Disable headless mode (shows browser UI)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.getLogger("HTMLExtractor").setLevel(logging.DEBUG)

    try:
        # Initialize the extractor
        extractor = HTMLExtractor(
            use_playwright=not args.no_playwright, headless=not args.no_headless
        )

        # Process the HTML
        result = extractor.extract_and_enhance(args.source, args.output, args.data)

        # Print summary
        print(f"HTML processing complete!")
        print(f"Enhanced HTML saved to: {args.output}")

        if args.data:
            print(f"Extraction data saved to: {args.data}")

        print("\nExtraction Summary:")
        for key, value in result.get("statistics", {}).items():
            print(f"  - {key.capitalize()}: {value}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
