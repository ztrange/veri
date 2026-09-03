/* veri, Annotated — tooltip layer.
   Every {{ref}} in the commentary is emitted as a real <a href="#p-id"> first, so the
   page works with no JS: the link jumps to the full reference entry. This adds the
   hover/focus preview on top. The tip is appended to <body> rather than nested in the
   link, because listings are overflow-x:auto containers that would clip it. */
(function () {
  "use strict";
  var TIPS = window.__VERI_TIPS__ || {};
  var tip = null, current = null, hideTimer = null;

  function build() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "tip";
    tip.setAttribute("role", "tooltip");
    tip.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
    tip.addEventListener("mouseleave", scheduleHide);
    document.body.appendChild(tip);
    return tip;
  }

  function show(link) {
    var id = link.getAttribute("data-ref");
    var d = TIPS[id];
    if (!d) return;
    clearTimeout(hideTimer);
    current = link;
    var t = build();
    t.innerHTML =
      '<span class="tip-sig">' + d.sig + "</span>" +
      '<span class="tip-name">' + d.name + "</span>" +
      "<p>" + d.gloss + "</p>" +
      '<a class="tip-go" href="#' + id + '">Open full reference &rarr;</a>';
    t.classList.add("on");
    place(link, t);
  }

  function place(link, t) {
    // measure off-screen first so width/height are real before we clamp
    t.style.left = "-9999px"; t.style.top = "0";
    var r = link.getBoundingClientRect();
    var tw = t.offsetWidth, th = t.offsetHeight;
    var pad = 10;
    var left = r.left + window.scrollX + r.width / 2 - tw / 2;
    var maxLeft = window.scrollX + document.documentElement.clientWidth - tw - pad;
    left = Math.max(window.scrollX + pad, Math.min(left, maxLeft));
    // above the link if there is room, otherwise below
    var top = r.top + window.scrollY - th - 9;
    if (r.top - th - 9 < 0) top = r.bottom + window.scrollY + 9;
    t.style.left = Math.round(left) + "px";
    t.style.top = Math.round(top) + "px";
  }

  function scheduleHide() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hide, 160);
  }
  function hide() {
    if (!tip) return;
    tip.classList.remove("on");
    current = null;
  }

  document.addEventListener("mouseover", function (e) {
    var link = e.target.closest && e.target.closest("a.tt");
    if (link) { show(link); }
    else if (current && !(e.target.closest && e.target.closest(".tip"))) { scheduleHide(); }
  });
  document.addEventListener("focusin", function (e) {
    var link = e.target.closest && e.target.closest("a.tt");
    if (link) show(link);
  });
  document.addEventListener("focusout", function (e) {
    if (e.target.closest && e.target.closest("a.tt")) scheduleHide();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") hide();
  });
  window.addEventListener("scroll", function () { if (current) place(current, tip); }, { passive: true });
  window.addEventListener("resize", hide);

  /* Jumping to a reference entry should make it obvious which one you landed on.
     :target handles the styling; this only covers arriving at an id already in the URL. */
  function flash() {
    var id = location.hash.slice(1);
    if (!id) return;
    var el = document.getElementById(id);
    if (el && el.classList.contains("card")) el.scrollIntoView({ block: "center" });
  }
  window.addEventListener("hashchange", hide);
  if (document.readyState !== "loading") flash();
  else document.addEventListener("DOMContentLoaded", flash);
})();
