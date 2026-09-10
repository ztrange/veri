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

/* veri, Annotated — scrollspy: where am I.
   Two readouts of one fact. The rail marks the entry you are inside; the sticky
   breadcrumb at the top of the page names its full path. Both read the same ordered
   model, window.__VERI_NAV__, which the generator builds from the same list the rail
   itself is rendered from — so they cannot disagree about section boundaries.

   Positions are measured once and cached, not recomputed per scroll event: this page
   is ~2300 lines of layout and a getBoundingClientRect() per entry per frame is enough
   to make scrolling stutter. The cache is dropped on resize, on font load (webfonts
   land after first paint and move everything down), and on hash navigation. */
(function () {
  "use strict";
  var NAV = window.__VERI_NAV__ || [];
  if (!NAV.length) return;

  var rail = document.querySelector(".rail");
  var crumb = document.querySelector(".crumb");
  var trail = crumb && crumb.querySelector(".crumb-trail");
  if (!rail || !trail) return;

  // one row per anchored entry: its heading, its rail link, its page offset
  var rows = [];
  for (var i = 0; i < NAV.length; i++) {
    var el = document.getElementById(NAV[i].id);
    if (!el) continue;                     // a nav entry with no heading is a build bug
    rows.push({ el: el, link: rail.querySelector('a[href="#' + NAV[i].id + '"]'),
                trail: NAV[i].trail, top: 0 });
  }
  if (!rows.length) return;

  var measured = false, current = -2;      // -2 so the first pass always paints

  function measure() {
    barH = crumb ? crumb.offsetHeight : 0;
    for (var i = 0; i < rows.length; i++) {
      rows[i].top = rows[i].el.getBoundingClientRect().top + window.scrollY;
    }
    measured = true;
  }
  function invalidate() { measured = false; schedule(); }

  /* The line that decides "inside": just below the sticky bar, plus a little, so a
     heading counts as current from the moment it clears the bar rather than when it
     reaches the top of the viewport. */
  var barH = 0;
  function line() {
    return window.scrollY + barH + 26;
  }

  function pick() {
    if (!measured) measure();
    // at the very bottom, the last section wins outright — it may be too short to
    // ever cross the line on its own, and "nothing selected" there reads as a bug
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
      return rows.length - 1;
    }
    var y = line(), idx = -1;
    for (var i = 0; i < rows.length; i++) {
      if (rows[i].top <= y) idx = i; else break;
    }
    return idx;
  }

  function seg(text, href, cls) {
    var node = document.createElement(href ? "a" : "span");
    if (href) node.setAttribute("href", "#" + href);
    if (cls) node.className = cls;
    node.innerHTML = text;               // labels carry entities, never markup
    return node;
  }

  function paint(idx) {
    if (idx === current) return;
    var prev = rows[current];
    if (prev && prev.link) {
      prev.link.classList.remove("on");
      prev.link.removeAttribute("aria-current");
    }
    current = idx;

    while (trail.firstChild) trail.removeChild(trail.firstChild);
    var row = rows[idx];
    if (!row) return;                    // above the first heading: just the home crumb

    if (row.link) {
      row.link.classList.add("on");
      row.link.setAttribute("aria-current", "true");
      reveal(row.link);
    }
    for (var i = 0; i < row.trail.length; i++) {
      var t = row.trail[i], last = i === row.trail.length - 1;
      trail.appendChild(seg("&rsaquo;", null, "sep"));
      var cls = last ? "here" : "";
      if (/\.sh$/.test(t.t)) cls += " file";
      trail.appendChild(seg(t.t, t.h || null, cls.trim() || null));
    }
  }

  /* Keep the marked entry inside the rail's own scrollport. Deliberately not
     scrollIntoView: that walks up and scrolls the window too, which would fight the
     scroll that triggered it. */
  function reveal(a) {
    var r = rail.getBoundingClientRect(), b = a.getBoundingClientRect();
    if (b.top < r.top + 8) rail.scrollTop -= (r.top + 8 - b.top);
    else if (b.bottom > r.bottom - 8) rail.scrollTop += (b.bottom - (r.bottom - 8));
  }

  /* A frame request alone is not enough. requestAnimationFrame does not fire while the
     document is not being painted — a background tab, an occluded window — and `queued`
     would then stay true forever, so every later schedule() returns early and the
     indicator never recovers even once the page is visible again. A timer races the
     frame; whichever arrives first does the work and the loser finds the latch clear. */
  var queued = false, timer = 0;
  function schedule() {
    if (queued) return;
    queued = true;
    var run = function () {
      if (!queued) return;
      queued = false;
      if (timer) { clearTimeout(timer); timer = 0; }
      paint(pick());
    };
    timer = setTimeout(run, 120);
    requestAnimationFrame(run);
  }

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", invalidate);
  window.addEventListener("hashchange", invalidate);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(invalidate);
  window.addEventListener("load", invalidate);
  schedule();
})();
