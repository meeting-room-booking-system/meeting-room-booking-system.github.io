import tempfile
import unittest
from pathlib import Path

from scripts.import_upstream_docs import rewrite_readme_links, stage_readme


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


if __name__ == "__main__":
    unittest.main()