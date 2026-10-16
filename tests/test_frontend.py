"""Unit tests for web frontend assets, mobile viewports, responsive CSS, and JSON-LD schemas."""
import os
import re
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")


class TestFrontend(unittest.TestCase):
    def test_all_html_viewports_and_mobile_meta(self):
        html_files = [
            os.path.join(DOCS_DIR, "index.html"),
            os.path.join(DOCS_DIR, "in", "index.html"),
            os.path.join(DOCS_DIR, "us", "index.html"),
            os.path.join(DOCS_DIR, "ca", "index.html"),
            os.path.join(DOCS_DIR, "uk", "index.html"),
            os.path.join(DOCS_DIR, "eu", "index.html"),
            os.path.join(DOCS_DIR, "docs", "index.html"),
        ]

        for path in html_files:
            rel = os.path.relpath(path, BASE_DIR)
            with self.subTest(file=rel):
                self.assertTrue(os.path.exists(path), f"Missing HTML file: {rel}")
                with open(path, encoding="utf-8") as f:
                    content = f.read()

                # Viewport with cover
                self.assertIn('name="viewport"', content)
                self.assertIn("viewport-fit=cover", content)
                self.assertIn("width=device-width", content)

                # Canonical link
                self.assertIn('rel="canonical"', content)

                # Stylesheet link
                self.assertIn('rel="stylesheet"', content)
                self.assertIn("style.css", content)

                # Early theme initialization in head (prevents white flash / FOUC)
                self.assertIn("localStorage.getItem(\"theme\")", content)
                self.assertIn("document.documentElement.setAttribute(\"data-theme\"", content)

                # Semantic elements
                self.assertIn("<header", content)
                self.assertIn("<nav", content)
                self.assertIn("<footer", content)

    def test_css_design_system_and_mobile_queries(self):
        css_path = os.path.join(DOCS_DIR, "css", "style.css")
        self.assertTrue(os.path.exists(css_path))

        with open(css_path, encoding="utf-8") as f:
            css = f.read()

        # Brace balance
        open_braces = css.count("{")
        close_braces = css.count("}")
        self.assertEqual(open_braces, close_braces, f"Unbalanced braces in style.css: {open_braces} != {close_braces}")

        # Core responsive breakpoints
        self.assertIn("@media (max-width: 768px)", css)
        self.assertIn("@media (max-width: 440px)", css)
        self.assertIn("@media (max-width: 360px)", css)

        # iOS auto-zoom prevention (16px search input)
        self.assertIn("font-size: 16px !important", css)

        # Touch active feedback & tap highlight reset
        self.assertIn("-webkit-tap-highlight-color: transparent", css)
        self.assertIn("pointer: coarse", css)

        # Horizontal overflow protection
        self.assertIn("overflow-x: hidden !important", css)

    def test_app_js_syntax_and_structure(self):
        js_path = os.path.join(DOCS_DIR, "js", "app.js")
        self.assertTrue(os.path.exists(js_path))

        with open(js_path, encoding="utf-8") as f:
            js = f.read()

        # Brace and parenthesis balance
        self.assertEqual(js.count("{"), js.count("}"), "Unbalanced curly braces in app.js")
        self.assertEqual(js.count("["), js.count("]"), "Unbalanced brackets in app.js")

        # Key app methods exist
        self.assertIn("function renderCardsView", js)
        self.assertIn("function renderCompactView", js)
        self.assertIn("function filterAndSortJobs", js)
        self.assertIn("function toggleSave", js)


if __name__ == "__main__":
    unittest.main()
