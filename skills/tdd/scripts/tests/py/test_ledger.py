"""In-process cases for veri/ledger.py, the ledger reader lib/ledger.sh's ledger_steps defines in bash."""
import importlib


def test_ledger_steps_returns_the_records_lib_ledger_sh_prints():
    text = (
        "# Plan for #9 — cogs mesh\n"
        "\n"
        "- [x] a cog exists ⟦criterion 1⟧\n"
        "- [X] two cogs mesh ⟦criterion 2⟧ ⟂ refactor pending\n"
        "- [ ] a cog turns ⟦full-suite⟧ ⟦criterion 2⟧\n"
        "  - [ ] a gear slips ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending\n"
        "not a step - [ ] at all\n"
        "- [ ] the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 4⟧\n"
        "- [ ] a note with no criterion"
    )

    ledger = importlib.import_module("veri.ledger")

    assert [tuple(record) for record in ledger.ledger_steps(text)] == [
        ("1", "done", "step", "0", "0", "1", "a cog exists ⟦criterion 1⟧"),
        ("2", "done", "step", "1", "0", "2", "two cogs mesh ⟦criterion 2⟧"),
        ("3", "open", "full-suite", "0", "0", "2", "a cog turns ⟦full-suite⟧ ⟦criterion 2⟧"),
        ("4", "open", "step", "0", "1", "3", "a gear slips ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending"),
        ("5", "open", "human-owed", "0", "0", "4", "the PR body lists the cogs ⟦human-owed⟧ ⟦criterion 4⟧"),
        ("6", "open", "step", "0", "0", "", "a note with no criterion"),
    ]


def test_ledger_steps_returns_kind_diff_checked_for_an_open_diff_checked_step():
    ledger = importlib.import_module("veri.ledger")

    assert [tuple(record) for record in ledger.ledger_steps("- [ ] x ⟦diff-checked⟧ ⟦criterion 3⟧\n")] == [
        ("1", "open", "diff-checked", "0", "0", "3", "x ⟦diff-checked⟧ ⟦criterion 3⟧"),
    ]


def test_ledger_steps_marks_added_only_by_lib_ledger_sh_s_suffix_rule():
    text = (
        "- [ ] a ⟦added⟧ b ⟦criterion 2⟧\n"
        "- [ ] ⟦added⟧\n"
        "- [ ] t ⟦added⟧ ⟦criterion 2⟧ ⟂ refactor pending\n"
        "- [ ] x ⟦added⟧ ⟦criterion 2⟧ y\n"
        "- [ ] x ⟦added⟧\n"
    )

    ledger = importlib.import_module("veri.ledger")

    assert [tuple(record) for record in ledger.ledger_steps(text)] == [
        ("1", "open", "step", "0", "0", "2", "a ⟦added⟧ b ⟦criterion 2⟧"),
        ("2", "open", "step", "0", "0", "", "⟦added⟧"),
        ("3", "open", "step", "0", "1", "2", "t ⟦added⟧ ⟦criterion 2⟧ ⟂ refactor pending"),
        ("4", "open", "step", "0", "0", "2", "x ⟦added⟧ ⟦criterion 2⟧ y"),
        ("5", "open", "step", "0", "1", "", "x ⟦added⟧"),
    ]


def test_ledger_steps_reads_no_step_from_a_line_led_by_nbsp_em_space_or_x1c():
    text = (
        " - [ ] nbsp\n"
        " - [ ] em\n"
        "\x1c- [ ] fs\n"
        "\t- [ ] tab\n"
    )

    ledger = importlib.import_module("veri.ledger")

    assert [tuple(record) for record in ledger.ledger_steps(text)] == [
        ("1", "open", "step", "0", "0", "", "tab"),
    ]


def test_new_step_returns_lib_ledger_sh_s_added_step_line():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.new_step("t", "2").encode() == "- [ ] t ⟦added⟧ ⟦criterion 2⟧".encode()


def test_ledger_tick_ticks_the_first_open_step_whose_whole_line_holds_the_matcher():
    text = (
        "# Plan\n"
        "- [x] two done\n"
        "- [X] two shouted\n"
        "- [ ] one a*b\n"
        "  - [ ] two\n"
        "- [ ] three\n"
    )

    ledger = importlib.import_module("veri.ledger")

    assert ledger.ledger_tick(text, "two") == (True, text.replace("  - [ ] two", "  - [x] two"))
    assert ledger.ledger_tick(text, "- [ ] t") == (True, text.replace("  - [ ] two", "  - [x] two"))
    assert ledger.ledger_tick(text, "[ ]") == (True, text.replace("- [ ] one", "- [x] one"))
    assert ledger.ledger_tick(text, "") == (True, text.replace("- [ ] one", "- [x] one"))
    assert ledger.ledger_tick(text, "a*b") == (True, text.replace("- [ ] one", "- [x] one"))
    assert ledger.ledger_tick(text, "*") == (True, text.replace("- [ ] one", "- [x] one"))
    assert ledger.ledger_tick(text, "a.b") == (False, text)
    assert ledger.ledger_tick(text, "done") == (False, text)
    assert ledger.ledger_tick(text, "shouted") == (False, text)


def test_ledger_tick_ticks_a_bare_box_with_nothing_after_it():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.ledger_tick("- [x] a\n- [ ]\n", "") == (True, "- [x] a\n- [x]\n")


def test_ledger_tick_copies_every_character_but_the_ticked_box_unchanged():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.ledger_tick("- [ ] a\n- [ ] b", "b") == (True, "- [ ] a\n- [x] b")
    assert ledger.ledger_tick("- [ ] a\n\n\n", "a") == (True, "- [x] a\n\n\n")
    assert ledger.ledger_tick("- [x] a\r\n- [ ] b\r\n", "b") == (True, "- [x] a\r\n- [x] b\r\n")


def test_ledger_tick_appends_the_refactor_pending_mark_at_the_line_end_only_when_asked():
    seed = "# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n- [ ] strip edge hyphens\n"

    ledger = importlib.import_module("veri.ledger")

    assert ledger.ledger_tick(seed, "collapse to single hyphen", pending=True) == (
        True,
        "# Plan for #42\n\n- [ ] add lowercasing\n- [x] collapse to single hyphen ⟂ refactor pending\n- [ ] strip edge hyphens\n",
    )
    assert ledger.ledger_tick("- [ ] a\r\n", "a", pending=True) == (True, "- [x] a\r ⟂ refactor pending\n")
    assert ledger.ledger_tick(seed, "collapse to single hyphen") == (
        True,
        "# Plan for #42\n\n- [ ] add lowercasing\n- [x] collapse to single hyphen\n- [ ] strip edge hyphens\n",
    )
