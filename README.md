# MRBS Web Site

This repository contains the public information website for the Meeting Room
Booking System (MRBS). The application itself is maintained in
[`mrbs-code`](https://github.com/meeting-room-booking-system/mrbs-code).

The site is published with GitHub Pages. Its static homepage preserves the
content of the former Introduction page. The old PHP website has been removed.
Screenshot source files are stored in `site/screenshots/` alongside the rest of
the Jekyll site.

The documentation pages are imported from a specified tag of the public
`mrbs-code` repository by [`.github/workflows/pages.yml`](.github/workflows/pages.yml).
The manual deployment requires a tag name such as `v1.12.2` (without
`refs/tags/`) and checks out that exact tag. The build prefers the upstream
`README.md` and falls back to its plaintext
`README`, then imports `INSTALL`, `LANGUAGE`, `UPGRADE`, `AUTHENTICATION`,
`NEWS`, `ChangeLog`, and `LICENSE`. Imported text documents are not maintained
in this repository.

Run the workflow manually from the Actions tab when you want to publish. Choose
the `mrbs-code` tag whose documentation should appear on the site; pushes to
either repository do not deploy automatically.

The Jekyll site source is in [`site/`](site/). To preview it locally, install
Jekyll and build after importing documentation from a local `mrbs-code`
checkout:

```sh
python3 scripts/import_upstream_docs.py ../mrbs-code site
jekyll build --source site --destination /tmp/mrbs-web-site
```

To contribute, update the relevant page in `site/`, run the build, and check
the generated links and images. Do not edit generated documentation pages in
`site/documentation/`; the workflow recreates them from `mrbs-code`.