(function () {
  'use strict';

  var script = document.currentScript;
  var gaId = script.getAttribute('data-ga-id');
  var privacyUrl = script.getAttribute('data-privacy-url');
  var STORAGE_KEY = 'mrbs-analytics-consent';

  function getSafePrivacyUrl(url) {
    try {
      var parsed = new URL(url, window.location.origin);
      if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
        return parsed.href;
      }
    } catch (e) {
      // Fall through to safe default.
    }
    return '/privacy';
  }

  function getChoice() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setChoice(value) {
    try {
      if (value === null) {
        window.localStorage.removeItem(STORAGE_KEY);
      } else {
        window.localStorage.setItem(STORAGE_KEY, value);
      }
    } catch (e) {
      // Storage unavailable: the choice applies to this page view only.
    }
  }

  function loadAnalytics() {
    if (window.mrbsAnalyticsLoaded) {
      return;
    }
    window.mrbsAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag('js', new Date());
    window.gtag('config', gaId);

    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(gaId);
    document.head.appendChild(tag);
  }

  function removeAnalyticsCookies() {
    var names = document.cookie.split(';').map(function (c) {
      return c.split('=')[0].trim();
    }).filter(function (name) {
      return name === '_ga' || name.indexOf('_ga_') === 0;
    });
    var host = window.location.hostname.split('.');
    var domains = [window.location.hostname];
    for (var i = 1; i < host.length - 1; i++) {
      domains.push('.' + host.slice(i).join('.'));
    }
    names.forEach(function (name) {
      domains.forEach(function (domain) {
        document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=' + domain;
      });
      document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    });
  }

  var banner = null;

  function hideBanner() {
    if (banner) {
      banner.remove();
      banner = null;
    }
  }

  function showBanner() {
    if (banner) {
      return;
    }
    banner = document.createElement('div');
    banner.className = 'consent-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-labelledby', 'consent-title');

    var text = document.createElement('p');
    var title = document.createElement('strong');
    title.id = 'consent-title';
    title.textContent = 'Analytics cookies';
    text.appendChild(title);
    text.appendChild(document.createTextNode(
      ' We would like to use Google Analytics cookies to understand how this site is used. ' +
      'Nothing is collected unless you accept. '));
    var link = document.createElement('a');
    link.href = getSafePrivacyUrl(privacyUrl);
    link.textContent = 'Privacy information';
    text.appendChild(link);

    var actions = document.createElement('div');
    actions.className = 'consent-actions';

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.className = 'consent-button';
    decline.textContent = 'Decline';
    decline.addEventListener('click', function () {
      setChoice('denied');
      removeAnalyticsCookies();
      hideBanner();
    });

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'consent-button';
    accept.textContent = 'Accept';
    accept.addEventListener('click', function () {
      setChoice('granted');
      loadAnalytics();
      hideBanner();
    });

    actions.appendChild(decline);
    actions.appendChild(accept);
    banner.appendChild(text);
    banner.appendChild(actions);
    document.body.appendChild(banner);
    accept.focus();
  }

  var settings = document.querySelector('[data-cookie-settings]');
  if (settings) {
    settings.hidden = false;
    settings.addEventListener('click', function () {
      setChoice(null);
      showBanner();
    });
  }

  var choice = getChoice();
  if (choice === 'granted') {
    loadAnalytics();
  } else if (choice !== 'denied') {
    showBanner();
  }
}());
