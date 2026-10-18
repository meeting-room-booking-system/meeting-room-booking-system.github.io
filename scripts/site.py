#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
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


def find_jekyll(explicit: str | None) -> str:
    if explicit:
        executable = shutil.which(explicit)
        if executable:
            return executable
        candidate = Path(explicit).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
        raise RuntimeError(f"Jekyll executable not found: {explicit}")

    executable = shutil.which("jekyll")
    if executable:
        return executable

    gem = shutil.which("gem")
    if gem:
        result = subprocess.run(
            [gem, "env", "user_gemhome"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            gem_bin = Path(result.stdout.strip()) / "bin"
            candidates = sorted(gem_bin.glob("jekyll*"))
            for candidate in candidates:
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    return str(candidate)

    raise RuntimeError(
        "Jekyll was not found on PATH or in RubyGems' user bin directory. "
        "Install it with `gem install --user-install jekyll`, ensure Ruby "
        "development headers are installed, or pass --jekyll /path/to/executable."
    )


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
    jekyll: str,
    operation: str,
    destination: Path,
    baseurl: str | None,
    host: str | None = None,
    port: int | None = None,
) -> list[str]:
    command = [
        jekyll,
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
        "--jekyll",
        help="Jekyll executable path or name; normally auto-detected",
    )


def build(args: argparse.Namespace) -> None:
    import_documents(args.code_repo)
    jekyll = find_jekyll(args.jekyll)
    baseurl = normalize_baseurl(args.baseurl)
    destination = args.destination.expanduser().resolve()
    command = jekyll_command(jekyll, "build", destination, baseurl)
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def serve(args: argparse.Namespace) -> None:
    import_documents(args.code_repo)
    jekyll = find_jekyll(args.jekyll)
    baseurl = normalize_baseurl(args.baseurl)
    destination = args.destination.expanduser().resolve()
    command = jekyll_command(
        jekyll, "serve", destination, baseurl, host=args.host, port=args.port
    )
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def deploy(args: argparse.Namespace) -> None:
    import_documents(args.code_repo)
    jekyll = find_jekyll(args.jekyll)
    baseurl = normalize_baseurl(args.baseurl)
    webroot = args.webroot.expanduser().resolve()
    if not webroot.is_dir():
        raise RuntimeError(f"Deployment webroot must already exist: {webroot}")
    if webroot == Path("/") or webroot == ROOT or ROOT in webroot.parents:
        raise RuntimeError(f"Refusing to deploy into the repository: {webroot}")

    rsync = shutil.which("rsync")
    if not rsync:
        raise RuntimeError("rsync was not found; install rsync to use deploy")

    with tempfile.TemporaryDirectory(prefix="mrbs-site-") as temporary_directory:
        destination = Path(temporary_directory) / "site"
        command = jekyll_command(jekyll, "build", destination, baseurl)
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, cwd=ROOT, check=True)

        sync = [rsync, "--archive", "--human-readable", "--itemize-changes"]
        if args.delete:
            sync.append("--delete")
        sync.extend([str(destination) + os.sep, str(webroot) + os.sep])
        print(f"Running: {' '.join(sync)}")
        subprocess.run(sync, check=True)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build, serve, or deploy the MRBS Jekyll website locally."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="build static files")
    add_site_options(build_parser)
    build_parser.add_argument(
        "--destination", type=Path, default=ROOT / "_site", help="build output directory"
    )
    build_parser.set_defaults(func=build)

    serve_parser = subparsers.add_parser("serve", help="run Jekyll's local web server")
    add_site_options(serve_parser)
    serve_parser.add_argument(
        "--destination", type=Path, default=ROOT / "_site", help="build output directory"
    )
    serve_parser.add_argument("--host", default="127.0.0.1", help="bind address")
    serve_parser.add_argument("--port", type=int, default=4000, help="listen port")
    serve_parser.set_defaults(func=serve)

    deploy_parser = subparsers.add_parser(
        "deploy", help="build and rsync the site to a local webroot"
    )
    add_site_options(deploy_parser)
    deploy_parser.add_argument(
        "--webroot", type=Path, required=True, help="existing destination webroot"
    )
    deploy_parser.add_argument(
        "--delete",
        action="store_true",
        help="remove destination files absent from the build; use only for a dedicated site directory",
    )
    deploy_parser.set_defaults(func=deploy)

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