"""In-process cases for veri/add_ledger_step.py, the module add-ledger-step.sh is a shim over."""
import importlib
import json

import pytest

from conftest import SCRIPTS

USAGE = (
    "usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]  (--planned goes with --criterion <k>)\n"
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

    monkeypatch.setenv("VERI_STEP_GROWTH", "1")
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main([str(ledger), "instead-of", "c three", "t", "u"])
    assert (code, ledger.read_bytes()) == (1, LEDGER + "\n## Owed steps\n\n- t\n- u\n".encode())
    monkeypatch.delenv("VERI_STEP_GROWTH")

    ledger.write_bytes("# Plan for #42\n\n- [ ] b two\n".encode())
    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    assert (code, ledger.read_bytes().decode()) == (0, "# Plan for #42\n\n- [ ] b two\n- [ ] t ⟦added⟧\n")


def test_main_inherits_the_last_criterion_unvalidated_and_writes_empty_multiline_and_indented_inserts_verbatim(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    head = "# Plan for #42\n\n"
    cases = {
        "unvalidated": ("- [ ] b two ⟦criterion abc⟧\n", "t"),
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
        "unterminated last line": ([(1, "", "")], unterminated + "\n- t\n"),
        "unterminated owed heading": ([(1, "", "")], unseen_heading + "\n- t\n"),
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
    assert sixth[3] == fifth[3] + "\n## Owed steps\n\n- sixth\n".encode()


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
         ["one more edge case", "fix the CI failure: z.test.sh ⟦ci-repair⟧"]),
        ("a pending added step spends the budget", counted, "1", ["one more edge case"]),
        ("repair texts at a budget of 0", unadded, "0",
         ["fix the CI failure: x.test.sh ⟦ci-repair⟧", "mid-text: y.test.sh ⟦suite-repair⟧"]),
    ):
        ledger.write_bytes(seed.encode())
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        code = add_ledger_step.main([str(ledger), "after", "collapse to single hyphen", *texts])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err, ledger.read_bytes().decode())
    anchor = "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    repairs = (
        "- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n"
        "- [ ] mid-text: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧\n"
    )
    assert got == {
        "uncounted lines, one added text": (0, "", "", uncounted.replace(
            anchor,
            anchor
            + "- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧\n"
            + "- [ ] fix the CI failure: z.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n",
        )),
        "a pending added step spends the budget": (1, "", "", counted + "\n## Owed steps\n\n- one more edge case\n"),
        "repair texts at a budget of 0": (0, "", "", unadded + repairs),
    }
    records = importlib.import_module("veri.ledger").ledger_steps(ledger.read_bytes().decode())[-2:]
    assert [(state, kind, text) for _, state, kind, _, _, _, text in records] == [
        ("open", "step", "fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧"),
        ("open", "step", "mid-text: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧"),
    ]


