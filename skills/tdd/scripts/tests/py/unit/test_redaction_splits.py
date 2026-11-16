"""redaction.redact against a secret split at every position by every kind of line break, indent, markdown prefix,
trailing backslash or zero-width character, and against prose holding no secret (#3960).

Every secret here is built from a documented shape with an obviously fake body (hex digests of fixed `veri-fake-…`
strings); none is read from the environment."""
import base64
import hashlib
import importlib

import pytest


def fake(seed, length):
    """<length> characters of hex, the same on every run, from the fixed seed `veri-fake-<seed>`."""
    text = ""
    while len(text) < length:
        text += hashlib.sha256(("veri-fake-%s-%d" % (seed, len(text))).encode()).hexdigest()
    return text[:length]


VALUE = "fake-gh-token-value-" + fake("value", 12)
SECRETS = {
    "classic": "ghp_" + fake("classic", 36),
    "fine-grained": "github_pat_" + fake("pat-a", 22) + "_" + fake("pat-b", 59),
    "anthropic": "sk-ant-api03-" + fake("ant-a", 60) + "-" + fake("ant-b", 34),
    "aws": "AKIA" + fake("aws", 16).upper(),
    "env value": VALUE,
}
BREAKS = {
    "LF": "\n", "CRLF": "\r\n", "JSON \\n": "\\n", "indent 1": "\n ", "indent 4": "\n    ", "indent 40": "\n" + " " * 40,
    "tab": "\n\t", "two trailing spaces": "  \n", "trailing backslash": "\\\n", "> ": "\n> ", "- ": "\n- ",
    "* ": "\n* ", "# ": "\n# ", "  > ": "\n  > ", "> > ": "\n> > ", "zero-width": "​",
    "gh CI log line": "\nbuild\tRun make test\t2026-11-16T10:20:30.1234567Z ",
    "ISO timestamp": "\n2026-11-16T10:20:30Z ",
}


@pytest.fixture
def redaction(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", VALUE)
    return importlib.import_module("veri.redaction")


def leaked(secret, output):
    """The first run of 8 consecutive characters of <secret> still in <output>, or None."""
    return next((secret[i:i + 8] for i in range(len(secret) - 7) if secret[i:i + 8] in output), None)


@pytest.mark.parametrize("shape", sorted(SECRETS))
def test_a_secret_split_at_any_position_by_any_break_is_redacted_whole_issue_3960(redaction, shape):
    secret = SECRETS[shape]
    failures = []
    for style, mark in sorted(BREAKS.items()):
        for at in range(1, len(secret)):
            output = redaction.redact("before %s%s%s after" % (secret[:at], mark, secret[at:]))
            if leaked(secret, output):
                failures.append((shape, style, at, leaked(secret, output)))

    assert failures == [], "%d of %d triples leak; first: %r" % (
        len(failures), len(BREAKS) * (len(secret) - 1), failures[0])


@pytest.mark.parametrize("shape", sorted(SECRETS))
def test_a_secret_split_three_ways_at_two_fixed_positions_is_redacted_whole_issue_3960(redaction, shape):
    secret = SECRETS[shape]
    first, second = len(secret) // 3, 2 * len(secret) // 3 + 1
    failures = []
    for one, two in [("\n> ", "\n  - "), ("\\\n", "​"), ("  \n", "\\n    "), ("\r\n# ", "\n\t")]:
        output = redaction.redact("x %s%s%s%s%s y" % (secret[:first], one, secret[first:second], two, secret[second:]))
        if leaked(secret, output):
            failures.append((one, two, leaked(secret, output)))

    assert failures == []


PNG = base64.b64encode(bytes(range(256)) * 3).decode()
PROSE = "\n".join([
    "## Plan for #3968 — redaction",
    "",
    "- [x] the comment is posted",
    "- [ ] the body is written ⟂ refactor pending",
    "  - a nested bullet with `code` in it",
    "* another bullet",
    "+ and a plus bullet",
    "> a quoted line from the issue",
    "> > a nested quote",
    "  > an indented quote",
    "# A heading",
    "### ✅ Done",
    "Closes #3968",
    "commit 0123456789abcdef0123456789abcdef01234567 landed",
    "run 123e4567-e89b-12d3-a456-426614174000 finished",
    "![chart](data:image/png;base64,%s)" % PNG,
    "- apple",
    "- pear",
    "- fig",
    "trailing backslash \\",
    "the end, with two trailing spaces  ",
    "and a JSON line {\"out\": \"step 3 FAIL\\nassert 1 == 2\\n\"}",
])


def test_prose_holding_no_secret_is_left_byte_identical_issue_3960(redaction):
    assert redaction.redact(PROSE) == PROSE


FULL_LENGTH = {"classic": SECRETS["classic"], "fine-grained": SECRETS["fine-grained"], "aws": SECRETS["aws"],
               "env value": VALUE, "anthropic at its cap": "sk-ant-" + fake("ant-cap", 101)}
NEXT_LINES = ["### ✅ Done", "- [ ] step", "- apple", "* bullet", "# Heading", "> quoted", "2. item", "Closes #123",
              "--flag"]


@pytest.mark.timeout(10)
@pytest.mark.parametrize("shape", sorted(FULL_LENGTH))
def test_1_mb_of_one_full_length_token_per_line_is_answered_within_the_case_timeout_issue_3960(redaction, shape):
    lines = 1048576 // (len(FULL_LENGTH[shape]) + 1)

    assert redaction.redact((FULL_LENGTH[shape] + "\n") * lines) == "[redacted]\n" * lines


@pytest.mark.parametrize("shape", sorted(FULL_LENGTH))
def test_a_full_length_token_at_a_lines_end_leaves_the_next_line_byte_identical_issue_3960(redaction, shape):
    changed = [line for line in NEXT_LINES if redaction.redact("token: %s\n%s\nlast" % (FULL_LENGTH[shape], line))
               != "token: [redacted]\n%s\nlast" % line]

    assert changed == []
