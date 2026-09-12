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

/* veri, Annotated — since-mode: which hunks are news to me.
   A reader who last read the page at some version wants the runs of lines tagged after
   it lit and the rest dimmed. This is the decision itself, kept apart from whatever
   paints it: given a hunk's tag and the version the reader last read, is that hunk
   news?

   The order is window.__VERI_ORDER__, the build's tag list in git's version sort — never
   a comparison of the tag strings, which put v0.10 before v0.9 and would hide the newest
   capability from exactly the reader who asked to see it. A hunk tagged X is not later
   than X: the reader has already seen it. */
(function () {
  "use strict";
  var ORDER = window.__VERI_ORDER__ || [];
  var HUNKS = window.__VERI_HUNKS__ || {};

  /* Where each script sits on the page, by file name. window.__VERI_SCRIPTS__ is the
     build's list of the scripts in document order, taken from the same entries the
     listings and the rail are rendered from, so it cannot disagree with them. */
  var PAGE_RANK = {};
  (window.__VERI_SCRIPTS__ || []).forEach(function (file, i) { PAGE_RANK[file] = i; });

  /* Page order, as a comparison of two hunk entries: the order the page lists the
     scripts, and within one script the lowest line first. An entry is
     [script, first, last, description]. Never the script's NAME, which puts
     classify-bail.sh before supervise.sh as text and after it on the page. A script the
     nav does not carry has no place on the page, so it sorts last rather than poisoning
     the comparison with a NaN. */
  function rank(entry) {
    var r = PAGE_RANK[entry[0]];
    return r === undefined ? Infinity : r;
  }
  function byPageOrder(a, b) { return rank(a) - rank(b) || a[1] - b[1]; }

  function lit(tag, since) {
    var hunkRank = ORDER.indexOf(tag), readRank = ORDER.indexOf(since);
    // -1 is what indexOf answers for a tag the order does not carry, and it ranks below
    // every real one — so an unknown tag is never later than a known choice, and an
    // unknown choice lights nothing. One comparison says both.
    return readRank >= 0 && hunkRank > readRank;
  }

  /* The capabilities that choice lights, newest first — the index's rows, in the order
     the index prints them. Which versions are lit is lit()'s answer and only lit()'s,
     here as in walk() below, so the two can never disagree about that; what this adds is
     an ORDER the index needs and the walk must not inherit.

     Read out of ORDER, never out of window.__VERI_HUNKS__: the map is keyed by the tags
     that own a hunk, so a capability that changed nothing this page quotes is absent from
     it, and walking the map would tell the reader a version they have not read does not
     exist. Its keys are a JSON object's besides, which is to say lexical — v0.10 before
     v0.9. */
  function litTags(since) {
    var tags = [];
    for (var i = ORDER.length - 1; i >= 0; i--) {
      if (lit(ORDER[i], since)) tags.push(ORDER[i]);
    }
    return tags;
  }

  /* The capability index for that same reader: the versions after the one they last
     read, newest first, each carrying the hunks it touched so the row says WHERE it
     changed something and not only that it did. A version that touched nothing the page
     quotes is a row with an empty list. */
  function index(since) {
    var rows = [], tags = litTags(since);
    for (var i = 0; i < tags.length; i++) {
      rows.push({ tag: tags[i], hunks: HUNKS[tags[i]] || [] });
    }
    return rows;
  }

  /* The lit hunks in page order: the stops n and p — and the two buttons in the crumb
     bar — step through, so that next always moves the reader down the page and previous
     always back up it.

     The stops are read straight out of window.__VERI_HUNKS__ — every run a lit tag owns,
     in whatever order the map hands its keys over — and byPageOrder above is what turns
     that into a walk. Not out of litTags(): its newest-first order is the index's, and
     borrowing it would leave the walk's result standing on how the index chose to print
     its rows rather than on the sort, silently, for as long as the two happened to agree.
     Unsorted the hunks arrive grouped by capability, so one script's runs are scattered
     across several groups and the scripts interleaved — a reader pressing n through that
     is thrown up and down two thousand lines of listing.

     The map is the right authority for stops where it was the wrong one for rows: a
     capability that touched nothing this page quotes contributes no stop, which is
     exactly its absence from the map, whereas the index still owes it a row. */
  function walk(since) {
    var stops = [];
    Object.keys(HUNKS).forEach(function (tag) {
      if (lit(tag, since)) stops = stops.concat(HUNKS[tag]);
    });
    return stops.sort(byPageOrder);
  }

  /* The version this page is in, and a reader choosing one — since-mode's only durable
     state. Kept in a variable it would die with the tab: nothing to bookmark, nothing to
     paste to whoever asked what changed, and a reader who comes back sets it up again. The
     address bar is the one place a browser hands back on the next load, so that is where
     it lives, as `#since=vX`; choose() writes it there and since() reads the same place,
     which is the whole of why reloading that URL comes up in the mode.

     Read live rather than captured at load, so the address and the mode are one fact
     instead of a copy that can lag it. The leading `#` is a delimiter the browser puts
     back on the getter whatever was assigned, not part of the choice, and a hash that is
     not a `since=` — a link to a script's own section — names no version: both fall out
     of the match. Which tag a reader may name is lit()'s business, not this one's.

     The two spell `since=` once between them, HASH_PREFIX, and the pattern is built from
     it rather than written out a second time: they are the ends of one round trip, and a
     page that writes one key and reads another restores nothing while both halves keep
     passing their own read. */
  var HASH_PREFIX = "since=";
  var HASH_RE = new RegExp("^#?" + HASH_PREFIX + "(.+)$");

  function since() {
    var m = HASH_RE.exec(location.hash || "");
    return m ? m[1] : "";
  }

  function choose(tag) { location.hash = HASH_PREFIX + tag; }

  window.__VERI_SINCE__ = { lit: lit, index: index, walk: walk,
                            since: since, choose: choose };
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
