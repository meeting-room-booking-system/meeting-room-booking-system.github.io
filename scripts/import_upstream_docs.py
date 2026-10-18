from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path


DOCUMENTS = {
    "INSTALL": "install",
    "LANGUAGE": "language",
    "UPGRADE": "upgrade",
    "AUTHENTICATION": "authentication",
    "NEWS": "news",
    "ChangeLog": "changelog",
    "LICENSE": "license",
}

README_LINK_TARGETS = {
    "README": "readme",
    "README.MD": "readme",
    **{filename.upper(): slug for filename, slug in DOCUMENTS.items()},
}
README_TOP_LEVEL_LINKS = {
    "news": "../../news/",
    "changelog": "../../changelog/",
}
README_LINK = re.compile(
    r"(?P<prefix>\]\()(?P<target>(?:\./)?(?:README(?:\.md)?|INSTALL|LANGUAGE|UPGRADE|AUTHENTICATION|NEWS|ChangeLog|LICENSE)(?:#[^)\s]*)?)(?P<suffix>\))",
    re.IGNORECASE,
)


def rewrite_readme_links(content: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        target = match.group("target")
        path, separator, fragment = target.partition("#")
        filename = Path(path.removeprefix("./")).name.upper()
        slug = README_LINK_TARGETS.get(filename)
        if slug is None:
            return match.group(0)

        relative_path = (
            "./"
            if slug == "readme"
            else README_TOP_LEVEL_LINKS.get(slug, f"../{slug}/")
        )
        return match.group("prefix") + relative_path + (separator + fragment if separator else "") + match.group("suffix")

    return README_LINK.sub(replace_link, content)


def stage_readme(source: Path, destination: Path) -> bool:
    readme_markdown = source / "README.md"
    readme_plaintext = source / "README"
    if readme_markdown.is_file():
        readme_content = readme_markdown.read_text(encoding="utf-8")
        readme_content = rewrite_readme_links(readme_content)
        readme_page = page_front_matter(
            "README", "readme", layout="markdown"
        ) + readme_content
        is_markdown = True
    elif readme_plaintext.is_file():
        readme_content = readme_plaintext.read_text(encoding="utf-8")
        readme_page = (
            page_front_matter("README", "readme")
            + '<pre class="plain-document">'
            + escape(readme_content)
            + "</pre>\n"
        )
        is_markdown = False
    else:
        raise FileNotFoundError(f"Neither README.md nor README exists in {source}")

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "readme.md").write_text(readme_page, encoding="utf-8")
    return is_markdown


def page_front_matter(
    title: str, slug: str, top_level: bool = False, layout: str = "page"
) -> str:
    permalink = f"/{slug}/" if top_level else f"/documentation/{slug}/"
    return (
        "---\n"
        f"layout: {layout}\n"
        f"title: {title}\n"
        f"permalink: {permalink}\n"
        "render_with_liquid: false\n"
        "---\n\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("site", type=Path)
    args = parser.parse_args()

    if not (args.source / "README.md").is_file() and not (args.source / "README").is_file():
        parser.error(f"Neither README.md nor README exists in {args.source}")

    missing_documents = [
        filename for filename in DOCUMENTS if not (args.source / filename).is_file()
    ]
    if missing_documents:
        parser.error("Required upstream documents are missing: " + ", ".join(missing_documents))

    destination = args.site / "documentation"
    stage_readme(args.source, destination)

    for filename, slug in DOCUMENTS.items():
        source_file = args.source / filename
        content = source_file.read_text(encoding="utf-8")
        top_level = filename in {"NEWS", "ChangeLog"}
        page = (
            page_front_matter(filename, slug, top_level=top_level)
            + '<pre class="plain-document">'
            + escape(content)
            + "</pre>\n"
        )
        (destination / f"{slug}.md").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()