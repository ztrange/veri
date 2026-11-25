"""In-process cases for veri/ledger.py, the ledger reader."""
import errno
import importlib
import os

import pytest


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



def test_4472_a_diff_checked_step_verify_branch_appended_keeps_its_kind_past_the_branch_repair_mark():
    ledger = importlib.import_module("veri.ledger")

    steps = ledger.ledger_steps("- [ ] x ⟦diff-checked⟧ ⟦branch-repair⟧ ⟦criterion 3⟧\n")

    assert [(step.kind, step.criterion) for step in steps] == [("diff-checked", "3")]

def test_4472_a_branch_repair_step_without_diff_checked_is_read_as_kind_step_with_its_criterion():
    ledger = importlib.import_module("veri.ledger")

    steps = ledger.ledger_steps("- [ ] x ⟦branch-repair⟧ ⟦criterion 3⟧\n")

    assert [(step.kind, step.criterion) for step in steps] == [("step", "3")]

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


def test_the_four_ledger_entry_points_drop_a_nul_and_keep_a_non_utf8_byte_without_exiting_2(tmp_path, monkeypatch, run_cli):
    monkeypatch.setattr(importlib.import_module("veri.add_ledger_step"), "verified_plan_size", lambda path: 2)
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
    monkeypatch.setattr(importlib.import_module("veri.add_ledger_step"), "verified_plan_size", lambda path: 2)
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


def test_ledger_items_parses_an_indented_checkbox_line_as_an_item():
    ledger = importlib.import_module("veri.ledger")

    items = ledger.ledger_items("  - [ ] indented step\n- [x] top step\nnot - [ ] an item\n")

    assert [(m.group(1), m.group(2)) for m in items] == [(" ", "indented step"), ("x", "top step")]


def test_items_at_raises_oserror_naming_rev_path_and_stderr_when_git_show_fails(monkeypatch):
    ledger = importlib.import_module("veri.ledger")

    class Failed:
        returncode = 128
        stdout = b""
        stderr = b"fatal: path 'x/ledger.md'\n  does not exist in 'abc123'\n"

    monkeypatch.setattr(ledger, "git", lambda *args, **kwargs: Failed())

    try:
        ledger.items_at("abc123", "x/ledger.md")
    except OSError as error:
        assert str(error) == "git show abc123:x/ledger.md failed: fatal: path 'x/ledger.md' does not exist in 'abc123'"
    else:
        raise AssertionError("items_at returned for a failed git show")


def test_is_skill_edit_equals_the_inline_marker_expression_for_leading_trailing_and_unmarked_steps():
    ledger = importlib.import_module("veri.ledger")

    def inline(step):
        return step.startswith("⟦skill-edit⟧") or ledger.carries_mark(ledger.trailing_markers(step), "skill-edit")

    for step, expected in (
        ("⟦skill-edit⟧ edit `skills/tdd/SKILL.md`", True),
        ("edit the skill ⟦skill-edit⟧ ⟦criterion 1⟧", True),
        ("a cog turns ⟦criterion 1⟧", False),
    ):
        assert inline(step) is expected
        assert ledger.is_skill_edit(step) is expected


def test_body_is_the_step_text_before_the_first_mark():
    ledger = importlib.import_module("veri.ledger")
    assert ledger.body("a step ⟦added⟧ ⟂ refactor pending") == "a step ⟦added⟧"
    assert ledger.body("a step ⟂ red done ⟂ green done") == "a step"
    assert ledger.body("a step") == "a step"
    assert ledger.body("⟂ not a delimiter: no leading space") == "⟂ not a delimiter: no leading space"


def test_open_step_line_is_the_unticked_checkbox_line_new_step_builds_on():
    ledger = importlib.import_module("veri.ledger")
    assert ledger.open_step_line("do it") == "- [ ] do it"
    assert ledger.new_step("do it", 3) == ledger.open_step_line("do it ⟦added⟧ ⟦criterion 3⟧")


