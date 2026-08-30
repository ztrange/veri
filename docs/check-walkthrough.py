#!/usr/bin/env python3
"""check-walkthrough.py — verify docs/walkthrough.html still describes the real scripts.

The walkthrough quotes each script verbatim, by line range. That is only useful while it
is true, so this checks the three ways it can silently rot:

  * every quoted listing matches the source byte-for-byte, at the stated line numbers
  * every stated total ("of 114") matches the file's real length
  * every in-page anchor link resolves to an id that exists

Run via `make docs-check`. Deliberately NOT part of `make test`: veri refuses to start a
cycle on a red baseline, and prose drifting behind code should not block a TDD run.

Exit: 0 all checks pass, 1 drift found (details on stdout).
"""
import re, html, pathlib, sys
doc = pathlib.Path("docs/walkthrough.html").read_text()
S = pathlib.Path(".claude/skills/solve-issue/scripts")
bad = []

ids = set(re.findall(r'id="([^"]+)"', doc))
links = set(re.findall(r'href="#([^"]+)"', doc))
if links - ids: bad.append("dangling anchors: %s" % sorted(links - ids))
print("anchors: %d ids / %d targets / %d dangling" % (len(ids), len(links), len(links - ids)))

gap = r'(?:(?!<span class="fname">).)*?'
pat = re.compile(r'<span class="fname">([^<]+)</span><span class="frange">L(\d+)&ndash;(\d+) of (\d+)</span>'
                 + gap + r'<pre class="src" style="counter-reset: ln (\d+)">(.*?)</pre>', re.S)
n = 0
for fname, first, last_, total, ctr, body in pat.findall(doc):
    n += 1
    src = (S / fname).read_text().splitlines()
    if len(src) != int(total): bad.append("%s: total %s != %d" % (fname, total, len(src)))
    if int(ctr) != int(first) - 1: bad.append("%s: counter %s vs L%s" % (fname, ctr, first))
    lines = [html.unescape(re.sub(r'</?span[^>]*>', '', m.group(1)))
             for m in re.finditer(r'<span class="l">(.*?)</span>(?=\n|$)', body)]
    want = src[int(first) - 1:int(last_)]
    if lines != want:
        for i, (g, w) in enumerate(zip(lines, want)):
            if g != w: bad.append("%s L%d\n   doc: %r\n   src: %r" % (fname, int(first)+i, g, w))
        if len(lines) != len(want):
            bad.append("%s: %d lines quoted, range spans %d" % (fname, len(lines), len(want)))
print("listings: %d checked" % n)

# unclosed-tag smoke test
for tag in ("div", "span", "pre", "p", "table"):
    o = len(re.findall(r'<%s[ >]' % tag, doc)); c = len(re.findall(r'</%s>' % tag, doc))
    if o != c: bad.append("tag balance <%s>: %d open / %d close" % (tag, o, c))

print("\n".join(bad) if bad else "\nALL CHECKS PASS")
sys.exit(1 if bad else 0)
