/* PTK Studio analytics: Google Analytics 4 (Firebase project ptk-studio-thetripnow),
   behind consent. Pattern from all-printable (docs/assets/js/core/analytics.js).

   - Nothing loads and no cookie is set until the visitor says yes. Say no
     (or send Do Not Track / Global Privacy Control) and gtag.js is never
     fetched.
   - The choice is remembered in localStorage and can be changed from any
     element with id="ptk-consent" (a footer link).
   - One page_view per page load (GA4's default for gtag 'config').

   The measurement ID is a public identifier, not a secret.
   ptk-studio#129 (Baseline: analytics). */
(function () {
  var MEASUREMENT_ID = 'G-2NJWE9YN45';
  var KEY = 'ptk.analytics.consent';

  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function remember(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function refused() {
    return navigator.doNotTrack === '1' || window.doNotTrack === '1' ||
           navigator.globalPrivacyControl === true;
  }
  function granted() { return !refused() && stored() === 'yes'; }

  var loaded = false;
  function load() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', MEASUREMENT_ID);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    document.head.appendChild(s);
  }

  function label() { return granted() ? 'Usage stats: on' : 'Usage stats: off'; }
  function refreshToggle() {
    var t = document.getElementById('ptk-consent');
    if (t) t.textContent = label();
  }

  function set(yes) {
    remember(yes ? 'yes' : 'no');
    var bar = document.getElementById('ptk-consent-bar');
    if (bar) bar.remove();
    if (yes) load();
    else if (loaded) location.reload(); /* drop the loaded tag */
    refreshToggle();
  }

  function banner() {
    if (refused() || stored()) return;
    var bar = document.createElement('div');
    bar.id = 'ptk-consent-bar';
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Usage statistics choice');
    bar.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;' +
      'max-width:560px;margin:0 auto;padding:12px 14px;border-radius:10px;' +
      'background:#1f2328;color:#fff;font:14px/1.4 system-ui,-apple-system,sans-serif;' +
      'box-shadow:0 4px 18px rgba(0,0,0,.25);display:flex;gap:12px;align-items:center;flex-wrap:wrap';
    bar.innerHTML =
      '<span style="flex:1 1 260px">May we count anonymous visits with Google Analytics, ' +
      'so we know what people find useful? <a href="/privacy/" style="color:#9ecbff">Privacy</a></span>' +
      '<span style="display:flex;gap:8px">' +
      '<button type="button" data-c="no" style="padding:6px 12px;border-radius:6px;border:1px solid #888;background:transparent;color:#fff;cursor:pointer">No thanks</button>' +
      '<button type="button" data-c="yes" style="padding:6px 12px;border-radius:6px;border:0;background:#2f81f7;color:#fff;cursor:pointer">Allow</button>' +
      '</span>';
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('[data-c]');
      if (b) set(b.getAttribute('data-c') === 'yes');
    });
    document.body.appendChild(bar);
  }

  /* Clicks that leave the site (the-trip-now-www#14), sent only while consent is on (gtag is loaded):
     - store_click: the store and its products (shop.88eggs.com, *.printify.me), with the product's
       utm_content (its slug), so First Cent can trace source -> visit -> product click;
     - outbound_click: any other link to another site (Instagram, the guides' Amazon links).
     The visit's own utm_source/medium/campaign are recorded by GA4 on the page_view. */
  function trackClick(e) {
    if (!loaded || !window.gtag) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var url;
    try { url = new URL(a.href, location.href); } catch (err) { return; }
    if (url.host === location.host || !/^https?:$/.test(url.protocol)) return;
    var store = /(^|\.)shop\.88eggs\.com$|\.printify\.me$|(^|\.)amazon\.com$/.test(url.hostname);
    var name = a.querySelector('.pname');
    window.gtag('event', store ? 'store_click' : 'outbound_click', {
      link_url: url.origin + url.pathname,
      link_domain: url.hostname,
      link_text: ((name || a).textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100),
      utm_content: url.searchParams.get('utm_content') || '',
      utm_campaign: url.searchParams.get('utm_campaign') || ''
    });
  }

  function init() {
    document.addEventListener('click', trackClick, true);
    if (refused()) { remember('no'); }
    if (granted()) load();
    banner();
    var t = document.getElementById('ptk-consent');
    if (t) {
      refreshToggle();
      t.addEventListener('click', function (e) { e.preventDefault(); set(!granted()); });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
