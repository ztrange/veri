#!/usr/bin/env python3
"""parse_verdict — extract a blind verifier leaf's structured verdict from its output.

Port of parse-verdict.sh (measurement spike). The CLI contract is the bash script's,
byte for byte: stdin is the leaf's raw output, stdout is the trimmed reason, exit 0 PASS,
1 REJECT, 2 malformed (stdout empty, one diagnostic on stderr). The LAST `VERDICT:` line
is the authoritative one; the reason is the following block (a leading `REASON:` label
stripped) or, failing that, the text inline after the verdict word.

Stdlib only. Text is handled as bytes decoded with surrogateescape so an invalid UTF-8
byte in the leaf's output round-trips the way bash's byte strings do.
"""
import re
import sys

# bash's [[:space:]] under LC_ALL=C: the six ASCII whitespace bytes, nothing more. Python's
# \s would also match Unicode spaces, which the bash script never treated as space.
_WS = " \t\r\n\f\v"
_WS_CLASS = "[" + re.escape(_WS) + "]"
# [Vv][Ee]… in the bash script is ASCII case-folding; re.ASCII keeps re.I from folding
# Unicode look-alikes (U+017F ſ → s, U+212A K → k) the bash regex would not.
_VERDICT_RE = re.compile(r"^" + _WS_CLASS + r"*verdict:" + _WS_CLASS + r"*(.*)$", re.I | re.A)
_REASON_RE = re.compile(r"^" + _WS_CLASS + r"*reason:" + _WS_CLASS + r"*(.*)$", re.I | re.A)
_FENCE_RE = re.compile(r"^" + _WS_CLASS + r"*(```|~~~)" + _WS_CLASS + r"*$")
_SEPARATORS = ("—", "–", "-", ":")  # '—' '–' '-' ':' in the bash script's order
_UPPER = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

EXIT_PASS = 0
EXIT_REJECT = 1
EXIT_MALFORMED = 2


def ltrim(s):
    return s.lstrip(_WS)


def rtrim(s):
    return s.rstrip(_WS)


def split_lines(text):
    """The lines `while IFS= read -r line || [[ -n "$line" ]]` yields: a trailing newline
    ends the last line rather than starting an empty one, and empty input is no lines."""
    if text == "":
        return []
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    return lines


def parse(text):
    """Return (exit_code, reason, diagnostic). reason is the stdout text (without its
    trailing newline) when the code is 0 or 1; diagnostic is the stderr line when it is 2."""
    lines = split_lines(text)
    vidx = -1
    tail = ""
    for i, line in enumerate(lines):
        m = _VERDICT_RE.match(line)
        if m:
            vidx = i
            tail = m.group(1)
    if vidx < 0:
        return EXIT_MALFORMED, "", "parse-verdict: no VERDICT: line found"

    # Verdict word = first whitespace-delimited token of the tail, upper-cased (ASCII only,
    # the way `tr '[:lower:]' '[:upper:]'` folds under LC_ALL=C).
    word_raw = re.split(_WS_CLASS, tail, maxsplit=1)[0]
    word = word_raw.translate(_UPPER)
    if word == "PASS":
        code = EXIT_PASS
    elif word == "REJECT":
        code = EXIT_REJECT
    else:
        return EXIT_MALFORMED, "", "parse-verdict: unrecognised verdict word '%s'" % word

    # Inline reason = the verdict line after the word, one leading separator stripped.
    inline = ltrim(tail[len(word_raw):])
    for sep in _SEPARATORS:
        if inline.startswith(sep):
            inline = inline[len(sep):]
    inline = ltrim(inline)

    # Following reason = the lines after the verdict line, a leading REASON: label stripped
    # from the first; `printf -v following '%s\n'` puts a newline after every line.
    following = ""
    if vidx + 1 < len(lines):
        rest = lines[vidx + 1:]
        m = _REASON_RE.match(rest[0])
        if m:
            rest[0] = m.group(1)
        following = "".join(r + "\n" for r in rest)

    reason = rtrim(following)
    if reason == "":
        reason = inline
    reason = rtrim(ltrim(reason))

    # A closing ``` or ~~~ fence trailing the reason is dropped, as a whole line.
    last = reason.rsplit("\n", 1)[-1]
    if _FENCE_RE.match(last):
        reason = reason.rsplit("\n", 1)[0] if "\n" in reason else ""
        reason = rtrim(reason)

    return code, reason, ""


def main(stdin=None, stdout=None, stderr=None):
    stdin = sys.stdin if stdin is None else stdin
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    data = stdin.buffer.read().decode("utf-8", "surrogateescape")
    code, reason, diagnostic = parse(data)
    if code == EXIT_MALFORMED:
        stderr.buffer.write((diagnostic + "\n").encode("utf-8", "surrogateescape"))
        stderr.buffer.flush()
    else:
        stdout.buffer.write((reason + "\n").encode("utf-8", "surrogateescape"))
        stdout.buffer.flush()
    return code


if __name__ == "__main__":
    sys.exit(main())
