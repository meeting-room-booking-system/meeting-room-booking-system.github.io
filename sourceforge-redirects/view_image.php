<?php

require_once __DIR__ . '/_redirect.php';

$screenshots = array(
  'mrbs_main.png',
  'mrbs_entry_edit.png',
  'mrbs_entry_view.png',
  'mrbs_search.png',
  'mrbs_admin.png'
);

$file = isset($_GET['file']) && is_string($_GET['file'])
  ? basename($_GET['file'])
  : '';

if (in_array($file, $screenshots, true))
{
  mrbs_redirect_to_site('/screenshots/' . rawurlencode($file));
}

mrbs_redirect_to_site('/screenshots/');