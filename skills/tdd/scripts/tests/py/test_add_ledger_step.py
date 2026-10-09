"""In-process cases for veri/add_ledger_step.py, the module add-ledger-step.sh is a shim over."""
import importlib

import pytest

USAGE = (
    "usage: add-ledger-step.sh [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]\n"
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
        inode = ledger.stat().st_ino
        code = add_ledger_step.main([str(ledger), "after", anchor, "t"])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err, ledger.read_bytes(), ledger.stat().st_ino == inode)
    step = "- [ ] t ⟦added⟧ ⟦criterion 1⟧\n".encode()
    assert got == {
        "anchor on an unterminated last line": (
            0, "", "", unterminated + b"\n" + "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n".encode(), True
        ),
        "insert before an unterminated last line": (
            0, "", "", unterminated.replace(
                "a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step
            ) + b"\n", True,
        ),
        "crlf": (
            0, "", "", crlf.replace("a one ⟦criterion 1⟧\r\n".encode(), "a one ⟦criterion 1⟧\r\n".encode() + step), True
        ),
        "non-utf-8": (
            0, "", "", latin.replace("a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step), True
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
