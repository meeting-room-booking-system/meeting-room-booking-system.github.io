import tempfile
import unittest
from pathlib import Path

from scripts.import_upstream_docs import (
    find_document,
    rewrite_readme_links,
    stage_document,
    stage_readme,
)
from scripts.site import normalize_baseurl


class StageReadmeTests(unittest.TestCase):
    def test_markdown_readme_is_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "site" / "documentation"
            source.mkdir()
            (source / "README.md").write_text("# Markdown source\n", encoding="utf-8")
            (source / "README").write_text("Plaintext source\n", encoding="utf-8")

            is_markdown = stage_readme(source, destination)
            output = (destination / "readme.md").read_text(encoding="utf-8")

            self.assertTrue(is_markdown)
            self.assertIn("layout: markdown", output)
            self.assertIn("# Markdown source", output)
            self.assertNotIn("Plaintext source", output)

    def test_markdown_links_use_generated_document_routes(self) -> None:
        markdown = (
            "[Install](INSTALL#requirements), [history](ChangeLog), "
            "[readme](README.md), and [external](https://example.com)"
        )

        rewritten = rewrite_readme_links(markdown)

        self.assertIn("[Install](../install/#requirements)", rewritten)
        self.assertIn("[history](../../changelog/)", rewritten)
        self.assertIn("[news](../../news/)", rewrite_readme_links("[news](NEWS)"))
        self.assertIn("[readme](./)", rewritten)
        self.assertIn("[external](https://example.com)", rewritten)

    def test_plaintext_readme_is_escaped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "site" / "documentation"
            source.mkdir()
            (source / "README").write_text("<tag> & text\n", encoding="utf-8")

            is_markdown = stage_readme(source, destination)
            output = (destination / "readme.md").read_text(encoding="utf-8")

            self.assertFalse(is_markdown)
            self.assertIn("<pre class=\"plain-document\">", output)
            self.assertIn("&lt;tag&gt; &amp; text", output)

    def test_missing_readme_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()

            with self.assertRaises(FileNotFoundError):
                stage_readme(source, root / "site" / "documentation")


class StageDocumentTests(unittest.TestCase):
    def test_markdown_preferred_for_any_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "site" / "documentation"
            source.mkdir()
            (source / "INSTALL.md").write_text("# Md install\n[up](UPGRADE.md)\n", encoding="utf-8")
            (source / "INSTALL").write_text("Plain install\n", encoding="utf-8")

            is_markdown = stage_document(source, destination, "INSTALL", "install")
            output = (destination / "install.md").read_text(encoding="utf-8")

            self.assertTrue(is_markdown)
            self.assertIn("layout: markdown", output)
            self.assertIn("# Md install", output)
            self.assertIn("[up](../upgrade/)", output)
            self.assertNotIn("Plain install", output)

    def test_plaintext_fallback_and_top_level_permalink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            destination = root / "site" / "documentation"
            source.mkdir()
            (source / "NEWS").write_text("<a> & b\n", encoding="utf-8")

            is_markdown = stage_document(source, destination, "NEWS", "news", top_level=True)
            output = (destination / "news.md").read_text(encoding="utf-8")

            self.assertFalse(is_markdown)
            self.assertIn("permalink: /news/", output)
            self.assertIn("&lt;a&gt; &amp; b", output)

    def test_find_document_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.assertIsNone(find_document(Path(temporary_directory), "LICENSE"))


class BaseUrlTests(unittest.TestCase):
    def test_root_slash_normalizes_to_empty(self) -> None:
        self.assertEqual(normalize_baseurl("/"), "")

    def test_subdirectory_prefix_is_normalized(self) -> None:
        self.assertEqual(normalize_baseurl("/~jberanek/mrbs-website/"), "/~jberanek/mrbs-website")

    def test_non_path_baseurl_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_baseurl("https://example.com")


if __name__ == "__main__":
    unittest.main()