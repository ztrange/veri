"""In-process cases for veri/add_ledger_step.py, the module add-ledger-step.sh is a shim over."""
import importlib
import json
import os
import types

import pytest

from conftest import SCRIPTS

USAGE = (
    "usage: add-ledger-step.sh [--planned] [--criterion <k>] <ledger-file> after|before|instead-of <anchor-substring> <text> [<text> …]  (--planned goes with --criterion <k>)\n"
)

LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] a one ⟦criterion 1⟧\n"
    "- [ ] b two ⟦criterion 2⟧\n"
    "- [ ] c three ⟦criterion 3⟧\n"
).encode()


NOT_DURABLE = "not durable"


def settled(err):
    return NOT_DURABLE if err.count("\n") == 1 and NOT_DURABLE in err.lower() else err


# The commit `ledger-growth.sh plan-sha` prints, faked at the git boundary for every case below: its ledger holds
# PLAN.steps planned steps, or (None) the ledger as it stood when add-ledger-step.sh first read that file in the case.
PLAN = types.SimpleNamespace(steps=None, held={})
PLAN_LOG = "beef plan: scope #42 into 3 steps (#42)\n"


def show_plan(line, cwd=None, **_):
    if PLAN.steps is not None:
        return 0, "".join("- [ ] planned step %d\n" % i for i in range(PLAN.steps)), ""
    path = os.path.join(cwd, line.rsplit(":./", 1)[1])
    if path not in PLAN.held:
        with open(path, "rb") as f:
            PLAN.held[path] = f.read()
    return 0, PLAN.held[path], ""


PLAN_COMMIT = {"git log --format=%H %s": (0, PLAN_LOG, ""), "git show beef:./": show_plan}


@pytest.fixture(autouse=True)
def verified_plan(fake_processes, monkeypatch):
    monkeypatch.setattr(PLAN, "steps", None)
    monkeypatch.setattr(PLAN, "held", {})
    return fake_processes.answers(PLAN_COMMIT)


def cap_at(monkeypatch, budget):
    """Cap the ledger's ⟦added⟧ steps at <budget>: a plan commit of that many steps, all of them allowed as growth."""
    monkeypatch.setattr(PLAN, "steps", int(budget))
    monkeypatch.setenv("VERI_STEP_GROWTH_PERCENT", "100")


@pytest.fixture
def add_ledger_step():
    return importlib.import_module("veri.add_ledger_step")


def test_main_refuses_bad_arguments_with_exit_2_and_inserts_after_the_anchor(tmp_path, monkeypatch, capsys, add_ledger_step):
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



