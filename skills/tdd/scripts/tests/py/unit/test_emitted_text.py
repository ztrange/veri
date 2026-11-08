"""Emitted-text pins: every script's usage text on a missing argument, byte-identical by `cksum`.

Each pin is the cksum of the `exit N` line, then the script's stdout then stderr with trailing
newlines stripped, then one trailing newline — not of the bare usage text.

Each case's subject is text the scripts emit, driven in-process through each script's module.
"""
import importlib


def cksum(data):
    """POSIX cksum: CRC-32 (poly 0x04C11DB7, MSB first) over the bytes then the length, complemented."""
    table = []
    for byte in range(256):
        crc = byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
        table.append(crc)
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[(crc >> 24) ^ byte]
    length = len(data)
    while length:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[(crc >> 24) ^ (length & 0xFF)]
        length >>= 8
    return "%d %d" % (crc ^ 0xFFFFFFFF, len(data))

USAGE = [
    ("3345015868 167", "add-ledger-step.sh", []),
    ("3115481657 48", "affected-suites.sh", []),
    ("1250444232 315", "build-develop-prompt.sh", []),
    ("1786216893 158", "build-verify-prompt.sh", []),
    ("3916945256 64", "clear-refactor-pending.sh", []),
    ("3860559291 55", "comment-class.sh", []),
    ("3619846594 58", "coverage-blocker.sh", []),
    ("1651026890 60", "criterion-finished.sh", []),
    ("3059909970 45", "detach-leaf.sh", []),
    ("1642735334 47", "event.sh", []),
    ("1165055683 43", "harvest-usage.sh", []),
    ("3146090332 58", "issue-worktree.sh", []),
    ("620984865 40", "leaf-model.sh", []),
    ("1964507760 39", "leaf-role.sh", []),
    ("1507644654 40", "metrics.sh", []),
    ("3513573825 54", "over-budget.sh", []),
    ("3822748993 60", "refactor-touched.sh", []),
    ("134802541 39", "run-conductor.sh", []),
    ("1042169812 59", "run-leaf.sh", []),
    ("4252593059 50", "supervise.sh", []),
    ("3650033748 63", "tick-issue-criterion.sh", []),
    ("3111273066 293", "tick-ledger.sh", []),
    ("3568418922 35", "tier-usual.sh", []),
    ("1826447128 65", "timed-test-run.sh", []),
    ("2203537502 52", "transform-touches-tests.sh", []),
    ("3750115868 145", "verify.sh", []),
    ("3132011146 48", "wait-leaf.sh", []),
    ("3345015868 167", "add-ledger-step.sh", [".tdd/issue-1.md", "after", "anchor"]),
    ("82452057 368", "build-develop-prompt.sh", ["green", "spec", "step"]),
    ("1786216893 158", "build-verify-prompt.sh", ["green"]),
    ("1786216893 158", "build-verify-prompt.sh", ["green", "spec"]),
    ("861611113 200", "build-verify-prompt.sh", ["--step"]),
    ("3146090332 58", "issue-worktree.sh", ["270"]),
    ("3146090332 58", "issue-worktree.sh", ["--remove"]),
    ("3513573825 54", "over-budget.sh", ["unit"]),
    ("3513573825 54", "over-budget.sh", ["unit", "10"]),
    ("2611868518 69", "solvable-issues.sh", ["--repo"]),
    ("1825838473 75", "supervise.sh", ["develop-red"]),
    ("1826447128 65", "timed-test-run.sh", ["all"]),
    ("1826447128 65", "timed-test-run.sh", ["all", ""]),
    ("3750115868 145", "verify.sh", ["green"]),
    ("3750115868 145", "verify.sh", ["green", "spec"]),
    ("1840331772 174", "verify.sh", ["--step"]),
]

def emitted(run_cli, script, argv):
    module = importlib.import_module("veri." + script[:-3].replace("-", "_"))
    code, out, err = run_cli(module, argv)
    return "exit %d\n%s" % (code, (out + err).rstrip("\n")) + "\n"


def test_usage_output_on_a_missing_argument_is_unchanged(run_cli):
    problems = []
    for want, script, argv in USAGE:
        text = emitted(run_cli, script, argv)
        if script == "build-develop-prompt.sh":
            usage = [l for l in text.splitlines() if "usage: " in l]
            phases = usage[0].split("usage: ")[1].split(" ")[0].split("|") if usage else []
            if not text.startswith("exit 2\n") or "dual-stub" not in phases or "beside" not in phases:
                problems.append("%s %s: usage line must name dual-stub and beside, got %r" % (script, " ".join(argv), text))
            continue
        got = cksum(text.encode("utf-8", "surrogateescape"))
        if got != want:
            args = "".join(" '%s'" % x for x in argv)
            problems.append(
                "%s %s: want %s, got %s\n"
                "  the pin covers: the line 'exit N' (here: exit 2), then the usage output with trailing newlines stripped, then one trailing newline\n"
                "  reproduce: out=$(skills/tdd/scripts/%s%s 2>&1); printf 'exit %%d\\n%%s\\n' $? \"$out\" | cksum"
                % (script, " ".join(argv), want, got, script, args))
    assert problems == []
