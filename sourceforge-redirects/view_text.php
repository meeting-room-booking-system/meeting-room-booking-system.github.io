<?php

require_once __DIR__ . '/_redirect.php';

$documents = array(
  'readme' => '/documentation/readme/',
  'readme.md' => '/documentation/readme/',
  'install' => '/documentation/install/',
  'upgrade' => '/documentation/upgrade/',
  'authentication' => '/documentation/authentication/',
  'language' => '/documentation/language/',
  'news' => '/news/',
  'changelog' => '/changelog/',
  'license' => '/documentation/license/'
);

$file = isset($_GET['file']) && is_string($_GET['file'])
  ? strtolower(basename($_GET['file']))
  : '';

if (isset($documents[$file]))
{
  mrbs_redirect_to_site($documents[$file]);
}

mrbs_redirect_to_site('/documentation/');