"""In-process cases for veri/add_ledger_step.py, the module add-ledger-step.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

USAGE = (
    "usage: add-ledger-step.sh <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]\n"
)

LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] a one ⟦criterion 1⟧\n"
    "- [ ] b two ⟦criterion 2⟧\n"
    "- [ ] c three ⟦criterion 3⟧\n"
).encode()


@pytest.fixture
def add_ledger_step():
    return importlib.import_module("veri.add_ledger_step")


def test_main_refuses_bad_arguments_with_exit_2_and_inserts_after_the_anchor(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    for argv in ([], ["l.md", "after", "anchor"], ["l.md", "after", "", "t"]):
        code = add_ledger_step.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)

    code = add_ledger_step.main([str(ledger), "sideways", "b two", "t"])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (
        2, "", "add-ledger-step.sh: position must be after, before or instead-of: sideways\n"
    )
    assert ledger.read_bytes() == LEDGER

    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    captured = capsys.readouterr()
    assert code == 0
    assert ledger.read_bytes().decode().split("\n")[3:5] == [
        "- [ ] b two ⟦criterion 2⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 2⟧",
    ]


COUNTED_FIXTURES = (
    ("- [x] lowercase the slug ⟦criterion 1⟧", 0),
    ("- [ ] collapse to single hyphen ⟦criterion 2⟧", 0),
    ("- [ ] strip edge hyphens ⟦criterion 3⟧", 0),
    ("- [ ] collapse a unicode dash too ⟦added⟧ ⟦criterion 2⟧", 1),
    ("- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧", 1),
    ("- [ ] collapse to single hyphen", 0),
    ("- [ ] collapse a unicode dash too ⟦added⟧", 1),
    ("- [ ] collapse an ASCII hyphen run ⟦added⟧ ⟦criterion 2⟧", 1),
    ("- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧", 1),
    ("- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 1⟧", 0),
    ("- [ ] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧", 0),
    ("- [x] fix the full-suite failure: x.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧", 0),
    ("- [x] say a step marked ⟦added⟧ is counted ⟦criterion 1⟧", 0),
    ("- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending", 1),
    ("- [ ] an extra edge case ⟦added⟧ ⟦criterion 2⟧", 1),
    ("- [x] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending", 0),
    ("- [ ] port status case a ⟦replaces-case⟧ ⟦criterion 1⟧", 0),
    ("- [ ] port status case c ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧", 1),
    ("- [ ] a lamp glows ⟦criterion 2⟧", 0),
)


def test_main_counts_against_a_budget_of_one_exactly_the_fixture_lines_lib_ledger_counts_as_added(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "1")
    ledger = tmp_path / "issue-42.md"
    got = {}
    for line, _ in COUNTED_FIXTURES:
        ledger.write_bytes(f"# Plan for #42\n\n{line}\n- [ ] the probe anchor ⟦criterion 9⟧\n".encode())
        got[line] = add_ledger_step.main([str(ledger), "after", "the probe anchor", "a probe step"])
        capsys.readouterr()
    assert got == dict(COUNTED_FIXTURES)


def test_main_inserts_beside_the_one_dash_step_holding_the_anchor_leaving_prose_and_star_lines_alone(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(
        "# Plan for #42\n"
        "\n"
        "a lamp glows in this prose line\n"
        "* [ ] a lamp glows\n"
        "- [ ] a lamp glows ⟦criterion 2⟧\n".encode()
    )
    code = add_ledger_step.main([str(ledger), "after", "a lamp glows", "a lamp dims"])
    captured = capsys.readouterr()
    assert (code, captured.err) == (0, "")
    assert ledger.read_bytes().decode() == (
        "# Plan for #42\n"
        "\n"
        "a lamp glows in this prose line\n"
        "* [ ] a lamp glows\n"
        "- [ ] a lamp glows ⟦criterion 2⟧\n"
        "- [ ] a lamp dims ⟦added⟧ ⟦criterion 2⟧\n"
    )


def test_main_inserts_the_line_veri_ledger_new_step_returns_for_the_text_and_the_anchor_criterion(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes("# Plan for #42\n\n- [ ] a lamp glows ⟦criterion 2⟧\n".encode())
    code = add_ledger_step.main([str(ledger), "after", "a lamp glows", "a lamp dims"])
    capsys.readouterr()
    assert code == 0
    assert ledger.read_bytes().split(b"\n")[3] == importlib.import_module("veri.ledger").new_step("a lamp dims", "2").encode()


def test_main_puts_the_texts_above_below_or_in_place_of_the_anchor_and_gives_none_a_criterion_the_anchor_lacks(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    head = "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
    anchor = "- [ ] b two ⟦criterion 2⟧\n"
    added = "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n- [ ] u ⟦added⟧ ⟦criterion 2⟧\n"
    tail = "- [ ] c three ⟦criterion 3⟧\n"
    got = {}
    for where in ("before", "after", "instead-of"):
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main([str(ledger), where, "b two", "t", "u"])
        got[where] = (code, capsys.readouterr().err, ledger.read_bytes().decode())
    assert got == {
        "before": (0, "", head + added + anchor + tail),
        "after": (0, "", head + anchor + added + tail),
        "instead-of": (0, "", head + added + tail),
    }

    ledger.write_bytes("# Plan for #42\n\n- [ ] b two\n".encode())
    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    assert (code, ledger.read_bytes().decode()) == (0, "# Plan for #42\n\n- [ ] b two\n- [ ] t ⟦added⟧\n")


def test_main_inherits_the_last_criterion_unvalidated_and_writes_empty_multiline_and_indented_inserts_verbatim(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    head = "# Plan for #42\n\n"
    cases = {
        "unvalidated": ("- [ ] b two ⟦criterion abc⟧\n", "t"),
        "last tag": ("- [ ] b two ⟦criterion 1⟧ ⟦criterion 2⟧ x\n", "t"),
        "empty text": ("- [ ] b two ⟦criterion 2⟧\n", ""),
        "newline": ("- [ ] b two ⟦criterion 2⟧\n", "x\ny"),
        "indented": ("  - [ ] b two ⟦criterion 4⟧\n", "t"),
    }
    got = {}
    for name, (anchor, text) in cases.items():
        ledger.write_bytes((head + anchor).encode())
        code = add_ledger_step.main([str(ledger), "after", "b two", text])
        got[name] = (code, capsys.readouterr().err, ledger.read_bytes().decode())
    assert got == {
        "unvalidated": (0, "", head + "- [ ] b two ⟦criterion abc⟧\n- [ ] t ⟦added⟧ ⟦criterion abc⟧\n"),
        "last tag": (0, "", head + "- [ ] b two ⟦criterion 1⟧ ⟦criterion 2⟧ x\n- [ ] t ⟦added⟧ ⟦criterion 2⟧\n"),
        "empty text": (0, "", head + "- [ ] b two ⟦criterion 2⟧\n- [ ]  ⟦added⟧ ⟦criterion 2⟧\n"),
        "newline": (0, "", head + "- [ ] b two ⟦criterion 2⟧\n- [ ] x\ny ⟦added⟧ ⟦criterion 2⟧\n"),
        "indented": (0, "", head + "  - [ ] b two ⟦criterion 4⟧\n- [ ] t ⟦added⟧ ⟦criterion 4⟧\n"),
    }


def test_main_over_budget_returns_1_silently_and_owes_every_text_under_the_last_owed_steps_heading(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    text = LEDGER.decode()
    notes = text + "\n## Owed steps\n\n- old\n\n## Notes\n\na remark\n"
    unterminated = text + "\n## Owed steps\n\n- old"
    unseen_heading = text + "\n## Owed steps"
    got = {}
    for name, seed, batches in (
        ("fresh then again", text, (["t", "fix x.test.sh ⟦suite-repair⟧"], ["u"])),
        ("notes after owed", notes, (["t"],)),
        ("unterminated last line", unterminated, (["t"],)),
        ("unterminated owed heading", unseen_heading, (["t"],)),
    ):
        ledger.write_bytes(seed.encode())
        runs = []
        for texts in batches:
            code = add_ledger_step.main([str(ledger), "after", "b two", *texts])
            captured = capsys.readouterr()
            runs.append((code, captured.out, captured.err))
        got[name] = (runs, ledger.read_bytes().decode())
    assert got == {
        "fresh then again": (
            [(1, "", ""), (1, "", "")],
            text + "\n## Owed steps\n\n- t\n- fix x.test.sh ⟦suite-repair⟧\n- u\n",
        ),
        "notes after owed": ([(1, "", "")], notes + "\n## Owed steps\n\n- t\n"),
        "unterminated last line": ([(1, "", "")], unterminated + "- t\n"),
        "unterminated owed heading": ([(1, "", "")], unseen_heading + "\n## Owed steps\n\n- t\n"),
    }


def test_main_refuses_position_then_anchor_then_budget_each_with_2_and_unset_allows_a_fifth_added_step(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"

    def run(*argv):
        code = add_ledger_step.main([str(ledger), *argv])
        captured = capsys.readouterr()
        return (code, captured.out, captured.err, ledger.read_bytes() if ledger.exists() else None)

    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    assert run("afterr", "b two", "t") == (
        2, "", "add-ledger-step.sh: position must be after, before or instead-of: afterr\n", None
    )

    ledger.write_bytes(LEDGER)
    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    anchors = ("nothing", "⟦criterion", "*", "t[w]o")
    assert {anchor: run("after", anchor, "t") for anchor in anchors} == {
        anchor: (2, "", f"add-ledger-step.sh: anchor matches no single step: {anchor}\n", LEDGER)
        for anchor in anchors
    }

    budgets = ("", "x", "-1", "1.5")
    got = {}
    for budget in budgets:
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        got[budget] = run("after", "b two", "t")
    assert got == {
        budget: (2, "", f"add-ledger-step.sh: VERI_STEP_GROWTH must be a whole number >= 0: {budget}\n", LEDGER)
        for budget in budgets
    }

    monkeypatch.setenv("VERI_STEP_GROWTH", "x")
    assert run("after", "nothing", "t") == (
        2, "", "add-ledger-step.sh: anchor matches no single step: nothing\n", LEDGER
    )

    monkeypatch.delenv("VERI_STEP_GROWTH")
    four = "".join(f"- [ ] extra {n} ⟦added⟧ ⟦criterion 2⟧\n" for n in range(4))
    seed = (LEDGER.decode() + four).encode()
    ledger.write_bytes(seed)
    fifth = run("after", "c three", "fifth")
    sixth = run("after", "c three", "sixth")
    assert (fifth[:3], sixth[:3]) == ((0, "", ""), (1, "", ""))
    assert b"- [ ] fifth \xe2\x9f\xa6added\xe2\x9f\xa7" in fifth[3]
    assert b"- [ ] sixth" not in sixth[3]


def test_main_counts_only_steps_ending_in_added_and_inserts_repair_texts_unmarked_and_uncounted(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    uncounted = (
        "# Plan for #42\n"
        "\n"
        "Steps the run grew carry ⟦added⟧\n"
        "- [x] say a step marked ⟦added⟧ is counted ⟦criterion 1⟧\n"
        "- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n"
        "- [x] fix the full-suite failure: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧ ⟂ refactor pending\n"
        "- [ ] port status case a ⟦replaces-case⟧ ⟦criterion 1⟧\n"
        "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
        "\n"
        "## Owed steps\n"
        "\n"
        "- an earlier edge case ⟦added⟧\n"
    )
    counted = (
        "# Plan for #42\n"
        "\n"
        "- [x] an extra edge case ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    )
    unadded = (
        "# Plan for #42\n"
        "\n"
        "- [x] an extra edge case ⟦criterion 1⟧\n"
        "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    )
    got = {}
    for name, seed, budget, texts in (
        ("uncounted lines, one added text", uncounted, "1",
         ["one more edge case", "fix the full-suite failure: z.test.sh ⟦suite-repair⟧"]),
        ("a pending added step spends the budget", counted, "1", ["one more edge case"]),
        ("repair texts at a budget of 0", unadded, "0",
         ["fix the CI failure: x.test.sh ⟦ci-repair⟧", "⟦suite-repair⟧ mid-text: y.test.sh"]),
    ):
        ledger.write_bytes(seed.encode())
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        code = add_ledger_step.main([str(ledger), "after", "collapse to single hyphen", *texts])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err, ledger.read_bytes().decode())
    anchor = "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    repairs = (
        "- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n"
        "- [ ] ⟦suite-repair⟧ mid-text: y.test.sh ⟦criterion 2⟧\n"
    )
    assert got == {
        "uncounted lines, one added text": (0, "", "", uncounted.replace(
            anchor,
            anchor
            + "- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧\n"
            + "- [ ] fix the full-suite failure: z.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧\n",
        )),
        "a pending added step spends the budget": (1, "", "", counted + "\n## Owed steps\n\n- one more edge case\n"),
        "repair texts at a budget of 0": (0, "", "", unadded + repairs),
    }
    records = importlib.import_module("veri.ledger").ledger_steps(ledger.read_bytes().decode())[-2:]
    assert [(state, kind, text) for _, state, kind, _, _, _, text in records] == [
        ("open", "step", "fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧"),
        ("open", "step", "⟦suite-repair⟧ mid-text: y.test.sh ⟦criterion 2⟧"),
    ]