def test_tick_line_ticks_the_box_of_a_matched_step_line_and_keeps_the_rest():
    ledger = importlib.import_module("veri.ledger")
    for line in ("- [ ] do it ⟂ red done", "  - [ ]", "- [ ] "):
        assert ledger.tick_line(ledger.STEP_RE.fullmatch(line)) == line.replace("[ ]", "[x]", 1)


def test_retire_mark_and_is_retired_agree_on_the_marks_a_retired_step_carries():
    ledger = importlib.import_module("veri.ledger")
    assert ledger.retire_mark("unpinnable") == " ⟂ retired unpinnable"
    assert ledger.retire_mark("already holds") == " ⟂ retired already holds"
    assert ledger.is_retired("- [x] a step" + ledger.retire_mark("unpinnable"))
    assert not ledger.is_retired("- [x] a step ⟂ red done")


def test_before_state_green_matches_a_clause_that_calls_the_before_state_green_and_no_clause_that_fails_negates_or_looks_after():
    ledger = importlib.import_module("veri.ledger")
    answers = {
        reason: bool(ledger.BEFORE_STATE_GREEN.search(reason))
        for reason in [
            "the before-state is green",
            "REASON: the before-state already passes",
            "x, green on the before-state",
            "fails on the before-state and passes after",
            "the before-state is not green",
            "the before-state is red",
            "green after the before-state",
        ]
    }

    assert answers == {
        "the before-state is green": True,
        "REASON: the before-state already passes": True,
        "x, green on the before-state": True,
        "fails on the before-state and passes after": False,
        "the before-state is not green": False,
        "the before-state is red": False,
        "green after the before-state": False,
    }


def test_added_file_is_the_added_md_sibling_of_a_ledger_file():
    ledger = importlib.import_module("veri.ledger")

    assert [ledger.added_file(p) for p in ["/run/.tdd/issue-7.md", "issue-7", "a.md.md"]] == [
        "/run/.tdd/issue-7-added.md", "issue-7-added.md", "a.md-added.md"]


def test_interface_phases_are_the_phases_of_an_interface_change():
    ledger = importlib.import_module("veri.ledger")
    assert ledger.INTERFACE_PHASES == ("expand", "cover-new", "migrate", "contract-a", "contract-b")


def test_a_step_record_reads_by_name_and_stays_the_tuple_ledger_steps_printed():
    ledger = importlib.import_module("veri.ledger")

    [record] = ledger.ledger_steps("- [X] two cogs mesh ⟦added⟧ ⟦criterion 2⟧ ⟂ refactor pending")

    assert (record.number, record.state, record.kind, record.pending, record.added, record.criterion, record.text) == (
        "1", "done", "step", "1", "1", "2", "two cogs mesh ⟦added⟧ ⟦criterion 2⟧")
    assert record == ("1", "done", "step", "1", "1", "2", "two cogs mesh ⟦added⟧ ⟦criterion 2⟧")
    assert "\t".join(record) == "1\tdone\tstep\t1\t1\t2\ttwo cogs mesh ⟦added⟧ ⟦criterion 2⟧"


STEPS_TEXT = (
    "- [x] a cog exists ⟦criterion 1⟧\n"
    "- [ ] two cogs mesh ⟦criterion 2⟧\n"
    "- [ ] two cogs mesh ⟦criterion 2⟧\n"
    "- [ ] 7\n"
)


def steps_of(ledger):
    return ledger.ledger_steps(STEPS_TEXT)


def test_step_at_names_the_step_a_number_reference_counts_to():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.step_at(steps_of(ledger), "2").text == "two cogs mesh ⟦criterion 2⟧"
    assert ledger.step_at(steps_of(ledger), "2").number == "2"


def test_step_at_answers_none_for_a_number_past_the_last_step_or_below_the_first_or_not_a_decimal():
    ledger = importlib.import_module("veri.ledger")
    steps = steps_of(ledger)

    assert [ledger.step_at(steps, ref) for ref in ("0", "5", "99999999999999999999", "²")] == [None] * 4


def test_step_at_reads_leading_zeros_as_the_number_they_spell():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.step_at(steps_of(ledger), "01").number == "1"


