"""Emitted-text pins: every script's usage text on a missing argument, and each prompt builder's output for fixed inputs, byte-identical by `cksum`.

Each case's subject is text the scripts emit, driven in-process through each script's module.
"""
import importlib
import os

import event
from conftest import SCRIPTS


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
    ("787667760 308", "build-develop-prompt.sh", []),
    ("217537457 94", "build-verify-prompt.sh", []),
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
    ("2629435625 115", "tick-ledger.sh", []),
    ("3568418922 35", "tier-usual.sh", []),
    ("1826447128 65", "timed-test-run.sh", []),
    ("2203537502 52", "transform-touches-tests.sh", []),
    ("3019634167 120", "verify.sh", []),
    ("3132011146 48", "wait-leaf.sh", []),
    ("3345015868 167", "add-ledger-step.sh", [".tdd/issue-1.md", "after", "anchor"]),
    ("2658457917 361", "build-develop-prompt.sh", ["green", "spec", "step"]),
    ("217537457 94", "build-verify-prompt.sh", ["green"]),
    ("217537457 94", "build-verify-prompt.sh", ["green", "spec"]),
    ("2618584748 136", "build-verify-prompt.sh", ["--step"]),
    ("3146090332 58", "issue-worktree.sh", ["270"]),
    ("3146090332 58", "issue-worktree.sh", ["--remove"]),
    ("3513573825 54", "over-budget.sh", ["unit"]),
    ("3513573825 54", "over-budget.sh", ["unit", "10"]),
    ("2611868518 69", "solvable-issues.sh", ["--repo"]),
    ("1825838473 75", "supervise.sh", ["develop-red"]),
    ("1826447128 65", "timed-test-run.sh", ["all"]),
    ("1826447128 65", "timed-test-run.sh", ["all", ""]),
    ("3019634167 120", "verify.sh", ["green"]),
    ("3019634167 120", "verify.sh", ["green", "spec"]),
    ("3584306278 149", "verify.sh", ["--step"]),
]

# Arguments name a fixture file as {spec}, {bug}, {refactor}, {ledger} or {reason}; {step} and {cmd} are fixed text.
PROMPTS = [
    ("1402995898 7552", "build-verify-prompt.sh", ["red", "{spec}", "t/x.test.sh", "case one"]),
    ("3981310562 8411", "build-verify-prompt.sh", ["red", "{bug}", "t/x.test.sh", "case one"]),
    ("3878499230 7729", "build-verify-prompt.sh", ["--step", "{step}", "red", "{spec}", "t/x.test.sh", "case one"]),
    ("186147977 8474", "build-verify-prompt.sh", ["--fast-cmd", "make unit", "green", "{spec}", "t/x.test.sh", "case one"]),
    ("213977504 8687", "build-verify-prompt.sh", ["--fast-cmd", "make unit", "refactor", "{spec}", "t/x.test.sh", "0123456"]),
    ("3583632872 7430", "build-verify-prompt.sh", ["pin", "{spec}", "t/x.test.sh", "case one"]),
    ("4061570679 14313", "build-verify-prompt.sh", ["plan", "{spec}", "{ledger}"]),
    ("929269162 15534", "build-verify-prompt.sh", ["plan", "{refactor}", "{ledger}"]),
    ("4209106995 5484", "build-verify-prompt.sh", ["rebase", "{spec}", "0123456", "89abcde"]),
    ("876453882 5291", "build-verify-prompt.sh", ["transform", "{spec}", "{reason}", "0123456"]),
]


FIXTURES = {
    "spec": "## What to build\n\nA fixed spec for pinning prompts, with an & and a \\ in it.\n\n## Acceptance criteria\n\n- [ ] one criterion\n",
    "bug": "## Bug\n\nIt breaks.\n\n## Acceptance criteria\n\n- [ ] it no longer breaks\n",
    "refactor": "## Refactor\n\nMove a function.\n",
    "ledger": "# Plan for #1 — fixed\n\n- [ ] one criterion ⟦criterion 1⟧\n",
    "reason": "the test pins nothing\n",
}


def emitted(run_cli, script, argv, stream):
    module = importlib.import_module("veri." + script[:-3].replace("-", "_"))
    code, out, err = run_cli(module, argv)
    text = out + err if stream == "usage" else out
    return "exit %d\n%s" % (code, text.rstrip("\n")) + "\n"


def test_usage_output_on_a_missing_argument_and_prompt_output_for_fixed_inputs_are_unchanged(run_cli, tmp_path):
    for name, text in FIXTURES.items():
        (tmp_path / (name + ".md")).write_text(text, encoding="utf-8")
    names = {name: str(tmp_path / (name + ".md")) for name in FIXTURES}
    names.update(step="the step", cmd="make test")
    problems = []
    for stream, table in (("usage", USAGE), ("prompt", PROMPTS)):
        for want, script, argv in table:
            argv = [a.format(**names) if stream == "prompt" else a for a in argv]
            text = emitted(run_cli, script, argv, stream)
            text = text.replace(str(SCRIPTS), "<scripts>").replace(str(tmp_path), "<work>")
            text = text.replace((event.toplevel() or os.getcwd()) + "/.tdd/", "<root>/.tdd/")
            got = cksum(text.encode("utf-8", "surrogateescape"))
            if got != want:
                problems.append("%s %s: want %s, got %s" % (script, " ".join(argv), want, got))
    assert problems == []
