"""parse-verdict.sh's transform, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import re
import string
import sys

SPACE = " \t\n\v\f\r"


def labelled(label):
    return re.compile(f"^[{SPACE}]*{label}:[{SPACE}]*(.*)$", re.IGNORECASE | re.ASCII)


VERDICT_RE = labelled("verdict")
REASON_RE = labelled("reason")
MISSING_TEST_RE = labelled("missing_test")
FLAGS_RE = labelled("flags")
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


def preceding_reason(before):
    kept = []
    in_block = False
    for line in before:
        match = REASON_RE.match(line)
        if match:
            kept.append(match.group(1))
            in_block = True
        elif MISSING_TEST_RE.match(line):
            kept.append(line)
        elif in_block and not FLAGS_RE.match(line):
            kept.append(line)
    return "\n".join(kept)


def drop_closing_fence(reason):
    head, _, last = reason.rpartition("\n")
    if FENCE_RE.match(last):
        return head.rstrip(SPACE)
    return reason


USAGE = "usage: parse-verdict.sh < leaf-output.txt"


def verdict(text):
    """Read the leaf output `text`; answer `(code, reason, err)`, printing nothing.

    `code` is 0 for PASS, 1 for REJECT, 2 when no answer exists (no VERDICT: line,
    or an unrecognised word). `reason` is what the shim prints on stdout, without
    its trailing newline ("" on code 2). `err` is the stderr line, newline included
    ("" unless code 2).
    """
    lines = read_lines(text)
    vidx = last_verdict(lines)
    if vidx < 0:
        return 2, "", "parse-verdict: no VERDICT: line found\n"
    tail = VERDICT_RE.match(lines[vidx]).group(1)
    token = first_token(tail)
    word = token.translate(UPPER)
    if word not in CODES:
        return 2, "", f"parse-verdict: unrecognised verdict word '{word}'\n"
    after = following_reason(lines[vidx + 1:]).rstrip(SPACE) or inline_reason(tail, token)
    if after:
        missing = [line for line in lines[:vidx] if MISSING_TEST_RE.match(line)]
        reason = "\n".join([*missing, after])
    else:
        reason = preceding_reason(lines[:vidx])
    return CODES[word], drop_closing_fence(reason.strip(SPACE)), ""


def main(argv):
    code, reason, err = verdict(sys.stdin.read())
    sys.stderr.write(err)
    if code != 2:
        print(reason)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