def test_step_at_names_the_first_step_whose_text_is_the_reference_when_it_is_no_number():
    ledger = importlib.import_module("veri.ledger")

    assert ledger.step_at(steps_of(ledger), "two cogs mesh ⟦criterion 2⟧").number == "2"
    assert ledger.step_at(steps_of(ledger), "two cogs mesh") is None


def test_step_at_never_looks_a_number_reference_up_as_text_unless_asked_to_by_index():
    ledger = importlib.import_module("veri.ledger")
    steps = steps_of(ledger)

    assert ledger.step_at(steps, "7") is None
    assert ledger.step_at(steps, "7", by_index=True).number == "4"


def test_step_at_by_index_takes_an_index_only_as_the_digits_it_was_numbered_with():
    ledger = importlib.import_module("veri.ledger")
    steps = steps_of(ledger)

    assert ledger.step_at(steps, "3", by_index=True).number == "3"
    assert ledger.step_at(steps, "03", by_index=True) is None


def test_step_at_takes_the_text_rule_as_a_parameter():
    ledger = importlib.import_module("veri.ledger")

    found = ledger.step_at(steps_of(ledger), "two cogs", text_matches=lambda reference, text: text.startswith(reference))

    assert found.number == "2"


def test_unit_of_returns_a_heading_unit_whose_heading_holds_backticks_whole():
    ledger = importlib.import_module("veri.ledger")
    unit = "skills/tdd/SKILL.md#Before the Red of a `⟦suite-repair⟧` step — is the suite still red?"

    assert ledger.unit_of(f"edit `{unit}` ⟦skill-edit⟧") == unit


def test_unit_of_ends_a_backticked_heading_unit_at_its_own_closing_backtick_when_another_span_follows():
    ledger = importlib.import_module("veri.ledger")
    unit = "skills/tdd/SKILL.md#A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"

    assert ledger.unit_of(f"edit `{unit}` per `foo` ⟦skill-edit⟧") == unit


def test_unit_of_returns_a_heading_unit_whose_closing_backtick_is_followed_by_punctuation():
    ledger = importlib.import_module("veri.ledger")
    unit = "skills/tdd/SKILL.md#Plain heading"

    assert ledger.unit_of(f"edit `{unit}`. ⟦skill-edit⟧") == unit


@pytest.mark.parametrize("after", [", then `foo` here", ". See `foo` now", ": `foo` x"])
def test_unit_of_ends_a_heading_unit_at_a_punctuation_closed_backtick_when_a_later_span_follows(after):
    ledger = importlib.import_module("veri.ledger")

    assert ledger.unit_of(f"edit `a/b.md#Plain heading`{after}") == "a/b.md#Plain heading"


@pytest.mark.parametrize("text, unit", [
    ("edit `a/b.md#H ` per `foo` x", "a/b.md#H "),
    ("edit `a/b.md#A\t`x` y` z", "a/b.md#A\t`x` y"),
    ("edit `a/b.md#H `x` y `z` tail", "a/b.md#H "),
    ("edit `a/b `c` d` x", "a/b "),
    ("edit `a/b.md#H `\t per `foo` x", "a/b.md#H "),
    ("edit `a/b.md#H `` y` z", "a/b.md#H `` y"),
    ("edit `a/b.md#Use `foo`` x", "a/b.md#Use `foo`"),
])
def test_unit_of_opens_an_inner_pair_only_at_a_whitespace_preceded_backtick_of_a_closed_heading_unit(text, unit):
    ledger = importlib.import_module("veri.ledger")

    assert ledger.unit_of(text) == unit


def test_same_step_reads_texts_differing_only_by_marks_and_a_trailing_suffix_as_one_step_4342():
    ledger = importlib.import_module("veri.ledger")
    step = "a cog turns ⟦criterion 2⟧"
    assert [ledger.same_step(step, other) for other in (
        "a cog turns ⟦added⟧ ⟦criterion 3⟧",
        "a cog turns",
        "a cog turns ⟦criterion 2⟧ ⟂ refactor pending",
        "a cog turns ⟦full-suite⟧ ⟦criterion 2⟧ ⟂ expand done",
        "a cog spins ⟦criterion 2⟧",
        "a cog turns twice ⟦criterion 2⟧",
    )] == [True, True, True, True, False, False]


