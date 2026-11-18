// The-trip-now-www#12: a visitor who arrives from a channel's bio link (thetripnow.com/?utm_source=instagram)
// keeps that source on the product links, so the store can tell which channel sold. Unknown sources are
// ignored; with no script, the links keep utm_source=thetripnow.
(function () {
  var allowed = ["instagram", "youtube", "pinterest"];
  var source;
  try {
    source = new URLSearchParams(window.location.search).get("utm_source");
  } catch (e) {
    return;
  }
  if (!source || allowed.indexOf(source.toLowerCase()) === -1) return;
  source = source.toLowerCase();
  var links = document.querySelectorAll("a.utm");
  for (var i = 0; i < links.length; i++) {
    var url = new URL(links[i].href);
    url.searchParams.set("utm_source", source);
    url.searchParams.set("utm_medium", "social");
    links[i].href = url.toString();
  }
})();
