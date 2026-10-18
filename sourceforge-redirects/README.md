# SourceForge transition redirects

This directory contains PHP 301 redirect handlers for the legacy
`mrbs.sourceforge.io` website. Upload the contents of this directory into the
SourceForge project web document root, preserving the `mrbs/`, `mrbs-tip/`,
`periodmrbs/`, and `periodsmrbs/` subdirectories. Back up the existing web
files before replacing them.

The public pages redirect to `https://meeting-room-booking-system.github.io/`.
The demo shortcuts continue to redirect to the demo site.
`view_text.php` and `view_image.php` only redirect recognized document names
and screenshot files; unknown values go to the corresponding index page.

The current live site serves PHP, but SourceForge's Project Web Services
documentation says PHP, `.htaccess`, and CGI support ended on May 20, 2025.
These handlers therefore depend on PHP execution continuing to work for this
project. Check the live response after deployment. If PHP is disabled, these
files cannot provide redirects from SourceForge.