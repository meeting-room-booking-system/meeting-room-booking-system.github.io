# MRBS Website

This repository contains the public information website for the Meeting Room
Booking System (MRBS). The application itself is maintained in
[`mrbs-code`](https://github.com/meeting-room-booking-system/mrbs-code).

The site is a static Jekyll website published at
`https://meeting-room-booking-system.github.io/`. Its homepage preserves the
content of the former Introduction page. The old PHP website has been removed.
Screenshot source files are stored in `site/screenshots/`.

## Requirements

- Python 3.10 or newer (the local helper and documentation importer use only the
  Python standard library)
- Ruby and RubyGems
- Jekyll, installed as a Ruby gem
- Git and a local `mrbs-code` checkout
- `rsync` only when using the local `deploy` command

Node.js, npm, pnpm, and Bun are not needed. The site has no JavaScript build
step or npm dependencies; adding a package manager would add setup work without
helping this Jekyll workflow.

### Installing Jekyll

Install the Ruby development headers before installing Jekyll. Some Jekyll
dependencies build native extensions; if installation fails with a missing
`ruby.h`, install the development package for your distribution and retry. For
example, Debian/Ubuntu use `ruby-dev`; Fedora/openSUSE use `ruby-devel`.

Install Jekyll in your user gem directory:

```sh
gem install --user-install jekyll
```

RubyGems may warn that its user `bin` directory is not on `PATH`. Some
installations also suffix executable names with the Ruby version, for example
`jekyll.ruby3.4`, rather than creating a plain `jekyll` command. The local
helper handles both cases: it checks `PATH`, then searches the directory
reported by `gem env user_gemhome` for an executable named `jekyll*`. If needed,
pass its path explicitly with `--jekyll`.

## Local Testing

The helper imports documentation from a local `mrbs-code` checkout before
building. By default it looks for `../mrbs-code` relative to this repository;
use `--code-repo` to select another checkout. Each command also accepts
`--baseurl`. Omit it to use `site/_config.yml`; use `/` for the domain root or
provide the URL prefix when serving below a directory.

Build the site into `_site/`:

```sh
python3 scripts/site.py build
```

Build to a temporary directory, selecting a source checkout and an explicit
base URL:

```sh
python3 scripts/site.py build \
  --code-repo ../mrbs-code \
  --destination /tmp/mrbs-web-site \
  --baseurl /
```

Run Jekyll's local server on `127.0.0.1:4000`:

```sh
python3 scripts/site.py serve --code-repo ../mrbs-code
```

The server binds to localhost by default. Use `--host 0.0.0.0` only when you
intentionally want other machines on your network to access the preview.

## Deploy to a Local Webroot

The `deploy` command builds to a temporary directory, then copies the result
with `rsync`. The destination must already exist. It does not delete files by
default, so obsolete files may remain after a build. For a dedicated site
directory, `--delete` makes the destination match the generated site exactly;
review the path carefully because this removes files from the destination that
are not in the build.

For the home-server directory used during development:

```sh
python3 scripts/site.py deploy \
  --code-repo ../mrbs-code \
  --webroot ~/public_html/mrbs-website \
  --baseurl /~johnsmith/mrbs-website
```

Add `--delete` only if that webroot contains nothing that must be preserved.

## GitHub Pages Releases

Run [`.github/workflows/pages.yml`](.github/workflows/pages.yml) manually from
the Actions tab. Supply exactly one of:

- `mrbs_code_tag`: a tag name such as `v1.12.2`
- `mrbs_code_branch`: a branch name such as `main`

Enter the bare name, not a `refs/tags/` or `refs/heads/` prefix. The workflow
checks out that exact ref, imports its README and documentation, builds the
site, and deploys it. Pushes to either repository do not deploy automatically.

The importer prefers upstream `README.md` and falls back to the plaintext
`README`. It also imports `INSTALL`, `LANGUAGE`, `UPGRADE`, `AUTHENTICATION`,
`NEWS`, `ChangeLog`, and `LICENSE`. These generated documentation pages are
not maintained in this repository. To contribute to the website, edit the
source pages under `site/`; do not edit generated pages in
`site/documentation/`.
