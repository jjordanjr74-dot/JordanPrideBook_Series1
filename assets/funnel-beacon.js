/* First-party conversion-intent beacon (jordanpride / JordanPrideBook_Series1).
 * Records ONLY {venture, event, page-path} via 1x1 pixel GET to https://app.thesoapbook.com/t/px.gif.
 * Zero cookies, zero PII, zero third-party tracker.
 */
(function () {
  var V = "jordanpride";
  var URL = "https://app.thesoapbook.com/t";

  function send(ev) {
    try {
      var img = new Image(1, 1);
      img.src = URL + "/px.gif?v=" + encodeURIComponent(V)
              + "&e=" + encodeURIComponent(ev)
              + "&p=" + encodeURIComponent(location.pathname)
              + "&_=" + Date.now();
    } catch (e) {}
  }

  document.addEventListener("click", function (ev) {
    var el = ev.target;
    var a = el && el.closest ? el.closest("a") : null;
    if (!a) { return; }
    var h = a.getAttribute("href") || "";
    if (h.indexOf("tel:") === 0) { send("tel_click"); }
    else if (h.indexOf("mailto:") === 0) { send("email_click"); }
    else if (h.indexOf("checkout.stripe.com") > -1 || h.indexOf("buy.stripe.com") > -1) { send("checkout_click"); }
  }, true);

  window.addEventListener("load", function () { send("view"); });
})();
