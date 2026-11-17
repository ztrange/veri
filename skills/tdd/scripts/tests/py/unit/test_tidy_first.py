"""In-process cases for veri/tidy_first.py, the module tidy-first.sh is a shim over (#4118, PRD 032.4 TI2)."""
import importlib

import pytest


@pytest.fixture
def tidy_first(tmp_path, monkeypatch):
    module = importlib.import_module("veri.tidy_first")
    run_records = importlib.import_module("veri.run_records")
    monkeypatch.setattr(run_records, "_sensitive", lambda run: (
        (("<repo>", [str(tmp_path)]), ("<tmp>", ["/scratch/tmp"]), ("~", ["/home/laneuser"])), {"lanehost"}, {"laneuser"}))
    return module


@pytest.fixture
def tree(tmp_path, monkeypatch):
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "route.py").write_text("def answer():\n    pass\n")
    monkeypatch.chdir(tmp_path)
    return tmp_path


REPORT = ("I read the step. Answering the route is one small change once the parsing moves out.\n"
          "TIDY_FIRST: Extract Function | lib/route.py::answer | the parse and the answer are tangled\n")


def test_4118_a_catalogue_refactoring_on_an_existing_file_exits_0_printing_the_diff_checked_step(tree, run_cli, tidy_first):
    code, out, err = run_cli(tidy_first, [], stdin=REPORT)

    assert (code, err) == (0, "")
    assert out == ("apply Extract Function to `lib/route.py::answer`, so the step after it is one small change;"
                   " the step changes no behaviour and no test file ⟦diff-checked⟧\n")


def test_4118_the_step_carries_none_of_the_leafs_why_since_its_text_reaches_the_blind_diff_verifier(tree, run_cli, tidy_first):
    code, out, err = run_cli(tidy_first, [], stdin=REPORT)

    assert (code, "tangled" in out) == (0, False)


def test_4118_a_report_with_no_tidy_first_line_exits_3_printing_nothing(tree, run_cli, tidy_first):
    for report in ("", "IMPL_PATH: lib/route.py\nSUITE: GREEN — 3 passed\n", " TIDY_FIRST: Extract Function | lib/route.py::answer | x\n",
                   "tidy_first: Extract Function | lib/route.py::answer | x\n"):
        assert run_cli(tidy_first, [], stdin=report) == (3, "", ""), report


@pytest.mark.parametrize("line, why", [
    ("TIDY_FIRST: Extract Function | lib/route.py::answer | a\nTIDY_FIRST: Move Function | lib/route.py::answer | b",
     "two or more TIDY_FIRST: lines"),
    ("TIDY_FIRST: Make It Nicer | lib/route.py::answer | a", "names a refactoring SMELLS.md does not list"),
    ("TIDY_FIRST: extract function | lib/route.py::answer | a", "names a refactoring SMELLS.md does not list"),
    ("TIDY_FIRST: Smell | lib/route.py::answer | a", "names a refactoring SMELLS.md does not list"),
    ("TIDY_FIRST: Extract Function | lib/gone.py::answer | a", "names a file absent from the working tree"),
    ("TIDY_FIRST: Extract Function | lib::answer | a", "names a file absent from the working tree"),
    ("TIDY_FIRST: Extract Function | /etc/hosts::answer | a", "names an absolute path, not one relative to the working tree"),
    ("TIDY_FIRST: Extract Function | ../outside.py::answer | a", "names a file absent from the working tree"),
    ("TIDY_FIRST: Extract Function | lib/route.py | a", "is not <refactoring> | <file>::<symbol> | <why>"),
    ("TIDY_FIRST: Extract Function | lib/route.py::an swer | a", "is not <refactoring> | <file>::<symbol> | <why>"),
    ("TIDY_FIRST: Extract Function | lib/route.py::answer", "is not <refactoring> | <file>::<symbol> | <why>"),
])
def test_4118_a_wrong_answer_exits_1_stdout_empty_and_one_stderr_line_naming_the_offending_line(tree, run_cli, tidy_first, line, why):
    (tree.parent / "outside.py").write_text("x = 1\n")
    code, out, err = run_cli(tidy_first, [], stdin="reasoning\n" + line + "\n")

    offending = line.split("\n")[-1]
    assert (code, out, err) == (1, "", f"tidy-first.sh: {why}: {offending}\n")


def test_4118_an_absolute_path_inside_the_working_tree_exits_1_and_never_reaches_the_step(tree, run_cli, tidy_first):
    line = f"TIDY_FIRST: Extract Function | {tree}/lib/route.py::answer | a"

    assert run_cli(tidy_first, [], stdin=line + "\n") == (
        1, "", "tidy-first.sh: names an absolute path, not one relative to the working tree:"
               " TIDY_FIRST: Extract Function | <repo>/lib/route.py::answer | a\n")


def test_4118_a_wrong_answers_stderr_line_carries_no_local_path_host_or_account(tree, run_cli, tidy_first):
    line = "TIDY_FIRST: Make It Nicer | lib/route.py::answer | laneuser on lanehost saw /home/laneuser/notes and /scratch/tmp/x"

    code, out, err = run_cli(tidy_first, [], stdin=line + "\n")

    assert (code, out) == (1, "")
    assert err == ("tidy-first.sh: names a refactoring SMELLS.md does not list: TIDY_FIRST: Make It Nicer |"
                   " lib/route.py::answer | <user> on <host> saw ~/notes and <tmp>/x\n")


def test_4118_an_unreadable_catalogue_exits_2_printing_nothing_on_stdout(tree, monkeypatch, run_cli, tidy_first):
    monkeypatch.setattr(tidy_first, "SMELLS", str(tree / "no-such-SMELLS.md"))

    code, out, err = run_cli(tidy_first, [], stdin=REPORT)

    assert (code, out, err.startswith("tidy-first.sh: cannot read the smell catalogue")) == (2, "", True)


def test_4118_an_argument_is_refused_with_exit_2_and_the_usage_line(tree, run_cli, tidy_first):
    assert run_cli(tidy_first, ["extra"], stdin=REPORT) == (
        2, "", "tidy-first.sh: unexpected argument 'extra'\nusage: tidy-first.sh < <green-report>\n")


def test_4118_every_refactoring_the_catalogue_lists_is_accepted_and_a_smell_name_is_not(tree, run_cli, tidy_first):
    names = tidy_first.catalogue_refactorings()

    assert {"Extract Function", "Remove Dead Code", "Replace Nested Conditional with Guard Clauses"} <= names
    assert "Duplicated Code" not in names and "Refactorings that answer it" not in names
    for name in sorted(names):
        code, out, _ = run_cli(tidy_first, [], stdin=f"TIDY_FIRST: {name} | lib/route.py::answer | w\n")
        assert (code, out.startswith(f"apply {name} to ")) == (0, True), name
