"""parse-verdict.sh's transform, run in-process."""
import re
import string
import sys

SPACE = " \t\n\v\f\r"


def labelled(label):
    return re.compile(f"^[{SPACE}]*{label}:[{SPACE}]*(.*)$", re.IGNORECASE | re.ASCII)


VERDICT_RE = labelled("verdict")
REASON_RE = labelled("reason")
FENCE_RE = re.compile(f"^[{SPACE}]*(```|~~~)[{SPACE}]*$")
UPPER = str.maketrans(string.ascii_lowercase, string.ascii_uppercase)
CODES = {"PASS": 0, "REJECT": 1}


def read_lines(text):
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def last_verdict(lines):
    vidx = -1
    for i, line in enumerate(lines):
        if VERDICT_RE.match(line):
            vidx = i
    return vidx


def first_token(text):
    return re.split(f"[{SPACE}]", text, maxsplit=1)[0]


def inline_reason(tail, token):
    inline = tail[len(token):].lstrip(SPACE)
    for sep in ("—", "–", "-", ":"):
        inline = inline.removeprefix(sep)
    return inline.lstrip(SPACE)


def following_reason(rest):
    if not rest:
        return ""
    match = REASON_RE.match(rest[0])
    if match:
        rest = [match.group(1), *rest[1:]]
    return "".join(f"{line}\n" for line in rest)


def drop_closing_fence(reason):
    head, _, last = reason.rpartition("\n")
    if FENCE_RE.match(last):
        return head.rstrip(SPACE)
    return reason


def main(argv):
    lines = read_lines(sys.stdin.read())
    vidx = last_verdict(lines)
    if vidx < 0:
        print("parse-verdict: no VERDICT: line found", file=sys.stderr)
        return 2
    tail = VERDICT_RE.match(lines[vidx]).group(1)
    token = first_token(tail)
    word = token.translate(UPPER)
    if word not in CODES:
        print(f"parse-verdict: unrecognised verdict word '{word}'", file=sys.stderr)
        return 2
    reason = following_reason(lines[vidx + 1:]).rstrip(SPACE) or inline_reason(tail, token)
    print(drop_closing_fence(reason.strip(SPACE)))
    return CODES[word]


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
