"""In-process cases for veri/ledger.py, the ledger reader."""
import errno
import importlib
import os


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
        ("4", "open", "step", "0", "0", "", "x ⟦added⟧ ⟦criterion 2⟧ y"),
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


def test_the_four_ledger_entry_points_drop_a_nul_and_keep_a_non_utf8_byte_without_exiting_2(tmp_path, run_cli):
    cases = {
        "tick_ledger": (b"- [ ] alpha\0 \xff\n- [ ] bravo\n", ["{p}", "alpha"]),
        "clear_refactor_pending": (b"- [x] alpha\0 \xff \xe2\x9f\x82 refactor pending\n- [ ] bravo\n", ["{p}", "alpha"]),
        "reorder_ledger_steps": (b"- [ ] alpha\0 \xff\n- [ ] bravo\n", ["{p}", "alpha", "after", "bravo"]),
        "add_ledger_step": (b"- [ ] alpha\0 \xff\n- [ ] bravo\n", ["{p}", "after", "bravo", "- [ ] charlie"]),
    }
    for name, (original, argv) in cases.items():
        path = tmp_path / (name + ".md")
        path.write_bytes(original)

        code, out, err = run_cli(importlib.import_module("veri." + name), [a.format(p=path) for a in argv])

        assert (name, code) == (name, 0), err
        assert b"\0" not in path.read_bytes(), name
        assert b"alpha \xff" in path.read_bytes(), name


def test_the_four_entry_points_exit_2_and_name_the_temporary_file_when_a_failed_write_leaves_it_behind(tmp_path, monkeypatch, run_cli):
    seed = b"- [ ] alpha\n- [ ] beta\n"
    real_replace, real_unlink = os.replace, os.unlink
    left = []

    def refusing_replace(src, dst, *args, **kwargs):
        if os.path.basename(dst) == "ledger.md":
            raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
        return real_replace(src, dst, *args, **kwargs)

    def failing_unlink(path, *args, **kwargs):
        real_unlink(path, *args, **kwargs)
        if os.path.basename(os.path.dirname(os.path.abspath(path))) == "ledger-dir":
            left.append(os.path.basename(path))
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)

    monkeypatch.setattr(os, "replace", refusing_replace)
    monkeypatch.setattr(os, "unlink", failing_unlink)
    monkeypatch.setenv("VERI_STEP_GROWTH", "5")
    outcomes = {}
    for module, rest in (
        ("tick_ledger", ["beta"]),
        ("add_ledger_step", ["after", "alpha", "gamma"]),
        ("reorder_ledger_steps", ["beta", "before", "alpha"]),
        ("clear_refactor_pending", ["beta"]),
    ):
        directory = tmp_path / module / "ledger-dir"
        directory.mkdir(parents=True)
        ledger = directory / "ledger.md"
        ledger.write_bytes(seed + (b"- [x] beta \xe2\x9f\x82 refactor pending\n" if module == "clear_refactor_pending" else b""))
        left.clear()
        code, out, err = run_cli(importlib.import_module("veri." + module), [str(ledger), *rest])
        outcomes[module] = (code, bool(left) and all(name in err for name in left), "Traceback" in err)

    assert outcomes == {name: (2, True, False) for name in outcomes}


def test_ledger_path_is_the_issue_ledger_under_the_run_directory():
    ledger = importlib.import_module("veri.ledger")

    assert str(ledger.ledger_path("/run/dir", "7")) == "/run/dir/.tdd/issue-7.md"