@pytest.mark.parametrize("step, expected", [
    ("Go-red guard: probe `a.py` `x` → `y` on `t.py::c` ⟦go-red⟧ ⟦criterion 1⟧", True),
    ("Go-red guard: probe `a.py` `x` → `y` on `t.py::c` ⟦go-red⟧", True),
    ("SKILL.md routes a `⟦go-red⟧` step to go-red-step.sh ⟦criterion 1⟧", False),
    ("⟦go-red⟧ Go-red guard: probe `a.py` `x` → `y` on `t.py::c` ⟦criterion 1⟧", False),
], ids=["trailing-before-criterion", "trailing-last", "backticked-mention", "leading"])
def test_is_go_red_counts_the_marker_only_among_the_steps_trailing_markers_4443(step, expected):
    ledger = importlib.import_module("veri.ledger")

    assert ledger.is_go_red(step) is expected


@pytest.mark.parametrize("step, mark, expected", [
    ("repair the build ⟦ci-repair⟧ ⟦criterion 1⟧", "⟦ci-repair⟧", True),
    ("repair the build ⟦ci-repair⟧", "⟦ci-repair⟧", True),
    ("a step quoting `⟦ci-repair⟧` in prose ⟦criterion 1⟧", "⟦ci-repair⟧", False),
    ("expand it ⟦phases: expand, migrate⟧ ⟦criterion 1⟧", "⟦phases:", True),
    ("⟦skill-edit⟧ edit `a/b.md` ⟦criterion 1⟧", "⟦skill-edit⟧", True),
    ("⟦diff-checked⟧ edit the case of the pin on `t.py::c` ⟦criterion 1⟧", "⟦diff-checked⟧", False),
    ("⟦ci-repair⟧ repair the build ⟦criterion 1⟧", "⟦ci-repair⟧", False),
    ("⟦diff-checked⟧ edit a case ⟦criterion 1⟧", "⟦diff-checked⟧", False),
    ("⟦diff-checked⟧ edit the case of the pin on `t.py::c` ⟦criterion 1⟧", "⟦skill-edit⟧", False),
    ("- [ ] ⟦skill-edit⟧ edit `a/b.md` ⟦criterion 1⟧", "⟦skill-edit⟧", True),
    ("- [x] ⟦skill-edit⟧ edit `a/b.md` ⟦criterion 1⟧", "⟦skill-edit⟧", True),
    ("- [ ] ⟦diff-checked⟧ edit the case of the pin on `t.py::c` ⟦criterion 1⟧", "⟦diff-checked⟧", False),
    ("- [ ] ⟦ci-repair⟧ repair the build ⟦criterion 1⟧", "⟦ci-repair⟧", False),
    ("- [ ] repair the build ⟦ci-repair⟧ ⟦criterion 1⟧", "⟦ci-repair⟧", True),
])
def test_4741_has_kind_reads_the_trailing_run_and_only_the_leading_skill_edit_form(step, mark, expected):
    ledger = importlib.import_module("veri.ledger")

    assert ledger.has_kind(step, mark) is expected


def test_4712_a_deviation_line_is_an_unticked_human_owed_line_of_its_criterion_naming_its_rule():
    ledger = importlib.import_module("veri.ledger")
    line = ("deviated from graded-edit at step 3: added a ⟦skill-edit⟧ step — the criterion names the prose"
            " ⟦human-owed⟧ ⟦deviation graded-edit⟧ ⟦criterion 2⟧")

    steps = ledger.ledger_steps("- [ ] " + line + "\n")

    assert [(step.state, step.kind, step.criterion) for step in steps] == [("open", "human-owed", "2")]
    assert (ledger.deviation_rule(line), ledger.deviation_rule("x ⟦human-owed⟧ ⟦criterion 2⟧")) == ("graded-edit", None)
