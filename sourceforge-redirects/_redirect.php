<?php

function mrbs_redirect_to_site($path)
{
  header('Location: https://meeting-room-booking-system.github.io' . $path, true, 301);
  exit;
}

function mrbs_redirect_to_url($url)
{
  header('Location: ' . $url, true, 301);
  exit;
}