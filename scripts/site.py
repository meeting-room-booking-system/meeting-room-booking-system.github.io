#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
IMPORTER = ROOT / "scripts" / "import_upstream_docs.py"
DEFAULT_CODE_REPO = ROOT.parent / "mrbs-code"


def normalize_baseurl(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value == "/":
        return ""
    if value and (not value.startswith("/") or "?" in value or "#" in value):
        raise ValueError("base URL must be a path beginning with /, or empty for root")
    return value.rstrip("/")


def import_documents(code_repo: Path) -> None:
    source = code_repo.expanduser().resolve()
    if not source.is_dir():
        raise RuntimeError(f"mrbs-code checkout not found: {source}")
    subprocess.run(
        [sys.executable, str(IMPORTER), str(source), str(SITE)],
        cwd=ROOT,
        check=True,
    )


def jekyll_command(
    operation: str,
    destination: Path,
    baseurl: str | None,
    host: str | None = None,
    port: int | None = None,
) -> list[str]:
    command = [
        "bundle",
        "exec",
        "jekyll",
        operation,
        "--source",
        str(SITE),
        "--destination",
        str(destination),
    ]
    if baseurl is not None:
        command.extend(["--baseurl", baseurl])
    if host is not None:
        command.extend(["--host", host])
    if port is not None:
        command.extend(["--port", str(port)])
    return command


def run_jekyll(command: list[str]) -> None:
    if not shutil.which("bundle"):
        raise RuntimeError(
            "Bundler was not found; install Ruby and Bundler, then run "
            "`bundle config set --local path vendor/bundle && bundle install`"
        )
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def add_site_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--code-repo",
        type=Path,
        default=DEFAULT_CODE_REPO,
        help=f"local mrbs-code checkout (default: {DEFAULT_CODE_REPO})",
    )
    parser.add_argument(
        "--baseurl",
        help="URL path prefix, e.g. /~user/site; omit for the configured default or use / for root",
    )
    parser.add_argument(
        "--destination", type=Path, default=ROOT / "_site", help="build output directory"
    )


def prepare(args: argparse.Namespace) -> tuple[Path, str | None]:
    destination = args.destination.expanduser().resolve()
    if destination == Path("/") or destination == Path.home() or destination in ROOT.parents:
        raise RuntimeError(f"Refusing to use {destination} as the output directory")
    import_documents(args.code_repo)
    return destination, normalize_baseurl(args.baseurl)


def build(args: argparse.Namespace) -> None:
    destination, baseurl = prepare(args)
    if args.clean:
        run_jekyll(jekyll_command("clean", destination, None))
    run_jekyll(jekyll_command("build", destination, baseurl))


def serve(args: argparse.Namespace) -> None:
    destination, baseurl = prepare(args)
    run_jekyll(
        jekyll_command("serve", destination, baseurl, host=args.host, port=args.port)
    )


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or serve the MRBS Jekyll website locally."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="build static files")
    add_site_options(build_parser)
    build_parser.add_argument(
        "--clean",
        action="store_true",
        help="first delete the destination directory and Jekyll's cache; "
        "use only for a directory dedicated to this site",
    )
    build_parser.set_defaults(func=build)

    serve_parser = subparsers.add_parser("serve", help="run Jekyll's local web server")
    add_site_options(serve_parser)
    serve_parser.add_argument("--host", default="127.0.0.1", help="bind address")
    serve_parser.add_argument("--port", type=int, default=4000, help="listen port")
    serve_parser.set_defaults(func=serve)

    return parser


def main() -> int:
    parser = make_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
