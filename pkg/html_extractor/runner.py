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
from playwright.sync_api import sync_playwright

# For URL fetching when needed
import requests


class HTMLExtractor:
    """
    HTML Extractor and Enhancer

    Loads HTML content, injects JavaScript for enhancement, and exports the result.
    """

    def __init__(self, headless: bool = True, profile_name: str = "default"):
      """
      Initialize the HTML extractor.

      Args:
        headless: Whether to run the browser in headless mode
        profile_name: The name of the Playwright profile to use
      """
      self.headless = headless

      # Get the path to the script directory
      self.script_dir = os.path.dirname(os.path.abspath(__file__))

      # Set up profile path
      self.profile_name = profile_name
      self.profile_path = os.path.join(self.script_dir, "profile", profile_name)

      # Get the path to the injector.js file
      self.injector_path = os.path.join(self.script_dir, "injector.js")

      # Check if injector script exists
      if not os.path.exists(self.injector_path):
        raise FileNotFoundError(f"JavaScript injector not found at {self.injector_path}")

      # Check if profile directory exists
      if not os.path.exists(self.profile_path):
        self.logger.warning(f"Profile directory not found at {self.profile_path}, will use default browser settings")

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

    def process_with_playwright(self, source: str) -> str:
      """
      Process HTML using Playwright with profile support.

      Args:
        source: The HTML source or URL

      Returns:
        str: Enhanced HTML

      Raises:
        Exception: If Playwright processing fails
      """
      self.logger.info("Processing with Playwright")
      self.logger.info(f"Using profile: {self.profile_name}")

      with sync_playwright() as p:
        # Check if profile directory exists and is usable
        use_profile = os.path.exists(self.profile_path)

        if use_profile:
          # Launch browser with persistent context using profile
          self.logger.info(f"Loading browser with profile from {self.profile_path}")
          browser_context = p.chromium.launch_persistent_context(
            user_data_dir=self.profile_path,
            headless=self.headless,
            devtools=True,
          )
          page = browser_context.new_page()
        else:
          # Fall back to standard browser if profile doesn't exist
          self.logger.warning("Profile not found, using default browser settings")
          browser = p.chromium.launch(
            headless=self.headless,
            devtools=True,
          )
          page = browser.new_page()

        try:
          # Load the content
          if self.is_url(source):
            self.logger.info(f"Navigating to URL: {source}")
            page.goto(source, wait_until="networkidle")
          else:
            self.logger.info("Setting page content from HTML source")
            page.set_content(source)

          client = page.context.new_cdp_session(page)
          result = client.send("Runtime.evaluate", {
            "includeCommandLineAPI": True, # Required for using getEventListeners function
            "expression": self.injector_script,
            "returnByValue": True,
          })
          self.logger.debug(result)
          if not result:
            self.logger.warning("JavaScript injection did not complete successfully")

          # Get the enhanced HTML
          enhanced_html = page.content()

          return enhanced_html

        finally:
          if use_profile:
            browser_context.close()
          else:
            browser.close()

    def process_html(self, source: str) -> str:
      """
      Process HTML from a source (file or URL).

      Args:
        source: HTML content, file path, or URL

      Returns:
        str: Enhanced HTML
      """
      # Check if source is a file path or URL
      if os.path.isfile(source):
        html = self.read_html_file(source)
      elif self.is_url(source):
        # Let Playwright handle the URL directly
        return self.process_with_playwright(source)
      else:
        # Assume source is HTML content
        html = source

      # Process the HTML
      return self.process_with_playwright(html)

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

    def extract_and_enhance(
        self, source: str, output_html: str
    ) -> None:
      """
      Extract and enhance HTML from source and save to output files.

      Args:
        source: HTML content, file path, or URL
        output_html: Where to save the enhanced HTML

      Raises:
        Exception: If extraction or saving fails
      """
      try:
        # Process the HTML
        enhanced_html = self.process_html(source)

        # Save the enhanced HTML
        self.save_html(enhanced_html, output_html)

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
  parser.add_argument(
    "--no-headless", action="store_true", help="Disable headless mode (shows browser UI)"
  )
  parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
  parser.add_argument(
    "--profile", default="default", help="Playwright profile to use (default: 'default')"
  )

  args = parser.parse_args()

  # Set up logging level
  if args.verbose:
    logging.getLogger("HTMLExtractor").setLevel(logging.DEBUG)

  try:
    # Initialize the extractor
    extractor = HTMLExtractor(
      headless=not args.no_headless,
      profile_name=args.profile
    )

    # Process the HTML
    extractor.extract_and_enhance(args.source, args.output)

    # Print summary
    print(f"HTML processing complete!")
    print(f"Enhanced HTML saved to: {args.output}")
    print(f"Used profile: {args.profile}")

  except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
