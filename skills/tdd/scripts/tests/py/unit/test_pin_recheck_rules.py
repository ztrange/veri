"""Table cases for pin_recheck's two pure rules: the retire-pin declarations a diff carries, and how one pin sorts
(skip / retire / replay) from the files the range deleted and the declarations. One case per row."""
import pytest

from veri import pin_recheck
from veri.pin_recheck import Kind

L = ".tdd/issue-1-mutations.md"
CMD = "make test TESTS=tests/t.py"


def added(*lines):
    return "\n".join(["diff --git a/x b/x", "@@ -0,0 +1 @@", *lines]) + "\n"


@pytest.mark.parametrize("diff, declared, refusal", [
    ("", {}, None),
    (added("+retire-pin: a.md f.py -- gone for good"), {("a.md", "f.py"): "gone for good"}, None),
    (added("+  retire-pin: a.md f.py --  padded  "), {("a.md", "f.py"): "padded"}, None),
    (added("+retire-pin: a.md f.py -- one", "+retire-pin: a.md f.py -- two"), {("a.md", "f.py"): "two"}, None),
    (added("+retire-pin: a.md f.py -- x", "+retire-pin: b.md g.py -- y"),
     {("a.md", "f.py"): "x", ("b.md", "g.py"): "y"}, None),
    (added("-retire-pin: a.md f.py -- removed line"), {}, None),
    (added(" retire-pin: a.md f.py -- context line"), {}, None),
    (added("+retire-pin: a.md f.py"), {}, None),
    (added("+retire-pin: a.md f.py --"), {}, "retire-pin for a.md f.py has an empty reason"),
    (added("+retire-pin: a.md f.py --   "), {}, "retire-pin for a.md f.py has an empty reason"),
    (added("+retire-pin: a.md f.py -- ok", "+retire-pin: b.md g.py --", "+retire-pin: c.md h.py --"),
     {}, "retire-pin for b.md g.py has an empty reason"),
])
def test_declared_retirements_reads_plus_lines_and_refuses_the_first_empty_reason(diff, declared, refusal):
    assert pin_recheck.declared_retirements(diff) == (declared, refusal)


def mutation(**over):
    return {"file": "src/f.py", "old": "a", "new": "b", "command": CMD, **over}


def before(**over):
    return {"before": "abc", "keep": "tests/t.py", "command": CMD, **over}


def outcome(kind, named=(), gone=(), reason="", command=None):
    return pin_recheck.Outcome(kind, tuple(named), tuple(gone), reason, command)


@pytest.mark.parametrize("pin, deleted, declared, expected", [
    # already retired: skipped whatever else is true
    (mutation(retired="why"), set(), {(L, "src/f.py"): "r"}, outcome(Kind.SKIP)),
    # a declaration for (ledger, mutated file) retires with its reason, ahead of the deletion rules
    (mutation(), set(), {(L, "src/f.py"): "r"}, outcome(Kind.RETIRE_DECLARED, reason="r")),
    (mutation(), {"tests/t.py"}, {(L, "src/f.py"): "r"}, outcome(Kind.RETIRE_DECLARED, reason="r")),
    # a declaration for another ledger or file does not apply
    (mutation(), set(), {("other.md", "src/f.py"): "r"}, outcome(Kind.REPLAY_MUTATION, ["tests/t.py"], command=CMD)),
    (mutation(), set(), {(L, "other.py"): "r"}, outcome(Kind.REPLAY_MUTATION, ["tests/t.py"], command=CMD)),
    # a before-pin is keyed by its keep file
    (before(), set(), {(L, "tests/t.py"): "r"}, outcome(Kind.RETIRE_DECLARED, reason="r")),
    # every named test file deleted: retired by deletion, one line per name
    (mutation(), {"tests/t.py"}, {}, outcome(Kind.RETIRE_TESTS_GONE, gone=["tests/t.py"], command=CMD)),
    (mutation(command="make test TESTS=a.py TESTS=b.py"), {"a.py", "b.py"}, {},
     outcome(Kind.RETIRE_TESTS_GONE, gone=["a.py", "b.py"], command="make test TESTS=a.py TESTS=b.py")),
    (mutation(command="make test TESTS=a.py::case"), {"a.py"}, {},
     outcome(Kind.RETIRE_TESTS_GONE, gone=["a.py::case"], command="make test TESTS=a.py::case")),
    (mutation(command='make test TESTS="a.py"'), {"a.py"}, {},
     outcome(Kind.RETIRE_TESTS_GONE, gone=["a.py"], command='make test TESTS="a.py"')),
    # some named tests deleted: they drop out of the command, the rest are replayed
    (mutation(command="make test TESTS=a.py TESTS=b.py"), {"a.py"}, {},
     outcome(Kind.REPLAY_MUTATION, ["b.py"], ["a.py"], command="make test  TESTS=b.py")),
    (before(command="make test TESTS=a.py TESTS=b.py"), {"b.py"}, {},
     outcome(Kind.REPLAY_BEFORE, ["a.py"], ["b.py"], command="make test TESTS=a.py ")),
    (mutation(command="make test TESTS='a.py' TESTS=b.py"), {"a.py"}, {},
     outcome(Kind.REPLAY_MUTATION, ["b.py"], ["a.py"], command="make test  TESTS=b.py")),
    # no TESTS= in the command: nothing is named, so no test deletion applies
    (mutation(command="python3 -m pytest -q t.py"), {"t.py"}, {},
     outcome(Kind.REPLAY_MUTATION, command="python3 -m pytest -q t.py")),
    # a before-pin replays its before-state; a mutation pin whose mutated file was deleted retires
    (before(), set(), {}, outcome(Kind.REPLAY_BEFORE, ["tests/t.py"], command=CMD)),
    (mutation(), {"src/f.py"}, {}, outcome(Kind.RETIRE_FILE_DELETED, ["tests/t.py"], command=CMD)),
    (mutation(), set(), {}, outcome(Kind.REPLAY_MUTATION, ["tests/t.py"], command=CMD)),
    # a before-pin never takes the file-deleted rule, even when its mutated file is deleted
    (before(command="make test TESTS=x.py", file="src/f.py"), {"src/f.py"}, {},
     outcome(Kind.REPLAY_BEFORE, ["x.py"], command="make test TESTS=x.py")),
])
def test_classify_sorts_one_pin_from_what_the_range_deleted_and_declared(pin, deleted, declared, expected):
    assert pin_recheck.classify(L, pin, deleted, declared) == expected