def test_4075_the_batch_is_capped_at_the_percent_of_the_steps_at_the_plan_commit_rounded_up_and_a_refused_percent_exits_2(
        tmp_path, run_cli, fake_processes, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    fake = fake_processes.answers({
        "git log --format=%H %s": (0, "f00d note: unrelated\nbeef plan: scope #42 into 3 steps (#42)\n", ""),
        "git show beef:./issue-42.md": (0, LEDGER.decode(), ""),
    })

    fits = run_cli(add_ledger_step, [str(ledger), "after", "b two", "x one", "x two"], cwd=tmp_path)
    grown = ledger.read_bytes()
    past = run_cli(add_ledger_step, [str(ledger), "after", "b two", "x three"], cwd=tmp_path)
    after_past = ledger.read_bytes()
    refused = run_cli(add_ledger_step, [str(ledger), "after", "b two", "x four"], env={"VERI_STEP_GROWTH_PERCENT": "x"},
                      cwd=tmp_path)

    assert (fits[0], grown.decode().count("⟦added⟧"), past[0], after_past.decode().split("\n## Owed steps")[0], refused[0],
            "VERI_STEP_GROWTH_PERCENT" in refused[2], ledger.read_bytes()) == (
        0, 2, 1, grown.decode(), 2, True, after_past), (fits, past, refused, fake.calls)



def test_4075_a_history_naming_no_plan_commit_or_one_git_cannot_show_exits_2_leaving_the_ledger(
        tmp_path, run_cli, fake_processes, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    got = []
    for table in ({"git log": (0, "f00d note: unrelated\n", "")}, {"git log": (128, "", "not a git repository\n")},
                  {"git log": (0, "beef plan: rewrite #42\n", ""), "git show": (128, "", "no such path\n")}):
        fake_processes.answers(table)
        code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", "t"], cwd=tmp_path)
        got.append((code, out, "no plan commit" in err, ledger.read_bytes()))

    assert got == [(2, "", True, LEDGER)] * 3



def test_4075_a_set_retired_veri_step_growth_exits_2_naming_veri_step_growth_percent_leaving_the_ledger(
        tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    got = [run_cli(add_ledger_step, [str(ledger), "after", "b two", "t"], env={"VERI_STEP_GROWTH": value}, cwd=tmp_path)
           for value in ("5", "")]

    assert [(code, out, "VERI_STEP_GROWTH_PERCENT" in err) for code, out, err in got] == [(2, "", True)] * 2
    assert ledger.read_bytes() == LEDGER


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
    cap_at(monkeypatch, "1")
    ledger = tmp_path / "issue-42.md"
    got = {}
    for line, _ in COUNTED_FIXTURES:
        ledger.write_bytes(f"# Plan for #42\n\n{line}\n- [ ] the probe anchor ⟦criterion 9⟧\n".encode())
        got[line] = add_ledger_step.main([str(ledger), "after", "the probe anchor", "a probe step"])
        capsys.readouterr()
    assert got == dict(COUNTED_FIXTURES)


def test_main_inserts_beside_the_one_dash_step_holding_the_anchor_leaving_prose_and_star_lines_alone(tmp_path, monkeypatch, capsys, add_ledger_step):
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
    assert (code, settled(captured.err)) == (0, NOT_DURABLE)
    assert ledger.read_bytes().decode() == (
        "# Plan for #42\n"
        "\n"
        "a lamp glows in this prose line\n"
        "* [ ] a lamp glows\n"
        "- [ ] a lamp glows ⟦criterion 2⟧\n"
        "- [ ] a lamp dims ⟦added⟧ ⟦criterion 2⟧\n"
    )


def test_main_inserts_the_line_veri_ledger_new_step_returns_for_the_text_and_the_anchor_criterion(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes("# Plan for #42\n\n- [ ] a lamp glows ⟦criterion 2⟧\n".encode())
    code = add_ledger_step.main([str(ledger), "after", "a lamp glows", "a lamp dims"])
    capsys.readouterr()
    assert code == 0
    assert ledger.read_bytes().split(b"\n")[3] == importlib.import_module("veri.ledger").new_step("a lamp dims", "2").encode()


def test_main_puts_the_texts_above_below_or_in_place_of_the_anchor_and_gives_none_a_criterion_the_anchor_lacks(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    head = "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
    anchor = "- [ ] b two ⟦criterion 2⟧\n"
    added = "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n- [ ] u ⟦added⟧ ⟦criterion 2⟧\n"
    tail = "- [ ] c three ⟦criterion 3⟧\n"
    got = {}
    for where in ("before", "after", "instead-of"):
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main([str(ledger), where, "b two", "t", "u"])
        got[where] = (code, settled(capsys.readouterr().err), ledger.read_bytes().decode())
    assert got == {
        "before": (0, NOT_DURABLE, head + added + anchor + tail),
        "after": (0, NOT_DURABLE, head + anchor + added + tail),
        "instead-of": (0, NOT_DURABLE, head + added + tail),
    }

    cap_at(monkeypatch, "1")
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main([str(ledger), "instead-of", "c three", "t", "u"])
    assert (code, ledger.read_bytes()) == (1, LEDGER + "\n## Owed steps\n\n- t\n- u\n".encode())
    monkeypatch.delenv("VERI_STEP_GROWTH_PERCENT")
    monkeypatch.setattr(PLAN, "steps", None)

    ledger.write_bytes("# Plan for #42\n\n- [ ] b two\n".encode())
    code = add_ledger_step.main([str(ledger), "after", "b two", "t"])
    assert (code, ledger.read_bytes().decode()) == (0, "# Plan for #42\n\n- [ ] b two\n- [ ] t ⟦added⟧\n")


def test_main_inherits_the_last_criterion_unvalidated_and_writes_empty_multiline_and_indented_inserts_verbatim(tmp_path, monkeypatch, capsys, add_ledger_step):
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
        got[name] = (code, settled(capsys.readouterr().err), ledger.read_bytes().decode())
    assert got == {
        "unvalidated": (0, NOT_DURABLE, head + "- [ ] b two ⟦criterion abc⟧\n- [ ] t ⟦added⟧ ⟦criterion abc⟧\n"),
        "empty text": (0, NOT_DURABLE, head + "- [ ] b two ⟦criterion 2⟧\n- [ ]  ⟦added⟧ ⟦criterion 2⟧\n"),
        "newline": (0, NOT_DURABLE, head + "- [ ] b two ⟦criterion 2⟧\n- [ ] x\ny ⟦added⟧ ⟦criterion 2⟧\n"),
        "indented": (0, NOT_DURABLE, head + "  - [ ] b two ⟦criterion 4⟧\n- [ ] t ⟦added⟧ ⟦criterion 4⟧\n"),
    }


def test_main_over_budget_returns_1_silently_and_owes_every_text_under_the_last_owed_steps_heading(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
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
        return (code, captured.out, settled(captured.err), ledger.read_bytes() if ledger.exists() else None)

    cap_at(monkeypatch, "0")
    assert run("afterr", "b two", "t") == (
        2, "", "add-ledger-step.sh: position must be after, before or instead-of: afterr\n", None
    )

    ledger.write_bytes(LEDGER)
    cap_at(monkeypatch, "5")
    anchors = ("nothing", "⟦criterion", "*", "t[w]o")
    assert {anchor: run("after", anchor, "t") for anchor in anchors} == {
        anchor: (2, "", f"add-ledger-step.sh: anchor matches no single step: {anchor}\n", LEDGER)
        for anchor in anchors
    }

    budgets = ("", "x", "-1", "1.5")
    got = {}
    for budget in budgets:
        monkeypatch.setenv("VERI_STEP_GROWTH_PERCENT", budget)
        got[budget] = run("after", "b two", "t")
    assert got == {
        budget: (2, "", f"add-ledger-step.sh: VERI_STEP_GROWTH_PERCENT must be a whole number >= 0: {budget}\n", LEDGER)
        for budget in budgets
    }

    monkeypatch.setenv("VERI_STEP_GROWTH_PERCENT", "x")
    assert run("after", "nothing", "t") == (
        2, "", "add-ledger-step.sh: anchor matches no single step: nothing\n", LEDGER
    )

    monkeypatch.delenv("VERI_STEP_GROWTH_PERCENT")
    monkeypatch.setattr(PLAN, "steps", 10)
    four = "".join(f"- [ ] extra {n} ⟦added⟧ ⟦criterion 2⟧\n" for n in range(4))
    seed = (LEDGER.decode() + four).encode()
    ledger.write_bytes(seed)
    fifth = run("after", "c three", "fifth")
    sixth = run("after", "c three", "sixth")
    assert (fifth[:3], sixth[:3]) == ((0, "", NOT_DURABLE), (1, "", ""))
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
        cap_at(monkeypatch, budget)
        code = add_ledger_step.main([str(ledger), "after", "collapse to single hyphen", *texts])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, settled(captured.err), ledger.read_bytes().decode())
    anchor = "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    repairs = (
        "- [ ] fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n"
        "- [ ] mid-text: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧\n"
    )
    assert got == {
        "uncounted lines, one added text": (0, "", NOT_DURABLE, uncounted.replace(
            anchor,
            anchor
            + "- [ ] one more edge case ⟦added⟧ ⟦criterion 2⟧\n"
            + "- [ ] fix the CI failure: z.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧\n",
        )),
        "a pending added step spends the budget": (1, "", "", counted + "\n## Owed steps\n\n- one more edge case\n"),
        "repair texts at a budget of 0": (0, "", NOT_DURABLE, unadded + repairs),
    }
    records = importlib.import_module("veri.ledger").ledger_steps(ledger.read_bytes().decode())[-2:]
    assert [(state, kind, text) for _, state, kind, _, _, _, text in records] == [
        ("open", "step", "fix the CI failure: x.test.sh ⟦ci-repair⟧ ⟦criterion 2⟧"),
        ("open", "step", "mid-text: y.test.sh ⟦suite-repair⟧ ⟦criterion 2⟧"),
    ]


def test_main_reads_and_rewrites_the_ledger_as_bytes_line_by_line_in_place(tmp_path, monkeypatch, capsys, add_ledger_step):
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
        got[name] = (code, captured.out, settled(captured.err), ledger.read_bytes())
    step = "- [ ] t ⟦added⟧ ⟦criterion 1⟧\n".encode()
    assert got == {
        "anchor on an unterminated last line": (
            0, "", NOT_DURABLE, unterminated + b"\n" + "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n".encode()
        ),
        "insert before an unterminated last line": (
            0, "", NOT_DURABLE, unterminated.replace(
                "a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step
            ) + b"\n",
        ),
        "crlf": (
            0, "", NOT_DURABLE, crlf.replace("a one ⟦criterion 1⟧\r\n".encode(), "a one ⟦criterion 1⟧\r\n".encode() + step)
        ),
        "non-utf-8": (
            0, "", NOT_DURABLE, latin.replace("a one ⟦criterion 1⟧\n".encode(), "a one ⟦criterion 1⟧\n".encode() + step)
        ),
    }


def test_main_writes_a_non_utf_8_byte_of_a_text_back_unchanged_when_it_inserts_and_when_it_owes(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    text = b"t \xff".decode(errors="surrogateescape")
    got = {}
    for name, budget in (("inserted", "3"), ("owed", "0")):
        cap_at(monkeypatch, budget)
        ledger.write_bytes(LEDGER)
        code = add_ledger_step.main([str(ledger), "after", "b two", text])
        captured = capsys.readouterr()
        got[name] = (code, captured.out, settled(captured.err), ledger.read_bytes())
    assert got == {
        "inserted": (
            0, "", NOT_DURABLE, LEDGER.replace(
                "b two ⟦criterion 2⟧\n".encode(),
                "b two ⟦criterion 2⟧\n- [ ] t ".encode() + b"\xff" + " ⟦added⟧ ⟦criterion 2⟧\n".encode(),
            ),
        ),
        "owed": (1, "", "", LEDGER + b"\n## Owed steps\n\n- t \xff\n"),
    }


def test_main_returns_2_naming_the_anchor_for_a_missing_or_directory_ledger_and_raises_on_a_failed_write(tmp_path, monkeypatch, capsys, add_ledger_step):
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
        cap_at(monkeypatch, budget)
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
        cap_at(monkeypatch, budget)
        ledger.write_bytes(LEDGER)
        with monkeypatch.context() as swap:
            swap.setattr("os.replace", refuse_swap)
            with pytest.raises(OSError):
                add_ledger_step.main([str(ledger), "after", "b two", "t"])
        assert (ledger.read_bytes(), sorted(p.name for p in tmp_path.iterdir())) == (LEDGER, ["issue-42.md"])


def test_main_finds_a_last_step_without_a_trailing_newline_as_the_anchor_and_keeps_it_after_inserting_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER.removesuffix(b"\n"))

    code = add_ledger_step.main([str(ledger), "after", "c three", "t"])
    captured = capsys.readouterr()

    assert (code, settled(captured.err)) == (0, NOT_DURABLE)
    assert ledger.read_bytes().decode().split("\n")[4:6] == [
        "- [ ] c three ⟦criterion 3⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 3⟧",
    ]


def test_main_keeps_a_last_line_without_a_trailing_newline_after_inserting_beside_an_earlier_step_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER.removesuffix(b"\n"))

    code = add_ledger_step.main([str(ledger), "after", "a one", "t"])
    captured = capsys.readouterr()

    assert (code, settled(captured.err)) == (0, NOT_DURABLE)
    assert ledger.read_bytes().decode().split("\n")[2:6] == [
        "- [x] a one ⟦criterion 1⟧",
        "- [ ] t ⟦added⟧ ⟦criterion 1⟧",
        "- [ ] b two ⟦criterion 2⟧",
        "- [ ] c three ⟦criterion 3⟧",
    ]


def test_main_counts_a_last_added_step_without_a_trailing_newline_against_the_budget_and_owes_the_batch_817(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "1")
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
    cap_at(monkeypatch, "0")
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
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    seed = LEDGER + b"\n## Owed steps\n\n- old"
    ledger.write_bytes(seed)

    code = add_ledger_step.main([str(ledger), "after", "b two", "t", "u"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err) == (1, "", "")
    assert ledger.read_bytes() == seed + b"\n- t\n- u\n"


def test_main_owes_each_bullet_under_an_unterminated_last_owed_steps_heading_without_a_second_heading_1109(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
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
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--criterion", "3", str(ledger), "after", "b two", "t", "u"])
    assert (code, settled(capsys.readouterr().err), ledger.read_bytes().decode()) == (
        0,
        NOT_DURABLE,
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦added⟧ ⟦criterion 3⟧\n- [ ] u ⟦added⟧ ⟦criterion 3⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_without_criterion_tags_inserted_lines_with_the_anchor_criterion_and_an_untagged_anchor_yields_untagged_lines_1224(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    got = {}
    monkeypatch.setenv("VERI_STEP_GROWTH_PERCENT", "100")
    for name, seed in (("tagged", LEDGER), ("untagged", "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n".encode())):
        ledger.write_bytes(seed)
        code = add_ledger_step.main([str(ledger), "after", "b two", "t", "u"])
        got[name] = (code, settled(capsys.readouterr().err), ledger.read_bytes().decode())
    assert got == {
        "tagged": (
            0,
            NOT_DURABLE,
            "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
            "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n- [ ] u ⟦added⟧ ⟦criterion 2⟧\n- [ ] c three ⟦criterion 3⟧\n",
        ),
        "untagged": (
            0,
            NOT_DURABLE,
            "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n- [ ] t ⟦added⟧\n- [ ] u ⟦added⟧\n",
        ),
    }


def test_main_given_a_criterion_no_step_carries_tags_every_inserted_line_with_it_and_returns_0_1292(tmp_path, monkeypatch, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, settled(capsys.readouterr().err), ledger.read_bytes().decode()) == (
        0,
        NOT_DURABLE,
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦added⟧ ⟦criterion 7⟧\n- [ ] u ⟦added⟧ ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_refuses_a_criterion_that_is_not_a_whole_number_of_at_least_1_with_2_and_one_stderr_line_naming_it_writing_nothing_1292(tmp_path, monkeypatch, capsys, add_ledger_step):
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
        assert (argv, code, out, err.count("\n"), err.startswith("usage: add-ledger-step.sh [--planned] [--criterion <k>] <ledger-file> ")) == (argv, 2, "", 1, True)


def test_main_refusing_too_few_arguments_prints_a_usage_line_naming_planned_alongside_criterion_1579(capsys, add_ledger_step):
    code = add_ledger_step.main([])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "--planned" in err, "--criterion" in err) == (2, "", 1, True, True)


def test_main_planned_criterion_k_inserts_unmarked_steps_that_do_not_count_toward_a_zero_step_growth_and_files_nothing_owed_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, settled(capsys.readouterr().err), ledger.read_bytes().decode()) == (
        0,
        NOT_DURABLE,
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦criterion 7⟧\n- [ ] u ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_planned_without_criterion_or_with_a_criterion_a_step_already_serves_refuses_with_2_and_one_stderr_line_writing_nothing_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
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
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
    planned = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    after_planned = ledger.read_bytes()
    code = add_ledger_step.main(["--criterion", "7", str(ledger), "after", "b two", "u"])
    assert (planned, code, settled(capsys.readouterr().err), ledger.read_bytes()) == (
        0, 1, NOT_DURABLE, after_planned + "\n## Owed steps\n\n- u\n".encode()
    )


def test_main_planned_criterion_k_beyond_the_spec_files_checkboxes_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n- [x] one\n- [ ] two\n- [ ] three\n\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "5", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 5" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "- [x] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_unticked_in_the_spec_file_and_served_by_no_step_still_inserts_unmarked_steps_and_returns_0_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t", "u"])
    assert (code, settled(capsys.readouterr().err), ledger.read_bytes().decode()) == (
        0,
        NOT_DURABLE,
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
        "- [ ] t ⟦criterion 7⟧\n- [ ] u ⟦criterion 7⟧\n- [ ] c three ⟦criterion 3⟧\n",
    )


def test_main_planned_criterion_k_with_no_spec_file_beside_the_ledger_refuses_with_2_naming_that_file_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), str(tmp_path / "issue-42-spec.md") in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_with_a_directory_in_place_of_the_spec_file_refuses_with_2_naming_that_path_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").mkdir()
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), str(tmp_path / "issue-42-spec.md") in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_with_a_capital_x_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "- [X] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_planned_criterion_k_ticked_in_an_indented_box_in_the_spec_file_refuses_with_2_naming_k_writing_nothing_and_filing_no_owed_step_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    """A box ledger.STEP_RE counts as criterion k is ticked by the same pattern, indented or not."""
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    boxes = "".join(f"- [ ] c{n}\n" for n in range(1, 7)) + "  - [x] c7\n"
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + boxes + "\n## Blocked by\n")
    code = add_ledger_step.main(["--planned", "--criterion", "7", str(ledger), "after", "b two", "t"])
    out, err = capsys.readouterr()
    assert (code, out, err.count("\n"), "criterion 7 is already ticked" in err, ledger.read_bytes() == LEDGER) == (2, "", 1, True, True)


def test_main_accepts_criterion_k_before_planned_the_same_as_planned_before_criterion_k_1579(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "0")
    got = {}
    for name, flags in (("planned first", ["--planned", "--criterion", "7"]), ("criterion first", ["--criterion", "7", "--planned"])):
        ledger = tmp_path / name / "issue-42.md"
        ledger.parent.mkdir()
        ledger.write_bytes(LEDGER)
        (ledger.parent / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [x] c{n}\n" for n in range(1, 7)) + "- [ ] c7\n\n## Blocked by\n")
        code = add_ledger_step.main([*flags, str(ledger), "after", "b two", "t"])
        got[name] = (code, settled(capsys.readouterr().err), ledger.read_bytes())
    assert got["criterion first"] == got["planned first"] and got["planned first"][:2] == (0, NOT_DURABLE)



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


def test_main_still_refuses_a_second_suite_repair_while_the_one_this_run_inserted_is_pending_3420(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    before = (
        "# Plan for #42\n"
        "\n"
        "- [x] a one ⟦criterion 1⟧\n"
        "- [ ] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧\n"
        "- [ ] b two ⟦criterion 2⟧\n"
    ).encode()
    ledger.write_bytes(before)

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", before)
    assert "this run already inserted a suite-repair step" in err
    assert "fix the full-suite failure: first.test.sh" in err


def test_main_inserts_a_suite_repair_when_the_only_suite_repair_step_the_ledger_holds_is_a_retired_one_3420(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(
        (
            "# Plan for #42\n"
            "\n"
            "- [x] a one ⟦criterion 1⟧\n"
            "- [x] fix the full-suite failure: first.test.sh ⟦suite-repair⟧ ⟦criterion 1⟧ ⟂ retired\n"
            "- [ ] b two ⟦criterion 2⟧\n"
        ).encode()
    )

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧"],
    )

    assert (code, settled(err)) == (0, NOT_DURABLE)
    assert "- [ ] fix the full-suite failure: second.test.sh ⟦suite-repair⟧" in ledger.read_text()


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
        env={"VERI_STEP_GROWTH_PERCENT": "0"},
    )

    assert (code, out) == (1, "")
    assert ledger.read_bytes() == before + b"\n## Owed steps\n\n- explain why \xe2\x9f\xa6ci-repair\xe2\x9f\xa7 and \xe2\x9f\xa6suite-repair\xe2\x9f\xa7 end a repair step\n"


def test_main_inserts_a_suite_repair_when_the_only_earlier_step_this_run_merely_quotes_the_mark_in_its_prose_1613_and_3618_says_durable_on_stderr_not_stdout(tmp_path, monkeypatch, run_cli, add_ledger_step, fake_processes):
    monkeypatch.setattr(add_ledger_step.pid_file, "recorded_started", lambda tree: "1")
    monkeypatch.setattr(add_ledger_step.pid_file, "ancestors", lambda: set())
    fake_processes.answers(dict(PLAN_COMMIT, git=(0, "abc1234\n", "")))
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

    assert (code, out) == (0, "")
    assert err in ("", "add-ledger-step.sh: the added step is durable (committed in abc1234)\n")
    assert "durable" in err
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

    assert (code, settled(err)) == (0, NOT_DURABLE)
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
    "staying with its assertion unmodified ⟦replaces-case⟧"
)


def test_main_refuses_a_replaces_case_step_with_unreadable_case_names_1538(tmp_path, monkeypatch, capsys, add_ledger_step):
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
            )

            kinds = {record[6]: record[2] for record in ledger_steps(ledger.read_text())}
            added = [kinds[text] for text in kinds if text.startswith("check it")]
            assert (kind, where, code, added) == (kind, where, 0, [kind])


def test_main_counts_a_kind_marked_added_step_against_the_budget_and_owes_the_next_insertion_1614(tmp_path, run_cli, add_ledger_step):
    for kind in ("full-suite", "human-owed", "diff-checked"):
        ledger = tmp_path / f"issue-42-{kind}.md"
        ledger.write_bytes(LEDGER)
        env = {"VERI_STEP_GROWTH_PERCENT": "33"}

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
    cap_at(monkeypatch, "2")
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
    cap_at(monkeypatch, "2")
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


def test_main_refuses_a_kind_marked_text_at_the_growth_budget_counting_it_as_one_added_step_and_owes_it_issue_1631(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "2")
    ledger = tmp_path / "issue-42.md"
    steps = (
        "# Plan for #42\n\n"
        "- [ ] alpha\n"
        "- [ ] extra one ⟦added⟧ ⟦criterion 1⟧\n"
        "- [ ] extra two ⟦added⟧ ⟦criterion 1⟧\n"
    )
    ledger.write_bytes(steps.encode())

    code = add_ledger_step.main([str(ledger), "after", "alpha", "marked step ⟦diff-checked⟧"])
    capsys.readouterr()

    text = ledger.read_bytes().decode()
    assert (code, text.startswith(steps), text[len(steps):]) == (1, True, "\n## Owed steps\n\n- marked step ⟦diff-checked⟧\n")


def test_main_refuses_an_instead_of_over_an_added_anchor_with_more_texts_than_the_budget_allows_after_the_credit_and_owes_them_issue_1631(tmp_path, monkeypatch, capsys, add_ledger_step):
    cap_at(monkeypatch, "2")
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
    header = "\n".join(line for line in (SCRIPTS / "add-ledger-step.sh").read_text().split("\n") if line.startswith("#"))
    exit2 = header[header.index("# Exit:"):]
    planned = [line for line in header.split("\n") if "--planned" in line]

    assert (
        any("VERI_STEP_GROWTH_PERCENT" in line for line in planned),
        any("⟦added⟧" in line for line in planned),
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

    cap_at(monkeypatch, "5")
    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first", "second"])
    assert code == 0
    inserted = [line for line in ledger.read_text().split("\n") if "⟦added⟧" in line]
    recorded = [json.loads(raw) for raw in events.read_text().splitlines()] if events.exists() else []
    assert [(e["event"], e["actor"]) for e in recorded] == [("step-added", "add-ledger-step")] * 2
    assert [line in e.values() for e, line in zip(recorded, inserted, strict=True)] == [True, True]

    before = events.read_bytes()
    cap_at(monkeypatch, "2")
    assert run_cli(add_ledger_step, [str(ledger), "after", "b two", "third"])[0] == 1
    assert run_cli(add_ledger_step, [str(ledger), "sideways", "b two", "t"])[0] == 2
    assert events.read_bytes() == before


def test_main_writes_each_inserted_step_to_the_tracked_added_file_beside_the_ledger_on_exit_0_and_none_on_exit_1_or_2_2130(tmp_path, monkeypatch, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    added = tmp_path / "issue-42-added.md"
    ledger.write_bytes(LEDGER)

    cap_at(monkeypatch, "5")
    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "first", "second"])
    assert code == 0
    inserted = [line for line in ledger.read_text().split("\n") if "⟦added⟧" in line]
    assert len(inserted) == 2
    recorded = added.read_text() if added.exists() else ""
    assert [line in recorded.split("\n") for line in inserted] == [True, True]

    before = added.read_bytes()
    cap_at(monkeypatch, "2")
    assert run_cli(add_ledger_step, [str(ledger), "after", "b two", "third"])[0] == 1
    assert run_cli(add_ledger_step, [str(ledger), "sideways", "b two", "t"])[0] == 2
    assert added.read_bytes() == before


def test_main_writes_the_step_added_record_with_an_integer_ts_and_an_awake_reading_2265(tmp_path, monkeypatch, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    cap_at(monkeypatch, "5")

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
    cap_at(monkeypatch, "5")
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
    cap_at(monkeypatch, "5")
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


def test_4307_accepts_an_added_skill_edit_step_on_a_backticked_heading_unit_whose_unit_file_exists_inserting_it_marked_added(tmp_path, run_cli, add_ledger_step):
    heading = "Before the Red of a `⟦suite-repair⟧` step — is the suite still red?"
    unit = f"skills/foo/SKILL.md#{heading}"
    (tmp_path / "skills/foo").mkdir(parents=True)
    (tmp_path / "skills/foo/SKILL.md").write_text(f"#### {heading}\n\nThe widget is blue.\n")
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


def test_main_refuses_a_text_already_holding_a_criterion_tag_naming_it_and_inserting_none_of_the_batch_2713(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    tag = "⟦criterion 1⟧"

    for flags in ([], ["--criterion", "3"]):
        for texts in (["some step " + tag], ["fine step", "some step " + tag], ["some step " + tag, "fine step"]):
            code, out, err = run_cli(add_ledger_step, [*flags, str(ledger), "after", "b two", *texts])
            assert (flags, texts, code, out, tag in err, ledger.read_bytes()) == (flags, texts, 2, "", True, LEDGER)


def test_main_refuses_a_criterion_tagged_text_at_the_growth_budget_owing_nothing_2713(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    steps = (
        "# Plan for #42\n\n"
        "- [ ] alpha\n"
        "- [ ] extra one ⟦added⟧ ⟦criterion 1⟧\n"
        "- [ ] extra two ⟦added⟧ ⟦criterion 1⟧\n"
    ).encode()
    ledger.write_bytes(steps)

    code, out, err = run_cli(
        add_ledger_step, [str(ledger), "after", "alpha", "tagged step ⟦criterion 2⟧"]
    )

    assert (code, out, "⟦criterion 2⟧" in err, ledger.read_bytes()) == (2, "", True, steps)


def test_2749_a_growing_call_emits_a_plan_event_with_the_new_step_total_and_the_issue_from_the_file_name(tmp_path, run_cli, add_ledger_step):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-2749.md"
    ledger.write_bytes(LEDGER)

    code, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", "t"])

    events = [json.loads(row) for row in (tdd / "events.jsonl").read_text().splitlines()]
    plans = [(e["event"], e["issue"], e["steps"]) for e in events if e["event"] == "plan"]
    assert (code, plans) == (0, [("plan", "2749", "4")])


def test_2749_a_growing_call_given_a_relative_ledger_path_writes_the_plan_event_to_the_ledgers_own_events_file(tmp_path, monkeypatch, run_cli, add_ledger_step):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    (tdd / "issue-2749.md").write_bytes(LEDGER)
    monkeypatch.chdir(tdd)

    code, _, _ = run_cli(add_ledger_step, ["issue-2749.md", "after", "b two", "t"])

    path = tdd / "events.jsonl"
    events = [json.loads(row) for row in path.read_text().splitlines()] if path.exists() else []
    plans = [(e["event"], e["steps"]) for e in events if e["event"] == "plan"]
    assert (code, plans, (tdd / ".tdd").exists()) == (0, [("plan", "4")], False)


def test_2937_a_skill_edit_step_naming_no_backticked_unit_path_exits_2_with_one_stderr_line_naming_it_leaving_the_ledger(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### skills/vgroom/SKILL.md\n")

    try:
        code, out, err = run_cli(
            add_ledger_step,
            [str(ledger), "after", "b two", "⟦skill-edit⟧ regrade skills/vgroom/SKILL.md against A1"],
            cwd=tmp_path,
        )
    except TypeError as crash:
        pytest.fail(f"crashed with TypeError: {crash}")

    lines = err.splitlines()
    assert (code, out, len(lines), "backtick" in err, "TypeError" in err or "Traceback" in err, ledger.read_bytes()) == (2, "", 1, True, False, LEDGER), err


def test_3709_a_skill_edit_step_with_leading_whitespace_and_no_unit_is_refused_like_the_unspaced_one(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### skills/vgroom/SKILL.md\n")
    step = "⟦skill-edit⟧ regrade skills/vgroom/SKILL.md against A1"

    plain = run_cli(add_ledger_step, [str(ledger), "after", "b two", step], cwd=tmp_path)
    spaced = run_cli(add_ledger_step, [str(ledger), "after", "b two", "  \t" + step], cwd=tmp_path)

    assert (plain[0], plain[1], "backtick" in plain[2]) == (2, "", True), plain
    assert (spaced[0], spaced[1], "backtick" in spaced[2], ledger.read_bytes()) == (2, "", True, LEDGER), spaced


def test_3314_a_text_holding_the_refactor_pending_delimiter_exits_2_naming_it_leaving_the_ledger_byte_identical(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", "a ⟂ b"], cwd=tmp_path)

    assert (code, out, " ⟂ " in err, ledger.read_bytes()) == (2, "", True, LEDGER), err


def test_3314_a_batch_with_one_text_holding_the_refactor_pending_delimiter_exits_2_inserting_none_of_it(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    for texts in (["fine step", "a ⟂ b", "other step"], ["a ⟂ b", "fine step"], ["fine step", "a ⟂ b"]):
        code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", *texts], cwd=tmp_path)
        assert (texts, code, out, " ⟂ " in err, ledger.read_bytes()) == (texts, 2, "", True, LEDGER), err


def test_3314_texts_without_the_refactor_pending_delimiter_are_inserted_with_exit_0_each_marked_added_and_counted_by_ledger_growth(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    plan = tmp_path / "plan.md"
    ledger.write_bytes(LEDGER)
    plan.write_bytes(LEDGER)
    growth = importlib.import_module("veri.ledger_growth")

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", "do X", "do Y⟂Z"], cwd=tmp_path)
    lines = ledger.read_bytes().decode().split("\n")
    within = run_cli(growth, [str(plan), str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "50"}, cwd=tmp_path)
    beyond = run_cli(growth, [str(plan), str(ledger)], env={"VERI_STEP_GROWTH_PERCENT": "33"}, cwd=tmp_path)

    assert (code, lines[4:6], within[0], beyond[0]) == (
        0, ["- [ ] do X ⟦added⟧ ⟦criterion 2⟧", "- [ ] do Y⟂Z ⟦added⟧ ⟦criterion 2⟧"], 0, 1), (err, within, beyond)


def test_main_refuses_a_diff_checked_step_that_would_carry_no_criterion_naming_the_tag_and_still_accepts_one_with_it_3438(tmp_path, monkeypatch, capsys, add_ledger_step):
    from veri.ledger import ledger_steps

    ledger = tmp_path / "issue-42.md"
    untagged = "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n".encode()
    ledger.write_bytes(untagged)
    code = add_ledger_step.main([str(ledger), "after", "b two", "x ⟦diff-checked⟧"])
    refused = (code, capsys.readouterr().err, ledger.read_bytes() == untagged)
    assert (refused[0], "criterion" in refused[1], refused[2]) == (2, True, True)

    ledger.write_bytes(LEDGER)
    code = add_ledger_step.main([str(ledger), "after", "b two", "x ⟦diff-checked⟧"])
    capsys.readouterr()
    record = [r for r in ledger_steps(ledger.read_text()) if "x ⟦diff-checked⟧" in r[6]]
    assert (code, [(r[2], r[4], r[5]) for r in record]) == (0, [("diff-checked", "1", "2")])


def test_main_adds_a_step_that_only_mentions_the_skill_edit_mark_in_its_prose_as_a_plain_step_3544(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### .tdd/issue-1.md\n")
    text = "document the ⟦skill-edit⟧ marker in `.tdd/issue-1.md`"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text], cwd=tmp_path)

    added = [line for line in ledger.read_text().split("\n") if line.startswith("- [ ] " + text)]
    assert (code, settled(err), added) == (0, NOT_DURABLE, ["- [ ] " + text + " ⟦added⟧ ⟦criterion 2⟧"])


def test_main_refuses_a_trailing_skill_edit_step_whose_unit_file_is_missing_naming_the_unit_without_a_traceback_3544(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### .tdd/issue-1.md\n")
    text = "regrade `.tdd/issue-1.md` ⟦skill-edit⟧"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text], cwd=tmp_path)

    assert (code, ".tdd/issue-1.md" in err, "Traceback" in err or "FileNotFoundError" in err, ledger.read_bytes()) == (2, True, False, LEDGER), err


def test_main_refuses_a_skill_edit_step_whose_only_backticked_token_is_not_a_path_saying_no_unit_path_was_found_leaving_the_ledger_3564(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### skills/tdd/SCRIPTS.md\n")
    text = "⟦skill-edit⟧ regrade `parked` rows in skills/tdd/SCRIPTS.md"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text], cwd=tmp_path)

    assert (code, out, "no unit path" in err, ledger.read_bytes()) == (2, "", True, LEDGER), err


def test_main_takes_a_bare_md_file_after_a_non_path_backticked_token_as_the_unit_naming_it_and_not_the_token_3564(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### README.md\n")
    text = "⟦skill-edit⟧ regrade `parked` rows in `README.md`"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text], cwd=tmp_path)

    assert (code, "README.md: the unit file does not exist" in err, "no unit path" in err, "parked:" in err, ledger.read_bytes()) == (2, True, False, False, LEDGER), err


def test_main_takes_the_first_path_shaped_backticked_token_as_the_unit_skipping_an_earlier_non_path_one_3564(tmp_path, run_cli, add_ledger_step):
    unit = "skills/tdd/SCRIPTS.md"
    (tmp_path / "skills/tdd").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    (tmp_path / "skills/tdd/REQUIREMENTS.md").write_text(
        f"## {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n")
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text(
        f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is blue. | because |\n"
        "| A2 | The widget is round. | shape |\n")
    text = f"⟦skill-edit⟧ regrade `parked` rows in `{unit}`"
    only_non_path = "⟦skill-edit⟧ regrade `parked` rows in the scripts doc"

    code, _, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text], cwd=tmp_path)
    inserted = [line for line in ledger.read_text().splitlines() if f"`{unit}`" in line]
    refused, _, _ = run_cli(add_ledger_step, [str(ledger), "after", "b two", only_non_path], cwd=tmp_path)

    assert (code, len(inserted), "⟦added⟧" in inserted[0] if inserted else None, refused) == (0, 1, True, 2), err


def test_main_refuses_a_restating_skill_edit_step_naming_the_path_shaped_unit_and_never_an_earlier_non_path_token_3564(tmp_path, run_cli, add_ledger_step):
    unit = "skills/tdd/SCRIPTS.md"
    (tmp_path / "skills/tdd").mkdir(parents=True)
    (tmp_path / unit).write_text("The widget is blue.\n")
    rows = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n"
    (tmp_path / "skills/tdd/REQUIREMENTS.md").write_text(f"## {unit}\n\n{rows}")
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text(f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n\n{rows}")

    code, out, err = run_cli(
        add_ledger_step, [str(ledger), "after", "b two", f"⟦skill-edit⟧ regrade `parked` rows in `{unit}`"], cwd=tmp_path)

    assert (code, out, f"{unit}: the issue's Requirements restate" in err, "parked" in err, ledger.read_bytes()) == (2, "", True, False, LEDGER), err


def test_main_refuses_a_skill_edit_step_whose_path_shaped_unit_file_is_missing_naming_the_unit_and_never_an_earlier_non_path_token_3564(tmp_path, run_cli, add_ledger_step):
    unit = "skills/tdd/SCRIPTS.md"
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text(f"## Problem\n\nText.\n\n## Requirements\n\n### {unit}\n")

    code, out, err = run_cli(
        add_ledger_step, [str(ledger), "after", "b two", f"⟦skill-edit⟧ regrade `parked` rows in `{unit}`"], cwd=tmp_path)

    assert (code, out, f"{unit}: the unit file does not exist" in err, "parked" in err, ledger.read_bytes()) == (2, "", True, False, LEDGER), err


def test_main_takes_a_slash_only_backticked_token_after_a_non_path_one_as_the_unit_naming_it_3564(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "l.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "l-spec.md").write_text("## Problem\n\nText.\n\n## Requirements\n\n### scripts/foo.sh\n")

    code, out, err = run_cli(
        add_ledger_step, [str(ledger), "after", "b two", "⟦skill-edit⟧ regrade `parked` rows in `scripts/foo.sh`"], cwd=tmp_path)

    assert (code, out, "scripts/foo.sh: the unit file does not exist" in err, "parked" in err, "no unit path" in err, ledger.read_bytes()) == (2, "", True, False, False, LEDGER), err


def test_main_3618_stderr_states_the_uncommitted_step_is_not_durable_when_no_conductor_is_live(tmp_path, monkeypatch, run_cli, add_ledger_step):
    monkeypatch.setattr(add_ledger_step.pid_file, "recorded_started", lambda tree: None)
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", "d four"])

    assert (code, out) == (0, "")
    assert b"- [ ] d four" in ledger.read_bytes()
    assert "not durable" in err.lower(), err


def test_spec_criteria_reads_the_section_as_tick_issue_criterion_does_last_heading_unfenced_crlf_tolerant(tmp_path, add_ledger_step):
    fence = "`" * 3
    ledger = tmp_path / "issue-42.md"
    spec = tmp_path / "issue-42-spec.md"
    got = {}
    for name, text in {
        "crlf": "## Acceptance criteria\r\n\r\n- [x] c1\r\n- [ ] c2\r\n",
        "fenced": f"## Acceptance criteria\n\n- [x] c1\n{fence}\n- [ ] fake\n{fence}\n- [ ] c2\n",
        "second heading": "## Acceptance criteria\n\n- [ ] old\n\n## Notes\n\n## Acceptance criteria\n\n- [x] c1\n- [ ] c2\n",
        "h1 ends": "## Acceptance criteria\n\n- [x] c1\n- [ ] c2\n\n# Other\n\n- [ ] stray\n",
    }.items():
        spec.write_text(text)
        got[name] = add_ledger_step.spec_criteria(str(ledger))
    assert got == {name: (2, {"1"}) for name in ("crlf", "fenced", "second heading", "h1 ends")}


def test_add_inserts_each_text_at_the_anchor_through_typed_parameters_like_main(tmp_path, monkeypatch, capsys, add_ledger_step):
    via_main, via_add = tmp_path / "main" / "issue-42.md", tmp_path / "add" / "issue-42.md"
    for ledger in (via_main, via_add):
        ledger.parent.mkdir()
        ledger.write_bytes(LEDGER)

    code_main = add_ledger_step.main([str(via_main), "before", "b two", "t1", "t2"])
    out_main = capsys.readouterr()
    code_add = add_ledger_step.add(str(via_add), "before", "b two", ["t1", "t2"])
    out_add = capsys.readouterr()

    assert (code_main, code_add) == (0, 0)
    assert via_add.read_bytes() == via_main.read_bytes()
    assert via_add.read_bytes().decode().split("\n")[3:6] == [
        "- [ ] t1 ⟦added⟧ ⟦criterion 2⟧",
        "- [ ] t2 ⟦added⟧ ⟦criterion 2⟧",
        "- [ ] b two ⟦criterion 2⟧",
    ]
    assert out_add == out_main
    events = [json.loads(line)["event"] for line in (via_add.parent / "events.jsonl").read_text().splitlines()]
    assert events.count("step-added") == 2


def test_add_with_criterion_and_planned_tags_the_step_and_leaves_the_growth_budget_alone(tmp_path, monkeypatch, add_ledger_step):
    cap_at(monkeypatch, "0")
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "issue-42-spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- [ ] c{n}\n" for n in range(1, 5)))

    code = add_ledger_step.add(str(ledger), "after", "c three", ["new"], criterion="4", planned=True)

    assert code == 0
    assert ledger.read_bytes().decode().split("\n")[5] == "- [ ] new ⟦criterion 4⟧"


def test_add_refuses_an_anchor_that_matches_no_single_step_with_exit_2_and_changes_nothing(tmp_path, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)

    code = add_ledger_step.add(str(ledger), "after", "zzz", ["t"])

    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", "add-ledger-step.sh: anchor matches no single step: zzz\n")
    assert ledger.read_bytes() == LEDGER


def test_add_refuses_an_empty_path_position_or_anchor_with_the_usage_line_and_exit_2(tmp_path, capsys, add_ledger_step):
    for args in (("", "after", "b two"), (str(tmp_path / "l.md"), "", "b two"), (str(tmp_path / "l.md"), "after", "")):
        code = add_ledger_step.add(*args, ["t"])
        captured = capsys.readouterr()
        assert (args, code, captured.out, captured.err) == (args, 2, "", USAGE)


LINT_LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] a one ⟦criterion 1⟧\n"
    "- [x] make `ruff check .` pass: E501 line too long ⟦diff-checked⟧ ⟦lint-repair⟧ ⟦added⟧ ⟦criterion 1⟧\n"
    "- [x] b two ⟦criterion 2⟧\n"
).encode()


def test_4123_a_second_lint_repair_in_one_run_exits_1_naming_the_first_and_leaves_the_ledger(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LINT_LEDGER)

    code, out, err = run_cli(
        add_ledger_step,
        [str(ledger), "after", "b two", "make `ruff check .` pass: F401 unused import ⟦diff-checked⟧ ⟦lint-repair⟧"],
    )

    assert (code, out, ledger.read_bytes()) == (1, "", LINT_LEDGER)
    assert "this run already inserted a lint-repair step" in err and "E501 line too long" in err


def test_4123_a_lint_repair_is_inserted_beside_a_suite_repair_this_run_and_a_suite_repair_beside_a_lint_repair(tmp_path, run_cli, add_ledger_step):
    for earlier, text in (("fix the full-suite failure: first.test.sh ⟦suite-repair⟧", "make `ruff check .` pass: F401 ⟦diff-checked⟧ ⟦lint-repair⟧"),
                          ("make `ruff check .` pass: E501 ⟦diff-checked⟧ ⟦lint-repair⟧ ⟦added⟧", "fix the full-suite failure: second.test.sh ⟦suite-repair⟧")):
        ledger = tmp_path / "issue-42.md"
        ledger.write_bytes(("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
                            f"- [x] {earlier} ⟦criterion 1⟧\n- [x] b two ⟦criterion 2⟧\n").encode())

        code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "b two", text])

        assert (code, settled(err)) == (0, NOT_DURABLE), (earlier, err)
        assert text in ledger.read_text()


def test_4123_a_lint_repair_step_carries_added_and_is_owed_once_the_growth_budget_is_spent(tmp_path, monkeypatch, run_cli, add_ledger_step):
    text = "make `ruff check .` pass: E501 line too long ⟦diff-checked⟧ ⟦lint-repair⟧"
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    cap_at(monkeypatch, "1")

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "a one", text])

    assert (code, settled(err)) == (0, NOT_DURABLE)
    assert f"- [ ] {text} ⟦added⟧ ⟦criterion 1⟧\n" in ledger.read_text()

    spent = LEDGER + "- [x] split off ⟦added⟧ ⟦criterion 3⟧\n".encode()
    ledger.write_bytes(spent)
    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "a one", text])

    assert (code, out) == (1, "")
    assert ledger.read_bytes() == spent + f"\n## Owed steps\n\n- {text}\n".encode()


def test_4547_instead_of_on_the_open_step_leaves_no_verdict_exit_file_of_the_replaced_step(tmp_path, add_ledger_step):
    """#4547: a `.tdd/verdict-<phase>.exit` names no step, so the one the replaced open step's verifier left would be
    read as the replacement's verdict."""
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    for phase in ("red", "green"):
        (tmp_path / ("verdict-%s.exit" % phase)).write_text("1\n")

    assert add_ledger_step.main([str(ledger), "instead-of", "b two", "b two"]) == 0

    assert sorted(p.name for p in tmp_path.glob("verdict-*.exit")) == []


def test_4547_instead_of_on_a_step_after_the_open_one_leaves_the_open_steps_verdict_exit_file(tmp_path, add_ledger_step):
    """#4547: the exit file is the open step's, so replacing a later step must not erase its verdict."""
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    (tmp_path / "verdict-green.exit").write_text("1\n")

    assert add_ledger_step.main([str(ledger), "instead-of", "c three", "c three"]) == 0

    assert (tmp_path / "verdict-green.exit").read_text() == "1\n"


def test_4547_instead_of_leaves_the_rejected_wait_record_naming_the_open_step_when_it_replaces_a_later_one(
        tmp_path, add_ledger_step):
    """#4547: only the replaced step's `<stage>-rejected` record goes; the open step's own record stays."""
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    record = tmp_path / "issue-42-green-half-rejected-wait"
    record.write_text('{"conductor": null, "at": "verdict-green", "values": {}, "step": "b two ⟦criterion 2⟧"}')

    assert add_ledger_step.main([str(ledger), "instead-of", "c three", "c three"]) == 0

    assert record.exists()


def test_4709_main_adds_a_step_only_quoting_diff_checked_in_its_prose_after_an_untagged_anchor(tmp_path, capsys, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two\n".encode())

    code = add_ledger_step.main([str(ledger), "after", "b two", "document the `⟦diff-checked⟧` mark in `a.md`"])

    err = capsys.readouterr().err
    assert (code, "- [ ] document the `⟦diff-checked⟧` mark in `a.md` ⟦added⟧" in ledger.read_text()) == (0, True), err


def test_main_before_inserts_an_untagged_diff_checked_text_with_the_anchor_criterion_and_refuses_a_tagged_one_4728(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    text = "make `test_split_rounds_half_cents` observe the rounding ⟦diff-checked⟧"

    refused = run_cli(add_ledger_step, [str(ledger), "before", "c three", text + " ⟦criterion 3⟧"])
    refused = (refused[0], refused[1], "⟦criterion 3⟧" in refused[2], ledger.read_bytes() == LEDGER)
    code, out, _ = run_cli(add_ledger_step, [str(ledger), "before", "c three", text])

    assert (refused, code, out, ledger.read_text().split("\n")[4:6]) == (
        (2, "", True, True),
        0,
        "",
        ["- [ ] " + text + " ⟦added⟧ ⟦criterion 3⟧", "- [ ] c three ⟦criterion 3⟧"],
    )


def test_4760_main_appends_a_quality_repair_step_with_no_added(tmp_path, run_cli, add_ledger_step):
    ledger = tmp_path / "issue-42.md"
    ledger.write_bytes(LEDGER)
    text = "fix POSSIBLE-BUG: test_a.py::test_b expects 1, code yields 2 ⟦diff-checked⟧ ⟦quality-repair⟧"

    code, out, err = run_cli(add_ledger_step, [str(ledger), "after", "c three", text])

    assert (code, out, settled(err), ledger.read_bytes().decode()) == (
        0, "", NOT_DURABLE, LEDGER.decode() + f"- [ ] {text} ⟦criterion 3⟧\n")
