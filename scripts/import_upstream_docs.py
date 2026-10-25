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
    **{filename.upper(): slug for filename, slug in DOCUMENTS.items()},
}
README_TOP_LEVEL_LINKS = {
    "news": "../../news/",
    "changelog": "../../changelog/",
}
README_LINK = re.compile(
    r"(?P<prefix>\]\()(?P<target>(?:\./)?(?:README|INSTALL|LANGUAGE|UPGRADE|AUTHENTICATION|NEWS|ChangeLog|LICENSE)(?:\.md)?(?:#[^)\s]*)?)(?P<suffix>\))",
    re.IGNORECASE,
)


def rewrite_readme_links(content: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        target = match.group("target")
        path, separator, fragment = target.partition("#")
        filename = Path(path.removeprefix("./")).name.upper().removesuffix(".MD")
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


def find_document(source: Path, name: str) -> Path | None:
    """Return the Markdown version of a document if present, else the plain text one."""
    for candidate in (source / f"{name}.md", source / name):
        if candidate.is_file():
            return candidate
    return None


def stage_document(
    source: Path, destination: Path, name: str, slug: str, top_level: bool = False
) -> bool:
    document = find_document(source, name)
    if document is None:
        raise FileNotFoundError(f"Neither {name}.md nor {name} exists in {source}")

    content = document.read_text(encoding="utf-8")
    is_markdown = document.suffix.lower() == ".md"
    if is_markdown:
        page = (
            page_front_matter(name, slug, top_level=top_level, layout="markdown")
            + rewrite_readme_links(content)
        )
    else:
        page = (
            page_front_matter(name, slug, top_level=top_level)
            + '<pre class="plain-document">'
            + escape(content)
            + "</pre>\n"
        )

    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"{slug}.md").write_text(page, encoding="utf-8")
    return is_markdown


def stage_readme(source: Path, destination: Path) -> bool:
    return stage_document(source, destination, "README", "readme")


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

    missing_documents = [
        name
        for name in ["README", *DOCUMENTS]
        if find_document(args.source, name) is None
    ]
    if missing_documents:
        parser.error("Required upstream documents are missing: " + ", ".join(missing_documents))

    destination = args.site / "documentation"
    stage_readme(args.source, destination)

    for filename, slug in DOCUMENTS.items():
        stage_document(
            args.source,
            destination,
            filename,
            slug,
            top_level=filename in {"NEWS", "ChangeLog"},
        )


if __name__ == "__main__":
    main()