def test_main_reads_veri_step_growth_as_bash_arithmetic_octal_base_errors_and_64_bit_wraps(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    text = LEDGER.decode()
    extras = lambda n: "".join(f"- [ ] extra {i} ⟦added⟧ ⟦criterion 2⟧\n" for i in range(n))
    ten = [f"t{i}" for i in range(10)]
    got = {}
    for name, budget, seed, texts in (
        ("010, eighth added step", "010", text + extras(7), ["t"]),
        ("010, ninth added step", "010", text + extras(8), ["t"]),
        ("08", "08", text, ten),
        ("09", "09", text, ten),
        ("2^64", "18446744073709551616", text, ["t"]),
        ("2^65", "36893488147419103232", text, ["t"]),
        ("2^63", "9223372036854775808", text, ["t"]),
    ):
        ledger.write_bytes(seed.encode())
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        code = add_ledger_step.main([str(ledger), "after", "c three", *texts])
        captured = capsys.readouterr()
        lines = captured.err.splitlines()
        named = len(lines) == 1 and f"{budget}: value too great for base" in lines[0]
        got[name] = (code, captured.out, captured.err if not named else "named", ledger.read_bytes().decode())
    inserted = lambda seed, texts: seed.replace(
        "- [ ] c three ⟦criterion 3⟧\n",
        "- [ ] c three ⟦criterion 3⟧\n" + "".join(f"- [ ] {t} ⟦added⟧ ⟦criterion 3⟧\n" for t in texts),
    )
    owed = text + "\n## Owed steps\n\n- t\n"
    assert got == {
        "010, eighth added step": (0, "", "", inserted(text + extras(7), ["t"])),
        "010, ninth added step": (1, "", "", text + extras(8) + "\n## Owed steps\n\n- t\n"),
        "08": (0, "", "named", inserted(text, ten)),
        "09": (0, "", "named", inserted(text, ten)),
        "2^64": (1, "", "", owed),
        "2^65": (1, "", "", owed),
        "2^63": (1, "", "", owed),
    }


def test_main_reads_and_rewrites_the_ledger_as_bytes_line_by_line_in_place(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    unterminated = LEDGER.removesuffix("- [ ] c three ⟦criterion 3⟧\n".encode()).removesuffix(b"\n")
    crlf = LEDGER.replace(b"\n", b"\r\n")
    latin = LEDGER.replace(b"# Plan for #42", b"# Plan for #42 \xff")
    got = {}
    for name, seed, anchor in (
        ("anchor on an unterminated last line", unterminated, "b two"),
        ("insert before an unterminated last line", unterminated, "a one"),
        ("crlf", crlf, "a one"),
        ("non-utf-8", latin, "a one"),
    ):
        ledger.write_bytes(seed)
        code = add_ledger_step.main([str(ledger), "after", anchor, "t"])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err, ledger.read_bytes())
    step = "- [ ] t ⟦added⟧ ⟦criterion 1⟧\n".encode()
    assert got == {
        "anchor on an unterminated last line": (
            0, "", "", unterminated + b"\n" + "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n".encode()
        ),
        "insert before an unterminated last line": (
            0, "", "", unterminated.replace(
                "a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step
            ) + b"\n",
        ),
        "crlf": (
            0, "", "", crlf.replace("a one ⟦criterion 1⟧\r\n".encode(), "a one ⟦criterion 1⟧\r\n".encode() + step)
        ),
        "non-utf-8": (
            0, "", "", latin.replace("a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step)
        ),
    }


def test_main_writes_a_non_utf_8_byte_of_a_text_back_unchanged_when_it_inserts_and_when_it_owes(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    text = b"t \xff".decode(errors="surrogateescape")
    got = {}
    for name, budget in (("inserted", "3"), ("owed", "0")):
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main([str(ledger), "after", "b two", text])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err, ledger.read_bytes())
    assert got == {
        "inserted": (
            0, "", "", LEDGER.replace(
                "b two ⟦criterion 2⟧\n".encode(),
                "b two ⟦criterion 2⟧\n- [ ] t ".encode() + b"\xff" + " ⟦added⟧ ⟦criterion 2⟧\n".encode(),
            ),
        ),
        "owed": (1, "", "", LEDGER + b"\n## Owed steps\n\n- t \xff\n"),
    }


def test_main_returns_2_naming_the_anchor_for_a_missing_or_directory_ledger_and_raises_on_a_failed_write(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    missing = tmp_path / "nofile.md"
    directory = tmp_path / "dir.md"
    directory.mkdir()
    got = {}
    for name, path in (("missing", missing), ("directory", directory)):
        code = add_ledger_step.main([str(path), "after", "b two", "t"])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err.splitlines()[-1:], sorted(p.name for p in tmp_path.iterdir()))
    assert got == {
        name: (2, "", ["add-ledger-step.sh: anchor matches no single step: b two"], ["dir.md"])
        for name in ("missing", "directory")
    }

    ledger = tmp_path / "issue-42.md"
    real_open = open

    def unwritable(file, mode="r", *args, **kwargs):
        if str(file) == str(ledger) and any(c in mode for c in "wa"):
            raise PermissionError(13, "Permission denied", str(file))
        return real_open(file, mode, *args, **kwargs)

    for budget in ("3", "0"):
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        ledger.write_bytes(LEDGER)
        monkeypatch.setattr("builtins.open", unwritable)
        with pytest.raises(PermissionError):
            add_ledger_step.main([str(ledger), "after", "b two", "t"])
        monkeypatch.setattr("builtins.open", real_open)
        assert ledger.read_bytes() == LEDGER


def test_main_leaves_the_ledger_byte_identical_and_no_temporary_file_beside_it_when_the_swap_fails_inserting_or_owing(tmp_path, monkeypatch, add_ledger_step):
    ledger = tmp_path / "issue-42.md"

    def refuse_swap(src, dst):
        raise OSError(28, "No space left on device")

    for budget in ("3", "0"):
        monkeypatch.setenv("VERI_STEP_GROWTH", budget)
        ledger.write_bytes(LEDGER)
        monkeypatch.setattr("os.replace", refuse_swap)
        with pytest.raises(OSError):
            add_ledger_step.main([str(ledger), "after", "b two", "t"])
        monkeypatch.undo()
        assert (ledger.read_bytes(), sorted(p.name for p in tmp_path.iterdir())) == (LEDGER, ["issue-42.md"])


def test_main_finds_a_last_step_without_a_trailing_newline_as_the_anchor_and_keeps_it_after_inserting_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER.removesuffix(b"\n"))

    code = add_ledger_step.main([str(ledger), "after", "c three", "t"])
    captured = capsys.readouterr()

    assert (code, captured.err) == (0, "")
    assert ledger.read_bytes().decode().split("\n")[4:6] == [
        "- [ ] c three ⟦criterion 3⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 3⟧",
    ]


def test_main_keeps_a_last_line_without_a_trailing_newline_after_inserting_beside_an_earlier_step_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER.removesuffix(b"\n"))

    code = add_ledger_step.main([str(ledger), "after", "a one", "t"])
    captured = capsys.readouterr()

    assert (code, captured.err) == (0, "")
    assert ledger.read_bytes().decode().split("\n")[2:6] == [
        "- [x] a one ⟦criterion 1⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 1⟧",
        "- [ ] b two ⟦criterion 2⟧",
        "- [ ] c three ⟦criterion 3⟧",
    ]


def test_main_counts_a_last_added_step_without_a_trailing_newline_against_the_budget_and_owes_the_batch_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "1")
    ledger = tmp_path / "issue-42.md"
    seed = LEDGER.decode().removesuffix(" ⟦criterion 3⟧\n") + " ⟦added⟧ ⟦criterion 3⟧"
    ledger.write_bytes(seed.encode())

    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    captured = capsys.readouterr()

    after = ledger.read_bytes().decode()
    assert (code, captured.out, captured.err) == (1, "", "")
    assert "- [ ] t" not in after
    assert after.endswith("## Owed steps\n\n- t\n")


