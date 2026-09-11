"""bashlex.py — the smallest bash lexer that makes these listings easier to read.

Not a parser, and deliberately not a general one: it colours four things — comments,
quoted strings, parameter expansions and control words — and leaves everything else
as plain code ink. Restraint is the point. The prose column carries the explanation;
the listing only needs enough colour to separate "text" from "code" at a glance.

The contract that makes it safe to run over real source: **the concatenation of every
token's text is the input line, byte for byte**. build-walkthrough.py asserts that on
every line it renders and refuses to emit a page if it ever fails, so a lexer bug
becomes a build error rather than a silently corrupted listing. check-walkthrough.py
then re-checks the rendered page against the real files independently.

Why each rule is shaped the way it is — all three were found in this corpus:

  ${...} is consumed by BRACE DEPTH, not by searching for '}'. parse-verdict.sh has
  "${1#"${1%%[![:space:]]*}"}" — an expansion nested inside a quote nested inside an
  expansion. Depth counting carries the whole thing through as one token; anything
  looking for the first '}' stops in the middle of it.

  '$' is handled BEFORE '#'. supervise.sh has [[ $# -ge 1 ]]; if '#' were tested
  first, the rest of that line would turn into a comment.

  A '#' only opens a comment at the start of a word — line start or after
  whitespace. Otherwise ${tail#...} and $# would both start one.

There are no heredocs in the scripts this renders, but quote state is still carried
across lines rather than reset per line, so a string that spans lines cannot leak its
colour into the rest of the file unnoticed.
"""
import re

# Control words and the builtins that read as structure. Highlighted only as whole
# words in command position-ish contexts; a word like "done" inside a string or an
# expansion never reaches this test, because those are consumed first.
KEYWORDS = frozenset("""
if then elif else fi for while until do done case esac in function select
local return exit break continue shift set trap eval exec export readonly declare
""".split())

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# $name  $1  $?  $!  $@  $#  $*  $$  $0
SIMPLE_VAR = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*|[0-9]|[?!@#*$-])")


def _expansion(s, i):
    """End index of a ${...} starting at i, by brace depth. -1 if never closed."""
    # i is AT the '{'. Counting it is the whole point: start at depth 1 and the
    # matching brace is the one that brings it back to 0. Starting at 0 instead
    # sends the first '}' to -1, so ${VAR:-} never closes and the rest of the line
    # is swallowed into the expansion — which is exactly what this did at first.
    depth = 1
    j = i + 1
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return -1


def tokens(line, state):
    """[(cls, text)] for one line. cls is '' for plain code.

    state is a one-key dict {'q': None | "'" | '"'} carried between lines.
    """
    out = []
    buf = []
    i, n = 0, len(line)

    def flush(cls=""):
        if buf:
            out.append((cls, "".join(buf)))
            buf.clear()

    while i < n:
        ch = line[i]

        # ── inside a single-quoted string: everything is literal until the quote ──
        if state["q"] == "'":
            j = line.find("'", i)
            if j < 0:
                out.append(("s", line[i:])); i = n; break
            out.append(("s", line[i:j + 1])); i = j + 1; state["q"] = None
            continue

        # ── inside a double-quoted string: expansions still show through ──────────
        if state["q"] == '"':
            start = i
            while i < n:
                if line[i] == "\\" and i + 1 < n:
                    i += 2; continue
                if line[i] == '"':
                    i += 1; state["q"] = None; break
                if line[i] == "$" and i + 1 < n and line[i + 1] in "{" :
                    break
                if line[i] == "$" and SIMPLE_VAR.match(line, i):
                    break
                i += 1
            if i > start:
                out.append(("s", line[start:i]))
            if state["q"] == '"' and i < n and line[i] == "$":
                i = _emit_var(line, i, out)
            continue

        # ── plain code ────────────────────────────────────────────────────────────
        if ch == "$":
            flush()
            j = _emit_var(line, i, out)
            if j == i:                       # a bare '$' that starts nothing
                buf.append(ch); i += 1
            else:
                i = j
            continue

        if ch in "'\"":
            flush()
            state["q"] = ch
            out.append(("s", ch))
            i += 1
            continue

        # The shebang is not a comment — it is the one line the kernel reads, and the
        # page has always shown it as code. Kept as it was.
        if i == 0 and line.startswith("#!"):
            buf.append(line); i = n
            break

        # a comment only opens at the start of a word
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            flush()
            out.append(("c", line[i:]))
            i = n
            break

        m = WORD.match(line, i)
        if m and (i == 0 or not (line[i - 1].isalnum() or line[i - 1] in "_-./$")):
            w = m.group(0)
            if w in KEYWORDS:
                flush()
                out.append(("k", w))
                i = m.end()
                continue
            buf.append(w); i = m.end(); continue

        buf.append(ch)
        i += 1

    flush()
    merged = []
    for cls, text in out:
        if merged and merged[-1][0] == cls:
            merged[-1] = (cls, merged[-1][1] + text)
        else:
            merged.append((cls, text))
    return merged


def _emit_var(line, i, out):
    """Emit one $-expansion at i; return the new index (== i if there was none)."""
    if line.startswith("${", i):
        end = _expansion(line, i + 1)
        if end > 0:
            out.append(("v", line[i:end])); return end
        out.append(("v", line[i:])); return len(line)
    m = SIMPLE_VAR.match(line, i)
    if m:
        out.append(("v", m.group(0))); return m.end()
    return i


def highlight(lines):
    """[(cls, text)] per input line, with quote state carried across lines."""
    state = {"q": None}
    return [tokens(ln, state) for ln in lines]
