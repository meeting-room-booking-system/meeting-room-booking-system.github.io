# MRBS Website

This repository contains the public information website for the Meeting Room
Booking System (MRBS). The application itself is maintained in
[`mrbs-code`](https://github.com/meeting-room-booking-system/mrbs-code).

The site is a static Jekyll website published at
`https://meeting-room-booking-system.github.io/`. Its homepage preserves the
content of the former Introduction page. The old PHP website has been removed.
Screenshot source files are stored in `site/screenshots/`.
[`sourceforge-redirects/`](sourceforge-redirects/README.md) holds the redirect
handlers for the legacy SourceForge site and is not part of the Jekyll build.

## Requirements

- Python 3.10 or newer (the helper script and documentation importer use only
  the standard library)
- Ruby and Bundler
- Git and a local `mrbs-code` checkout

Node.js and npm are not needed; the site has no JavaScript build step.

### Installing Jekyll

The [`Gemfile`](Gemfile) uses the `github-pages` gem so local builds use the
same Jekyll and plugin versions as GitHub Pages. Install the gems into the
repository (no root access or `PATH` changes needed):

```sh
bundle config set --local path vendor/bundle
bundle install
```

Some gems build native extensions. If installation fails with a missing
`ruby.h`, install the Ruby development package for your distribution (for
example `ruby-dev` on Debian/Ubuntu, `ruby-devel` on Fedora/openSUSE) and retry.

## Local Testing

The helper imports documentation from a local `mrbs-code` checkout before
building. By default it looks for `../mrbs-code` relative to this repository;
use `--code-repo` to select another checkout. Both commands also accept
`--destination` (default `_site/`) and `--baseurl`. Omit `--baseurl` to use
`site/_config.yml`; use `/` for the domain root or provide the URL prefix when
serving below a directory.

Run Jekyll's local server on `127.0.0.1:4000`:

```sh
python3 scripts/site.py serve
```

In VS Code Remote sessions the forwarded port makes this reachable from your
local browser. The server binds to localhost by default; use `--host 0.0.0.0`
only when you intentionally want other machines on your network to access the
preview.

Build the static files into `_site/`:

```sh
python3 scripts/site.py build
```

Jekyll deletes stale generated files from the destination on every build, so
do not point `--destination` at a directory containing other content. Add
`--clean` to also delete the destination and Jekyll's cache before building:

```sh
python3 scripts/site.py build --clean \
  --code-repo ../mrbs-code \
  --destination ~/public_html/mrbs-website \
  --baseurl /~johnsmith/mrbs-website
```

Run the tests with:

```sh
python3 -m unittest discover -s tests
```

## Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the tests and a
Jekyll build for pull requests and for pushes to branches other than `main`.

## GitHub Pages Releases

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the site.
It runs automatically on pushes to `main` that change `site/`, `scripts/`, or
the workflow itself, and can be run manually from the Actions tab. Manual runs
accept at most one of:

- `mrbs_code_tag`: a tag name such as `v1.12.2`
- `mrbs_code_branch`: a branch name such as `main`

Enter the bare name, not a `refs/tags/` or `refs/heads/` prefix. If both are
empty (including on automatic runs), the latest `v*` release tag of `mrbs-code`
is used. The workflow checks out that ref, imports its README and
documentation, builds the site, and deploys it. Pushes to `mrbs-code` do not
deploy automatically, so run the workflow manually after a release.

The importer prefers upstream `README.md` and falls back to the plaintext
`README`. It also imports `INSTALL`, `LANGUAGE`, `UPGRADE`, `AUTHENTICATION`,
`NEWS`, `ChangeLog`, and `LICENSE`. These generated documentation pages are
not maintained in this repository. To contribute to the website, edit the
source pages under `site/`; do not edit generated pages in
`site/documentation/`.

Fonts (DM Sans and Space Grotesk, SIL Open Font License) are self-hosted in
`site/assets/fonts/`, so pages make no requests to third-party servers, with
one exception: Google Analytics.

## Analytics and Cookie Consent

Google Analytics (GA4) is loaded by
[`site/assets/consent.js`](site/assets/consent.js) only after a visitor
accepts the cookie banner; until then no request is made to Google and no
cookies are set. The choice is kept in `localStorage` and can be changed from
the "Cookie settings" link in the footer. The measurement ID is set in the
`data-ga-id` attribute in
[`site/_layouts/default.html`](site/_layouts/default.html), and the
[privacy page](site/privacy/index.md) describes what is collected.
