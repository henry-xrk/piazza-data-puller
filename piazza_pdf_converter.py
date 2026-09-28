#!/usr/bin/env python3
"""
Piazza PDF Converter - Convert live Piazza posts to PDF
This tool uses browser automation to capture Piazza posts with all images and formatting
"""

import json
import os
import time
from typing import List, Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class PiazzaPDFConverter:
    """Convert Piazza posts to PDF using browser automation"""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the PDF converter

        Args:
            email: Piazza account email
            password: Piazza account password
        """
        self.email = email
        self.password = password
        self.browser = None
        self.context = None
        self.page = None
        self.authenticated = False
        self.playwright = None

    def start_browser(self, headless: bool = True):
        """Start the browser instance"""
        print("Starting browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        print("✓ Browser started")

    def stop_browser(self):
        """Stop the browser instance"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, "playwright") and self.playwright:
            self.playwright.stop()
        print("✓ Browser stopped")

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Login to Piazza

        Args:
            email: Piazza account email (optional if set in __init__)
            password: Piazza account password (optional if set in __init__)

        Returns:
            True if login successful, False otherwise
        """
        email = email or self.email
        password = password or self.password

        if not email or not password:
            print("✗ Email and password are required for login")
            return False

        if not self.page:
            print("✗ Browser not started. Call start_browser() first")
            return False

        try:
            print("Logging in to Piazza...")
            self.page.goto("https://piazza.com/", wait_until="networkidle")
            time.sleep(1)

            try:
                sign_in_selectors = [
                    'text="Sign In"',
                    'a:has-text("Sign In")',
                    'button:has-text("Sign In")',
                    '[data-pats="sign-in"]',
                    'a[href*="login"]',
                ]
                clicked = False
                for selector in sign_in_selectors:
                    try:
                        self.page.click(selector, timeout=3000)
                        clicked = True
                        break
                    except Exception:
                        continue
                if clicked:
                    time.sleep(1)
            except Exception as e:
                print(f"  Note: Could not find sign in button: {e}")

            email_selectors = [
                'input[type="email"]:visible',
                'input[name="email"]:visible',
                'input#email_field:visible',
                'input[data-pats="login-email"]:visible',
            ]
            email_found = False
            email_selector = None
            for selector in email_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000, state="visible")
                    email_selector = selector.replace(":visible", "")
                    email_found = True
                    break
                except Exception:
                    continue

            if not email_found:
                try:
                    fallback = 'input[name="email"], input#email_field'
                    self.page.wait_for_selector(fallback, timeout=5000)
                    email_selector = fallback
                except Exception:
                    raise Exception("Could not find email input field")

            self.page.fill(email_selector, email)
            time.sleep(0.5)

            password_selectors = [
                'input[type="password"]:visible',
                'input[name="password"]:visible',
                'input#password_field:visible',
            ]
            password_found = False
            password_selector = None
            for selector in password_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000, state="visible")
                    password_selector = selector.replace(":visible", "")
                    password_found = True
                    break
                except Exception:
                    continue

            if not password_found:
                password_selector = 'input[type="password"], input[name="password"]'

            self.page.fill(password_selector, password)
            time.sleep(0.5)

            login_button_selectors = [
                'button[type="submit"]:visible',
                'button:has-text("Sign In"):visible',
                'button:has-text("Log In"):visible',
                '[data-pats="login-submit"]:visible',
            ]
            button_clicked = False
            for selector in login_button_selectors:
                try:
                    self.page.click(selector, timeout=3000)
                    button_clicked = True
                    break
                except Exception:
                    continue

            if not button_clicked:
                self.page.click(
                    'button[type="submit"], button:has-text("Sign In"), button:has-text("Log In")'
                )

            try:
                self.page.wait_for_url("**/class/**", timeout=10000)
                print("✓ Successfully logged in to Piazza")
                self.authenticated = True
                return True
            except PlaywrightTimeoutError:
                url = self.page.url
                if "piazza.com" in url and "signup" not in url and "login" not in url:
                    print("✓ Successfully logged in to Piazza")
                    self.authenticated = True
                    return True
                print("✗ Login failed - please check your credentials")
                return False
        except Exception as e:
            print(f"✗ Error during login: {e}")
            return False

    def _collapse_feed(self):
        """Hide the class feed so the PDF is the post itself."""
        try:
            button = self.page.query_selector('[title="Collapse feed"]')
            if button:
                button.click()
                time.sleep(1)
        except Exception:
            pass

    def convert_post_to_pdf(
        self,
        class_id: str,
        post_number: int,
        output_dir: str = "pdfs",
        wait_time: float = 2.0,
    ) -> Optional[str]:
        """
        Convert a single Piazza post to PDF

        Args:
            class_id: The Piazza class ID from the class URL
            post_number: The post number
            output_dir: Directory to save PDFs
            wait_time: Time to wait for page to load (seconds)

        Returns:
            Path to the generated PDF file, or None on failure
        """
        if not self.authenticated:
            print("✗ Not authenticated. Please login first")
            return None

        if not self.page:
            print("✗ Browser not started")
            return None

        os.makedirs(output_dir, exist_ok=True)
        url = f"https://piazza.com/class/{class_id}/post/{post_number}"

        try:
            print(f"Converting post {post_number} to PDF...")
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(wait_time)

            try:
                self.page.wait_for_selector(
                    '.post_region, .post-content, [class*="post"]',
                    timeout=10000,
                )
            except Exception:
                print(f"  Warning: Could not find post content selector for post {post_number}")

            self._collapse_feed()

            pdf_filename = f"post_{post_number}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            self.page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"},
            )
            print(f"  ✓ Saved: {pdf_filename}")
            return pdf_path
        except PlaywrightTimeoutError:
            print(f"  ✗ Timeout loading post {post_number} - post may not exist or be inaccessible")
            return None
        except Exception as e:
            print(f"  ✗ Error converting post {post_number}: {e}")
            return None

    def convert_posts_range(
        self,
        class_id: str,
        start: int,
        end: int,
        output_dir: str = "pdfs",
        wait_time: float = 2.0,
        skip_errors: bool = True,
    ) -> List[str]:
        """
        Convert a range of Piazza posts to PDF

        Args:
            class_id: The Piazza class ID from the class URL
            start: Starting post number (inclusive)
            end: Ending post number (inclusive)
            output_dir: Directory to save PDFs
            wait_time: Time to wait for each page to load (seconds)
            skip_errors: Continue after a failed post

        Returns:
            Paths of PDFs that were saved
        """
        if not self.authenticated:
            print("✗ Not authenticated. Please login first")
            return []

        print(f"\n{'=' * 60}")
        print(f"Converting posts {start} to {end} from class {class_id}")
        print(f"{'=' * 60}\n")

        pdf_files = []
        failed_posts = []

        for post_number in range(start, end + 1):
            try:
                pdf_path = self.convert_post_to_pdf(
                    class_id=class_id,
                    post_number=post_number,
                    output_dir=output_dir,
                    wait_time=wait_time,
                )
                if pdf_path:
                    pdf_files.append(pdf_path)
                else:
                    failed_posts.append(post_number)
                    if not skip_errors:
                        print(f"\n✗ Stopping due to error on post {post_number}")
                        break
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\n\n⚠ Interrupted by user")
                break
            except Exception as e:
                print(f"  ✗ Unexpected error on post {post_number}: {e}")
                failed_posts.append(post_number)
                if not skip_errors:
                    break

        print(f"\n{'=' * 60}")
        print("Conversion Complete")
        print(f"{'=' * 60}")
        print(f"✓ Successfully converted: {len(pdf_files)} posts")
        if failed_posts:
            print(f"✗ Failed/Skipped: {len(failed_posts)} posts")
            print(f"  Failed post numbers: {failed_posts}")
        print(f"{'=' * 60}\n")
        return pdf_files

    def save_metadata(self, pdf_files: List[str], output_dir: str = "pdfs"):
        """
        Save metadata about converted PDFs

        Args:
            pdf_files: List of PDF file paths
            output_dir: Directory where metadata will be saved
        """
        metadata = {
            "total_pdfs": len(pdf_files),
            "pdf_files": [os.path.basename(path) for path in pdf_files],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "output_directory": output_dir,
        }
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved to {metadata_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert Piazza posts to PDF")
    parser.add_argument("--email", type=str, help="Piazza account email")
    parser.add_argument("--password", type=str, help="Piazza account password")
    parser.add_argument(
        "--class-id",
        type=str,
        required=True,
        help="Piazza class ID from the class URL",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting post number (default: 1)",
    )
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="Ending post number (inclusive)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="pdfs",
        help="Output directory for PDFs (default: pdfs)",
    )
    parser.add_argument(
        "--wait-time",
        type=float,
        default=2.0,
        help="Wait time for pages to load in seconds (default: 2.0)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Show browser window (for debugging)",
    )
    parser.add_argument("--config", type=str, help="Path to config.json file")
    args = parser.parse_args()

    email = args.email
    password = args.password

    if args.config:
        try:
            with open(args.config, "r") as f:
                config = json.load(f)
            email = email or config.get("email")
            password = password or config.get("password")
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

    if not email or not password:
        print("Error: Email and password are required")
        print("Provide them via --email and --password, or use --config config.json")
        return

    converter = PiazzaPDFConverter(email=email, password=password)
    try:
        converter.start_browser(headless=args.headless)
        if not converter.login():
            print("Login failed. Exiting.")
            return

        pdf_files = converter.convert_posts_range(
            class_id=args.class_id,
            start=args.start,
            end=args.end,
            output_dir=args.output_dir,
            wait_time=args.wait_time,
        )
        if pdf_files:
            converter.save_metadata(pdf_files, args.output_dir)
    finally:
        converter.stop_browser()


if __name__ == "__main__":
    main()