def test_main_starts_the_owed_steps_heading_on_its_own_line_after_a_last_line_without_a_trailing_newline_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    seed = LEDGER.removesuffix(b"\n")
    ledger.write_bytes(seed)

    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    captured = capsys.readouterr()

    after = ledger.read_bytes()
    lines = after.decode().split("\n")
    assert (code, captured.out, captured.err) == (1, "", "")
    assert after.startswith(seed + b"\n")
    assert "- [ ] c three ⟦criterion 3⟧" in lines
    assert "## Owed steps" in lines
    assert after.endswith(b"## Owed steps\n\n- t\n")


def test_main_owes_each_bullet_on_its_own_line_after_an_unterminated_last_owed_bullet_1109(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    seed = LEDGER + b"\n## Owed steps\n\n- old"
    ledger.write_bytes(seed)

    code = add_ledger_step.main([str(ledger), "after", "b two", "t", "u"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (1, "", "")
    assert ledger.read_bytes() == seed + b"\n- t\n- u\n"


def test_main_owes_each_bullet_under_an_unterminated_last_owed_steps_heading_without_a_second_heading_1109(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    seed = LEDGER + b"\n## Owed steps"
    ledger.write_bytes(seed)

    code = add_ledger_step.main([str(ledger), "after", "b two", "t", "u"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (1, "", "")
    after = ledger.read_bytes()
    assert after.startswith(seed + b"\n")
    lines = after.decode().split("\n")
    assert lines.count("## Owed steps") == 1
    assert lines[-3:] == ["- t", "- u", ""]


def test_main_refuses_a_ledger_whose_step_carries_two_criterion_tags_naming_the_step_and_writing_nothing_1116(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    seeds = {
        "the anchor": (
            "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
            "- [ ] reject an empty title ⟦criterion 1⟧ ⟦criterion 2⟧\n"
        ).encode(),
        "another step": (
            "# Plan for #42\n\n- [x] reject an empty title ⟦criterion 1⟧ ⟦criterion 2⟧\n"
            "- [ ] b two ⟦criterion 2⟧\n"
        ).encode(),
    }
    anchors = {"the anchor": "reject an empty title", "another step": "b two"}
    got = {}
    for name, seed in seeds.items():
        ledger.write_bytes(seed)
        code = add_ledger_step.main([str(ledger), "after", anchors[name], "t"])
        out, err = capsys.readouterr()
        lines = err.splitlines()
        got[name] = (
            code,
            out,
            len(lines),
            bool(lines) and "reject an empty title" in lines[0],
            bool(lines) and "one step serves one criterion" in lines[0].lower(),
            ledger.read_bytes() == seed,
        )
    assert got == {name: (2, "", 1, True, True, True) for name in seeds}


def test_main_given_criterion_k_tags_every_inserted_line_with_k_whatever_the_anchor_carries_1224(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--criterion", "3", str(ledger), "after", "b two", "t", "u"])
    assert (code, capsys.readouterr().err, ledger.read_bytes().decode()) == (
        0,
        "",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦added⟧ ⟦criterion 3⟧\n- [ ] u ⟦added⟧ ⟦criterion 3⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_without_criterion_tags_inserted_lines_with_the_anchor_criterion_and_an_untagged_anchor_yields_untagged_lines_1224(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    got = {}
    for name, seed in (("tagged", LEDGER), ("untagged", "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n".encode())):
        ledger.write_bytes(seed)
        code = add_ledger_step.main([str(ledger), "after", "b two", "t", "u"])
        got[name] = (code, capsys.readouterr().err, ledger.read_bytes().decode())
    assert got == {
        "tagged": (
            0,
            "",
            "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
            "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n- [ ] u ⟦added⟧ ⟦criterion 2⟧\n- [ ] c three ⟦criterion 3⟧\n",
        ),
        "untagged": (
            0,
            "",
            "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n- [ ] t ⟦added⟧\n- [ ] u ⟦added⟧\n",
        ),
    }


def test_main_given_a_criterion_no_step_carries_tags_every_inserted_line_with_it_and_returns_0_1292(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, capsys.readouterr().err, ledger.read_bytes().decode()) == (
        0,
        "",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦added⟧ ⟦criterion 7⟧\n- [ ] u ⟦added⟧ ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_refuses_a_criterion_that_is_not_a_whole_number_of_at_least_1_with_2_and_one_stderr_line_naming_it_writing_nothing_1292(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    got = {}
    for value in ("0", "two", "-1", ""):
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main(["--criterion", value, str(ledger), "after", "b two", "t"])
        out, err = capsys.readouterr()
        got[value] = (
            code,
            out,
            err.count("\n"),
            err.startswith("add-ledger-step.sh: ") and err.endswith(f" {value}\n"),
            ledger.read_bytes() == LEDGER,
        )
    assert got == {value: (2, "", 1, True, True) for value in ("0", "two", "-1", "")}


def test_main_refusing_too_few_arguments_prints_a_usage_line_naming_the_optional_leading_criterion_1224(capsys, add_ledger_step):
    for argv in ([], ["l.md", "after", "anchor"], ["--criterion", "2", "l.md", "after", "anchor"]):
        code = add_ledger_step.main(argv)
        out, err = capsys.readouterr()
        assert (argv, code, out, err.count("\n"), err.startswith("usage: add-ledger-step.sh [--criterion <k>] <ledger-file> ")) == (argv, 2, "", 1, True)


def test_main_refusing_too_few_arguments_prints_a_usage_line_naming_planned_alongside_criterion_1579(capsys, add_ledger_step):
    code = add_ledger_step.main([])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "--planned" in err, "--criterion" in err) == (2, "", 1, True, True)


def test_main_planned_criterion_k_inserts_unmarked_steps_that_do_not_count_toward_a_zero_step_growth_and_files_nothing_owed_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, capsys.readouterr().err, ledger.read_bytes().decode()) == (
        0,
        "",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦criterion 7⟧\n- [ ] u ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_planned_without_criterion_or_with_a_criterion_a_step_already_serves_refuses_with_2_and_one_stderr_line_writing_nothing_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n- [x] c1\n- [ ] c2\n- [ ] c3\n\n## Blocked by\n")
    got = {}
    for name, flags in (("none", []), ("served", ["--criterion", "2"])):
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main(["--planned", *flags, str(ledger), "after", "b two", "t"])
        out, err = capsys.readouterr()
        got[name] = (code, out, err.count("\n"), ledger.read_bytes() == LEDGER, "already serves" in err or name == "none")
    assert got == {name: (2, "", 1, True, True) for name in ("none", "served")}


def test_main_a_later_criterion_k_add_after_a_planned_one_is_marked_added_and_refused_into_owed_steps_at_a_spent_budget_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
    planned = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    after_planned = ledger.read_bytes()
    code = add_ledger_step.main(["--criterion", "7", str(ledger), "after", "b two", "u"])
    assert (planned, code, capsys.readouterr().err, ledger.read_bytes()) == (
        0, 1, "", after_planned + "\n## Owed steps\n\n- u\n".encode()
    )


def test_main_planned_criterion_k_beyond_the_spec_files_checkboxes_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n- [x] one\n- [ ] two\n- [ ] three\n\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "5", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 5" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "- [x] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_unticked_in_the_spec_file_and_served_by_no_step_still_inserts_unmarked_steps_and_returns_0_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, capsys.readouterr().err, ledger.read_bytes().decode()) == (
        0,
        "",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦criterion 7⟧\n- [ ] u ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_planned_criterion_k_with_no_spec_file_beside_the_ledger_refuses_with_2_naming_that_file_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), str(tmp_path / "issue-42-spec.md") in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_with_a_directory_in_place_of_the_spec_file_refuses_with_2_naming_that_path_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").mkdir()
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), str(tmp_path / "issue-42-spec.md") in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_with_a_capital_x_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "- [X] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_in_an_indented_box_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    """A box ledger.STEP_RE counts as criterion k is ticked by the same pattern, indented or not."""
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "  - [x] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7 is already ticked" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_accepts_criterion_k_before_planned_the_same_as_planned_before_criterion_k_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "0")
    got = {}
    for name, flags in (("planned first", ["--planned", "--criterion", "7"]), ("criterion first", ["--criterion", "7", "--planned"])):
        ledger = tmp_path / name / "issue-42.md"
        ledger.parent.mkdir()
        ledger.write_bytes(LEDGER)
        (ledger.parent / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
        code = add_ledger_step.main([*flags, str(ledger), "after", "b two", "t"])
        got[name] = (code, capsys.readouterr().err, ledger.read_bytes())
    assert got["criterion first"] == got["planned first"] and got["planned first"][:2] == (0, "")



def test_main_refuses_a_second_suite_repair_in_the_same_run_naming_the_first_and_files_nothing_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", before)
    assert "fix the full-suite failure: first.test.sh" in err


def test_main_inserts_a_suite_repair_after_the_last_resume_when_the_ledger_holds_one_from_before_it_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_bytes((
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode())
    events = [
        {"ts": 1, "issue": "42", "event": "step-added", "anchor": "a one", "added": "1"},
        {"ts": 2, "issue": "42", "event": "resume"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert code == 0, err
    assert "second.test.sh ⟦suite-repair⟧" in ledger.read_text()


def test_main_inserts_a_suite_repair_when_the_only_step_added_after_the_last_resume_is_for_a_non_repair_step_or_this_repair_itself_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_bytes((
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [x] b two ⟦criterion 2⟧\n"
        "- [x] c three ⟦added⟧ ⟦criterion 2⟧\n"
    ).encode())
    events = [
        {"ts": 1, "issue": "42", "event": "resume"},
        {"ts": 2, "issue": "42", "event": "step-added", "step": "b two", "anchor": "b two", "added": "1"},
        {"ts": 3, "issue": "42", "event": "step-added", "step": "c three", "anchor": "c three", "added": "1"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "c three", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert code == 0, err
    assert "second.test.sh ⟦suite-repair⟧" in ledger.read_text()


def test_main_refuses_a_second_suite_repair_inserted_after_the_last_resume_whose_step_added_event_names_only_its_anchor_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] b two ⟦criterion 2⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)
    events = [
        {"ts": 1, "issue": "42", "event": "resume"},
        {"ts": 2, "issue": "42", "event": "step-added", "step": "b two", "anchor": "b two", "added": "1"},
        {"ts": 3, "issue": "42", "event": "step-added", "step": "first.test.sh", "anchor": "first.test.sh", "added": "1"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "first.test.sh", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", before)
    assert "fix the full-suite failure: first.test.sh" in err


def test_main_refuses_a_third_suite_repair_naming_the_one_this_run_inserted_after_the_last_resume_not_an_earlier_runs_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [x] b two ⟦criterion 2⟧\n"
        "- [x] fix the full-suite failure: second.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧\n"
        "- [ ] c three ⟦criterion 3⟧\n"
    ).encode()
    ledger.write_bytes(before)
    events = [
        {"ts": 1, "issue": "42", "event": "step-added", "anchor": "a one", "added": "1"},
        {"ts": 2, "issue": "42", "event": "resume"},
        {"ts": 3, "issue": "42", "event": "step-added", "anchor": "b two", "added": "1"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "c three", "fix the full-suite failure: third.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", before)
    assert "second.test.sh" in err and "first.test.sh" not in err


def test_main_inserts_a_suite_repair_when_the_one_in_the_ledger_was_added_before_the_second_of_two_resumes_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_bytes((
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode())
    events = [
        {"ts": 1, "issue": "42", "event": "resume"},
        {"ts": 2, "issue": "42", "event": "step-added", "anchor": "a one", "added": "1"},
        {"ts": 3, "issue": "42", "event": "resume"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert code == 0, err
    assert "second.test.sh ⟦suite-repair⟧" in ledger.read_text()


def test_main_refuses_a_second_suite_repair_in_a_first_run_whose_events_hold_step_added_and_no_resume_1607(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)
    events = [
        {"ts": 1, "issue": "42", "event": "step-added", "anchor": "a one", "added": "1"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", before)
    assert "fix the full-suite failure: first.test.sh" in err


def test_main_marks_a_text_that_only_quotes_a_repair_mark_in_its_prose_added_and_counts_it_against_the_budget_1613(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    before = (
        "# Plan for #42\n"
        "\n"
        "- [ ] a one ⟦criterion 1⟧\n"
    ).encode()
    ledger.write_bytes(before)

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "a one", "explain why ⟦ci-repair⟧ and ⟦suite-repair⟧ end a repair step"],
        env={"VERI_STEP_GROWTH": "0"},
    )

    assert (code, out) == (1, "")
    assert ledger.read_bytes() == before + b"\n## Owed steps\n\n- explain why \xe2\x9f\xa6ci-repair\xe2\x9f\xa7 and \xe2\x9f\xa6suite-repair\xe2\x9f\xa7 end a repair step\n"


def test_main_inserts_a_suite_repair_when_the_only_earlier_step_this_run_merely_quotes_the_mark_in_its_prose_1613(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(
        (
            "# Plan for #42\n"
            "\n"
            "- [x] a one ⟦criterion 1⟧\n"
            "- [x] explain why ⟦suite-repair⟧ ends a repair step ⟦added⟧ ⟦criterion 1⟧\n"
            "- [ ] b two ⟦criterion 2⟧\n"
        ).encode()
    )

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: real.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, err) == (0, "", "")
    assert b"fix the full-suite failure: real.test.sh" in ledger.read_bytes()


def test_main_inserts_a_text_that_only_quotes_the_suite_repair_mark_when_this_run_already_inserted_a_suite_repair_1613(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes((
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode())

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "explain why ⟦suite-repair⟧ steps are capped per run"],
    )

    assert (code, err) == (0, "")
    assert "- [ ] explain why ⟦suite-repair⟧ steps are capped per run ⟦added⟧ ⟦criterion 2⟧\n" in ledger.read_text()


def test_main_inserts_a_suite_repair_after_the_last_resume_when_the_step_after_this_runs_anchor_only_quotes_the_mark_1613(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_bytes((
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [x] b two ⟦criterion 2⟧\n"
        "- [x] explain why ⟦suite-repair⟧ steps are capped per run ⟦added⟧ ⟦criterion 2⟧\n"
        "- [ ] c three ⟦criterion 3⟧\n"
    ).encode())
    events = [
        {"ts": 1, "issue": "42", "event": "step-added", "anchor": "a one", "added": "1"},
        {"ts": 2, "issue": "42", "event": "resume"},
        {"ts": 3, "issue": "42", "event": "step-added", "anchor": "b two", "added": "1"},
    ]
    (ledger.parent / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "c three", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert code == 0, err
    assert "second.test.sh ⟦suite-repair⟧" in ledger.read_text()


UNQUOTED_REPLACES_STEP = (
    "tests/py/test_tick_ledger.py calls veri.tick_ledger.main(argv) for a ticked step, an unmatched matcher and `[]` "
    "and asserts return codes 0, 3 and 2 — every exit inside 0–3: replaces the tick-ledger.sh half of the foreign "
    "ledger-transform code case in skills/tdd/scripts/tests/tick-ledger.test.sh, the clear-refactor-pending.sh case "
    "staying with its assertion unmodified ⟦replaces-case⟧ ⟦criterion 3⟧"
)


def test_main_refuses_a_replaces_case_step_with_unreadable_case_names_1538(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    code = add_ledger_step.main([str(ledger), "after", "b two", UNQUOTED_REPLACES_STEP])
    captured = capsys.readouterr()

    assert code == 1
    assert "tick-ledger.sh half of the foreign ledger-transform code case" in captured.out + captured.err
    assert not any(
        "⟦replaces-case⟧" in line for line in ledger.read_text().split("\n") if line.startswith("- [")
    )


def test_main_reads_an_inserted_or_replaced_step_carrying_a_kind_mark_with_that_kind_1614(tmp_path, run_cli, add_ledger_step):
    from veri.ledger import ledger_steps

    for kind in ("full-suite", "human-owed", "diff-checked"):
        for where in ("after", "instead-of"):
            ledger = tmp_path / f"issue-42-{kind}-{where}.md"
            ledger.write_bytes(LEDGER)

            code, out, err = run_cli(
                add_ledger_step,
                [str(ledger), where, "b two", f"check it ⟦{kind}⟧"],
                env={"VERI_STEP_GROWTH": "5"},
            )

            kinds = {record[6]: record[2] for record in ledger_steps(ledger.read_text())}
            added = [kinds[text] for text in kinds if text.startswith("check it")]
            assert (kind, where, code, added) == (kind, where, 0, [kind])


def test_main_counts_a_kind_marked_added_step_against_the_budget_and_owes_the_next_insertion_1614(tmp_path, run_cli, add_ledger_step):
    for kind in ("full-suite", "human-owed", "diff-checked"):
        ledger = tmp_path / f"issue-42-{kind}.md"
        ledger.write_bytes(LEDGER)
        env = {"VERI_STEP_GROWTH": "1"}

        first = run_cli(add_ledger_step, [str(ledger), "after", "b two", f"check it ⟦{kind}⟧"], env=env)
        second = run_cli(add_ledger_step, [str(ledger), "after", "b two", "one more"], env=env)

        after = ledger.read_text()
        assert (kind, first[0], second[0]) == (kind, 0, 1)
        assert "- [ ] one more" not in after
        assert after.endswith("## Owed steps\n\n- one more\n")


def test_main_exits_2_naming_the_log_and_the_unreadable_line_when_a_suite_repair_would_follow_a_malformed_events_line_leaving_the_ledger_1619(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)
    log = ledger.parent / "events.jsonl"
    log.write_text(json.dumps({"ts": 1, "issue": "42", "event": "resume"}) + "\n{not json\n")

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (2, "", before)
    assert str(log) in err and "{not json" in err


def test_main_exits_2_naming_the_log_and_the_unreadable_line_when_a_suite_repair_would_follow_an_events_line_that_is_not_utf_8_leaving_the_ledger_1619(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)
    log = ledger.parent / "events.jsonl"
    log.write_bytes(json.dumps({"ts": 1, "issue": "42", "event": "resume"}).encode() + b"\n\xff\xfe broken\n")

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (2, "", before)
    assert str(log) in err and "broken" in err


def test_main_names_the_log_and_the_unreadable_line_without_add_ledger_step_opening_events_jsonl_itself(tmp_path, monkeypatch, run_cli, add_ledger_step):
    import builtins

    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)
    log = ledger.parent / "events.jsonl"
    log.write_text(json.dumps({"ts": 1, "issue": "42", "event": "resume"}) + "\n{not json\n")
    opened = []

    def spy_open(file, *args, **kwargs):
        opened.append(str(file))
        return builtins.open(file, *args, **kwargs)

    monkeypatch.setattr(add_ledger_step, "open", spy_open, raising=False)

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (2, "", before)
    assert str(log) in err and "{not json" in err
    assert [path for path in opened if path.endswith("events.jsonl")] == []


def test_main_replaces_an_added_step_at_the_growth_budget_leaving_the_added_count_unchanged_issue_1631(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "2")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(
        "# Plan for #42\n\n"
        "- [ ] a one ⟦criterion 1⟧\n"
        "- [ ] extra one ⟦added⟧ ⟦criterion 1⟧\n"
        "- [ ] extra two ⟦added⟧ ⟦criterion 1⟧\n".encode()
    )

    code = add_ledger_step.main([str(ledger), "instead-of", "extra two", "reworded"])
    capsys.readouterr()

    text = ledger.read_bytes().decode()
    assert (code, text.count("⟦added⟧"), "extra two" in text, "reworded" in text, "## Owed steps" in text) == (0, 2, False, True, False)


def test_main_refuses_a_newline_text_at_the_growth_budget_counting_it_as_one_added_step_and_owes_it_issue_1631(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "2")
    ledger = tmp_path / "issue-42.md"
    steps = (
        "# Plan for #42\n\n"
        "- [ ] alpha ⟦criterion 1⟧\n"
        "- [ ] extra one ⟦added⟧ ⟦criterion 1⟧\n"
        "- [ ] extra two ⟦added⟧ ⟦criterion 1⟧\n"
    )
    ledger.write_bytes(steps.encode())

    code = add_ledger_step.main([str(ledger), "after", "alpha", "first line\nsecond line"])
    capsys.readouterr()

    text = ledger.read_bytes().decode()
    assert (code, text.startswith(steps), text[len(steps):]) == (1, True, "\n## Owed steps\n\n- first line\nsecond line\n")


def test_main_refuses_an_instead_of_over_an_added_anchor_with_more_texts_than_the_budget_allows_after_the_credit_and_owes_them_issue_1631(tmp_path, monkeypatch, capsys, add_ledger_step):
    monkeypatch.setenv("VERI_STEP_GROWTH", "2")
    ledger = tmp_path / "issue-42.md"
    steps = (
        "# Plan for #42\n\n"
        "- [ ] alpha ⟦criterion 1⟧\n"
        "- [ ] extra one ⟦added⟧ ⟦criterion 1⟧\n"
        "- [ ] extra two ⟦added⟧ ⟦criterion 1⟧\n"
    )
    ledger.write_bytes(steps.encode())

    code = add_ledger_step.main([str(ledger), "instead-of", "extra two", "reworded one", "reworded two"])
    capsys.readouterr()

    text = ledger.read_bytes().decode()
    assert (code, text.startswith(steps), text[len(steps):]) == (1, True, "\n## Owed steps\n\n- reworded one\n- reworded two\n")


def test_shim_header_describes_planned_and_its_exit_2_refusals_and_no_longer_lists_a_criterion_no_step_carries_1579():
    header = "\n".join(l for l in (SCRIPTS / "add-ledger-step.sh").read_text().split("\n") if l.startswith("#"))
    exit2 = header[header.index("# Exit:"):]
    planned = [l for l in header.split("\n") if "--planned" in l]

    assert (
        any("VERI_STEP_GROWTH" in l for l in planned),
        any("⟦added⟧" in l for l in planned),
        "--planned without --criterion" in exit2,
        "already serves" in exit2,
        "unticked in the issue body" in exit2,
        "readable spec file" in exit2,
        "no ledger step carries" in exit2,
    ) == (True, True, True, True, True, True, False)


def test_main_refuses_a_replaces_case_step_with_an_unquoted_name_after_a_quoted_one_or_a_trailing_parenthetical_with_one_line_naming_it_1538(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    shapes = []
    for text in (
        "x: replaces 'a', b in t/x.test.sh ⟦replaces-case⟧",
        "x: replaces 'a' (from #12) in t/x.test.sh ⟦replaces-case⟧",
    ):
        ledger.write_bytes(LEDGER)
        code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text])
        shapes.append((code, err.count("\n"), text in err, "Traceback" in err, ledger.read_bytes() == LEDGER))

    assert shapes == [(1, 1, True, False, True)] * 2


def test_main_refuses_a_replaces_case_step_mixing_quoted_and_unquoted_names_with_one_line_naming_it_1882(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    text = "x: replaces 'a', b, 'c' in t/x.test.sh ⟦replaces-case⟧"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text])

    assert (code, err.count("\n"), text in err, ledger.read_bytes() == LEDGER) == (1, 1, True, True)


def test_main_records_one_step_added_event_per_inserted_line_on_exit_0_and_none_on_exit_1_or_2_2130(tmp_path, monkeypatch, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    events = tmp_path / "events.jsonl"
    ledger.write_bytes(LEDGER)

    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first", "second"])
    assert code == 0
    inserted = [line for line in ledger.read_text().split("\n") if "⟦added⟧" in line]
    recorded = [json.loads(raw) for raw in events.read_text().splitlines()] if events.exists() else []
    assert [(e["event"], e["actor"]) for e in recorded] == [("step-added", "add-ledger-step")] * 2
    assert [line in e.values() for e, line in zip(recorded, inserted)] == [True, True]

    before = events.read_bytes()
    monkeypatch.setenv("VERI_STEP_GROWTH", "2")
    assert run_cli(add_ledger_step, [str(ledger), "after", "b two", "third"])[0] == 1
    assert run_cli(add_ledger_step, [str(ledger), "sideways", "b two", "t"])[0] == 2
    assert events.read_bytes() == before


def test_main_writes_each_inserted_step_to_the_tracked_added_file_beside_the_ledger_on_exit_0_and_none_on_exit_1_or_2_2130(tmp_path, monkeypatch, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    added = tmp_path / "issue-42-added.md"
    ledger.write_bytes(LEDGER)

    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first", "second"])
    assert code == 0
    inserted = [line for line in ledger.read_text().split("\n") if "⟦added⟧" in line]
    assert len(inserted) == 2
    recorded = added.read_text() if added.exists() else ""
    assert [line in recorded.split("\n") for line in inserted] == [True, True]

    before = added.read_bytes()
    monkeypatch.setenv("VERI_STEP_GROWTH", "2")
    assert run_cli(add_ledger_step, [str(ledger), "after", "b two", "third"])[0] == 1
    assert run_cli(add_ledger_step, [str(ledger), "sideways", "b two", "t"])[0] == 2
    assert added.read_bytes() == before


def test_main_writes_the_step_added_record_with_an_integer_ts_and_an_awake_reading_2265(tmp_path, monkeypatch, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    monkeypatch.setenv("VERI_STEP_GROWTH", "5")

    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first"])

    assert code == 0
    inserted = [line for line in ledger.read_text().split("\n") if "⟦added⟧" in line]
    record = json.loads((tmp_path / "events.jsonl").read_text().splitlines()[-1])
    assert (record["event"], record["actor"], record["step"]) == ("step-added", "add-ledger-step", inserted[0])
    assert isinstance(record.get("ts"), int)
    assert "awake" in record


def test_stop_reason_and_metrics_read_a_run_log_holding_an_add_ledger_step_insertion_2265(tmp_path, monkeypatch, run_cli, add_ledger_step):
    run = tmp_path / ".tdd" / "wt" / "42"
    ledger = run / ".tdd" / "issue-42.md"
    events = run / ".tdd" / "events.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_bytes(LEDGER)
    marks = [
        {"ts": 100, "awake": 10, "issue": "42", "event": "step-start", "step": "1"},
        {"ts": 130, "awake": 40, "issue": "42", "event": "step-done", "step": "1"}]
    events.write_text("".join(json.dumps(mark) + "\n" for mark in marks))
    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    monkeypatch.setenv("VERI_SLEEP_GAP", str(2**50))
    assert run_cli(add_ledger_step, [str(ledger), "after", "b two", "first"])[0] == 0
    with open(events, "a") as f:
        f.write(json.dumps({"ts": 2**40, "awake": 2**40, "issue": "42", "event": "done", "pr": "https://github.com/o/r/pull/9"}) + "\n")

    stopped = run_cli(importlib.import_module("veri.stop_reason"), ["42"], cwd=tmp_path)
    measured = run_cli(importlib.import_module("veri.metrics"), ["42"], cwd=run)

    assert stopped[:2] == (0, "done https://github.com/o/r/pull/9\n")
    assert "KeyError" not in stopped[2]
    assert measured[0] == 0
    assert "the log carries no awake-clock reading" not in measured[1]


def test_main_exits_2_leaving_the_ledger_the_added_file_and_the_events_log_byte_identical_when_the_awake_clock_fails_2322(tmp_path, monkeypatch, run_cli, add_ledger_step):
    from types import SimpleNamespace
    from veri import event

    ledger = tmp_path / "issue-42.md"
    added = tmp_path / "issue-42-added.md"
    events = tmp_path / "events.jsonl"
    ledger.write_bytes(LEDGER)
    added.write_text("- [ ] earlier ⟦added⟧\n")
    events.write_bytes(b'{"ts": 1, "awake": 1, "event": "step-start"}\n')
    before = (ledger.read_bytes(), added.read_bytes(), events.read_bytes())
    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    monkeypatch.setenv("VERI_AWAKE_CLOCK", "failing-clock")
    monkeypatch.setattr(event, "run_clock", lambda clock: SimpleNamespace(returncode=1, stdout=b""))

    code, _, stderr = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first"])

    assert (code, "Traceback" in stderr) == (2, False)
    assert (ledger.read_bytes(), added.read_bytes(), events.read_bytes()) == before


def test_main_refuses_an_added_skill_edit_step_whose_spec_requirements_restate_the_units_list_exactly_naming_the_unit_and_leaving_the_ledger(tmp_path, run_cli, add_ledger_step):
    unit = "skills/foo/SKILL.md"
    (tmp_path / "skills/foo").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    (tmp_path / "skills/foo/REQUIREMENTS.md").write_text(
        f"## {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text(
        f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", f"⟦skill-edit⟧ regrade `{unit}` against A1"],
        cwd=tmp_path,
    )

    assert (code, out, unit in err, "row" in err, ledger.read_bytes()) == (2, "", True, True, LEDGER), err


def test_main_accepts_an_added_skill_edit_step_whose_spec_requirements_add_a_row_the_units_list_lacks_inserting_it_marked_added(tmp_path, run_cli, add_ledger_step):
    unit = "skills/foo/SKILL.md"
    (tmp_path / "skills/foo").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    (tmp_path / "skills/foo/REQUIREMENTS.md").write_text(
        f"## {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text(
        f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    step = f"⟦skill-edit⟧ regrade `{unit}` against A1"

    code, _, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", step], cwd=tmp_path)

    inserted = [line for line in ledger.read_text().splitlines() if f"regrade `{unit}`" in line]
    assert (code, len(inserted), "⟦added⟧" in inserted[0] if inserted else None) == (0, 1, True), err


def test_main_accepts_an_added_skill_edit_step_whose_spec_requirements_reword_one_row_and_drop_another_inserting_it_marked_added(tmp_path, run_cli, add_ledger_step):
    unit = "skills/foo/SKILL.md"
    (tmp_path / "skills/foo").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    (tmp_path / "skills/foo/REQUIREMENTS.md").write_text(
        f"## {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text(
        f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is navy. | because |\n"
        "| A2 | (dropped) | shape |\n")
    step = f"⟦skill-edit⟧ regrade `{unit}` against A1"

    code, _, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", step], cwd=tmp_path)

    inserted = [line for line in ledger.read_text().splitlines() if f"regrade `{unit}`" in line]
    assert (code, len(inserted), "⟦added⟧" in inserted[0] if inserted else None) == (0, 1, True), err


@pytest.mark.parametrize("flags", ([], ["--criterion", "3"]), ids=("no-criterion-flag", "criterion-flag"))
@pytest.mark.parametrize("texts", (
    ["some step ⟦criterion 1⟧"],
    ["a clean step", "some step ⟦criterion 1⟧"],
), ids=("alone", "second-in-a-batch"))
def test_2713_a_text_already_carrying_a_criterion_tag_exits_2_names_the_tag_and_inserts_nothing(
        tmp_path, monkeypatch, capsys, add_ledger_step, flags, texts):
    monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    code = add_ledger_step.main(flags + [str(ledger), "after", "b two", *texts])

    captured = capsys.readouterr()
    assert (code, "⟦criterion 1⟧" in captured.err, ledger.read_bytes()) == (2, True, LEDGER)
    assert not (tmp_path / "issue-42-added.md").exists()
