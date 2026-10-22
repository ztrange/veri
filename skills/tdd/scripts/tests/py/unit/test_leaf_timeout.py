"""In-process cases for veri/leaf_timeout.py, the module leaf-timeout.sh is a shim over."""
import importlib
import importlib.util
import os
import pathlib
import shutil

import pytest

from conftest import SCRIPTS

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


@pytest.fixture
def leaf_timeout(monkeypatch):
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    return importlib.import_module("veri.leaf_timeout")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _worktree(root):
    (root / ".git").mkdir(parents=True)
    return root


def test_main_refuses_a_baseline_of_ten_with_its_diagnostic_and_usage_and_returns_2(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    code = leaf_timeout.main(["ten"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "leaf-timeout: <baseline-seconds> must be a whole number >= 0: ten\n" + USAGE + "\n")


def test_main_with_veri_timeout_unset_derives_max_900_six_times_the_baseline_and_refuses_a_malformed_one(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for argv in (["0"], ["5"], ["150"], ["151"], ["200"], ["abc"], ["-1"], ["1.5"], []):
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((argv, code, out, err))
    refusal = "leaf-timeout: <baseline-seconds> must be a whole number >= 0: {}\n" + USAGE + "\n"
    assert seen == [
        (["0"], 0, "900\n", ""),
        (["5"], 0, "900\n", ""),
        (["150"], 0, "900\n", ""),
        (["151"], 0, "906\n", ""),
        (["200"], 0, "1200\n", ""),
        (["abc"], 2, "", refusal.format("abc")),
        (["-1"], 2, "", refusal.format("-1")),
        (["1.5"], 2, "", refusal.format("1.5")),
        ([], 2, "", refusal.format("")),
    ]


def test_main_prints_an_explicit_veri_timeout_as_given_whatever_the_baseline_and_refuses_one_not_a_whole_number_of_at_least_1(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, baseline in (("900", "200"), ("1800", "5"), ("1", "200"), ("0", "200"), ("abc", "200"), ("-1", "200"), ("1.5", "200")):
        monkeypatch.setenv("VERI_TIMEOUT", timeout)
        code = leaf_timeout.main([baseline])
        out, err = capsys.readouterr()
        seen.append((timeout, baseline, code, out, err))
    refusal = "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {}\n"
    assert seen == [
        ("900", "200", 0, "900\n", ""),
        ("1800", "5", 0, "1800\n", ""),
        ("1", "200", 0, "1\n", ""),
        ("0", "200", 2, "", refusal.format("0")),
        ("abc", "200", 2, "", refusal.format("abc")),
        ("-1", "200", 2, "", refusal.format("-1")),
        ("1.5", "200", 2, "", refusal.format("1.5")),
    ]


def test_main_with_refactor_multiplies_the_derived_timeout_by_max_1_veri_refactor_budget_and_prints_an_explicit_veri_timeout_unmultiplied(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, budget, baseline in (
            (None, "5", "200"), (None, "1", "200"), (None, "0", "200"), (None, "3", "5"), (None, None, "5"),
            ("900", "5", "200"), ("1800", "5", "200")):
        for name, value in (("VERI_TIMEOUT", timeout), ("VERI_REFACTOR_BUDGET", budget)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        code = leaf_timeout.main([baseline, "refactor"])
        out, err = capsys.readouterr()
        seen.append((timeout, budget, baseline, code, out, err))
    assert seen == [
        (None, "5", "200", 0, "6000\n", ""),
        (None, "1", "200", 0, "1200\n", ""),
        (None, "0", "200", 0, "1200\n", ""),
        (None, "3", "5", 0, "2700\n", ""),
        (None, None, "5", 0, "4500\n", ""),
        ("900", "5", "200", 0, "900\n", ""),
        ("1800", "5", "200", 0, "1800\n", ""),
    ]


def test_main_with_full_derives_from_the_full_tier_prints_an_explicit_veri_timeout_as_given_and_refuses_a_malformed_full_tier(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, argv in (
            (None, ["5", "--full", "600"]),
            ("900", ["5", "--full", "600"]), ("7200", ["5", "--full", "20"]), ("1", ["150", "--full", "151"]),
            (None, ["5", "--full", "abc"]), (None, ["5", "--full", "-1"]), (None, ["5", "--full", "1.5"]),
            (None, ["5", "--full"])):
        if timeout is None:
            monkeypatch.delenv("VERI_TIMEOUT", raising=False)
        else:
            monkeypatch.setenv("VERI_TIMEOUT", timeout)
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((timeout, argv, code, out, err))
    refusal = "leaf-timeout: <full-seconds> must be a whole number >= 0: {}\n" + USAGE + "\n"
    assert seen == [
        (None, ["5", "--full", "600"], 0, "3600\n", ""),
        ("900", ["5", "--full", "600"], 0, "900\n", ""),
        ("7200", ["5", "--full", "20"], 0, "7200\n", ""),
        ("1", ["150", "--full", "151"], 0, "1\n", ""),
        (None, ["5", "--full", "abc"], 2, "", refusal.format("abc")),
        (None, ["5", "--full", "-1"], 2, "", refusal.format("-1")),
        (None, ["5", "--full", "1.5"], 2, "", refusal.format("1.5")),
        (None, ["5", "--full"], 2, "", refusal.format("")),
    ]


def test_main_keeps_leaf_timeout_sh_argument_and_environment_quirks(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, budget, argv in (
            ("007", None, ["abc"]), ("007", None, []), ("", None, ["200"]), ("abc", None, []),
            (None, None, ["5", "--full"]), (None, None, ["200", "foo"]), (None, "5", ["200", "refactor", "x"]),
            (None, "", ["200", "refactor"]), (None, "-3", ["200", "refactor"])):
        for name, value in (("VERI_TIMEOUT", timeout), ("VERI_REFACTOR_BUDGET", budget)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((timeout, budget, argv, code, out, err))
    assert seen == [
        ("007", None, ["abc"], 0, "7\n", ""),
        ("007", None, [], 0, "7\n", ""),
        ("", None, ["200"], 0, "1200\n", ""),
        ("abc", None, [], 2, "", "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: abc\n"),
        (None, None, ["5", "--full"], 2, "", "leaf-timeout: <full-seconds> must be a whole number >= 0: \n" + USAGE + "\n"),
        (None, None, ["200", "foo"], 0, "1200\n", ""),
        (None, "5", ["200", "refactor", "x"], 0, "6000\n", ""),
        (None, "", ["200", "refactor"], 0, "6000\n", ""),
        (None, "-3", ["200", "refactor"], 2, "", "leaf-timeout: VERI_REFACTOR_BUDGET must be a whole number >= 0: -3\n"),
    ]


def test_main_reproduces_leaf_timeout_sh_bash_arithmetic_in_stdout_and_return_code_reading_leading_zeros_as_decimal_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for budget, argv in (
            (None, ["0200"]), (None, ["08"]), (None, ["5", "--full", "0200"]), ("abc", ["200", "refactor"]),
            ("010", ["200", "refactor"]),
            (None, ["1537228672809129302"]), (None, ["768614336404564651", "refactor"]),
            (None, ["9223372036854775808"])):
        if budget is None:
            monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
        else:
            monkeypatch.setenv("VERI_REFACTOR_BUDGET", budget)
        code = leaf_timeout.main(argv)
        out, _ = capsys.readouterr()
        seen.append((budget, argv, code, out))
    assert seen == [
        (None, ["0200"], 0, "1200\n"),
        (None, ["08"], 0, "900\n"),
        (None, ["5", "--full", "0200"], 0, "1200\n"),
        ("abc", ["200", "refactor"], 2, ""),
        ("010", ["200", "refactor"], 0, "12000\n"),
        (None, ["1537228672809129302"], 0, "9223372036854775812\n"),
        (None, ["768614336404564651", "refactor"], 0, "23058430092136939530\n"),
        (None, ["9223372036854775808"], 0, "55340232221128654848\n"),
    ]


def test_main_with_refactor_refuses_a_veri_refactor_budget_not_a_non_negative_whole_number_with_2_naming_it_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for budget in ("abc", "-3", "1.5"):
        monkeypatch.setenv("VERI_REFACTOR_BUDGET", budget)
        code = leaf_timeout.main(["200", "refactor"])
        out, err = capsys.readouterr()
        seen.append((budget, code, out, "VERI_REFACTOR_BUDGET" in err))
    assert seen == [
        ("abc", 2, "", True),
        ("-3", 2, "", True),
        ("1.5", 2, "", True),
    ]


def test_main_prints_a_veri_timeout_given_with_leading_zeros_as_its_decimal_value_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.setenv("VERI_TIMEOUT", "010")
    code = leaf_timeout.main(["200"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "10\n", "")


def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_prints_and_exits_as_in_place_for_a_good_and_a_bad_baseline(
        tmp_path, monkeypatch, run_cli, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    inplace = _load(SCRIPTS / "veri" / "leaf_timeout.py", "leaf_timeout_inplace")
    linked = _load(tmp_path / "linked-skill" / "scripts" / "veri" / "leaf_timeout.py", "leaf_timeout_linked")
    answers = {baseline: (run_cli(inplace, [baseline], cwd=SCRIPTS), run_cli(linked, [baseline], cwd=elsewhere))
               for baseline in ("200", "ten")}
    refusal = "leaf-timeout: <baseline-seconds> must be a whole number >= 0: ten\n" + USAGE + "\n"
    assert answers == {
        "200": ((0, "1200\n", ""), (0, "1200\n", "")),
        "ten": ((2, "", refusal), (2, "", refusal)),
    }


def test_cli_with_veri_issue_954_records_its_settled_1200_in_the_worktrees_tdd_and_a_second_settling_leaves_it_in_place_issue_954(
        tmp_path, monkeypatch, run_cli, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    work = _worktree(tmp_path / "work")
    (work / ".tdd").mkdir()
    record = work / ".tdd" / "issue-954-timeout"
    run_cli(leaf_timeout, ["10", "--full", "200"], env={"VERI_ISSUE": "954"}, cwd=work)
    first = record.read_text() if record.exists() else "<no record>"
    run_cli(leaf_timeout, ["10", "--full", "300"], env={"VERI_ISSUE": "954"}, cwd=work)
    second = record.read_text() if record.exists() else "<no record>"
    assert (first, second) == ("1200\n", "1200\n")


def test_cli_with_veri_issue_unset_prints_1200_and_records_no_settled_timeout_under_tdd_issue_954(
        tmp_path, monkeypatch, run_cli, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    work = _worktree(tmp_path / "work")
    _, out, _ = run_cli(leaf_timeout, ["10", "--full", "200"], cwd=work)
    assert (out, sorted(p.name for p in work.glob(".tdd/issue-*timeout"))) == ("1200\n", [])


def test_cli_with_veri_issue_954_run_from_a_subdirectory_records_its_settled_1200_at_the_worktree_roots_tdd_issue_954(
        tmp_path, monkeypatch, run_cli, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    work = _worktree(tmp_path / "work")
    (work / "sub" / "dir").mkdir(parents=True)
    run_cli(leaf_timeout, ["10", "--full", "200"], env={"VERI_ISSUE": "954"}, cwd=work / "sub" / "dir")
    record = work / ".tdd" / "issue-954-timeout"
    assert (record.read_text() if record.exists() else "<no record>") == "1200\n"


def test_cli_run_from_the_scripts_directory_of_a_decoy_repository_holding_a_copy_records_no_timeout_outside_the_scratch_repository_issue_1158(
        tmp_path, monkeypatch, run_cli):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    repo = _worktree(tmp_path / "repo")
    decoy = _worktree(tmp_path / "decoy")
    mutant = decoy / "skills" / "tdd" / "scripts"
    (mutant / "veri").mkdir(parents=True)
    shutil.copy(SCRIPTS / "veri" / "leaf_timeout.py", mutant / "veri" / "leaf_timeout.py")
    copy = _load(mutant / "veri" / "leaf_timeout.py", "leaf_timeout_decoy")
    code, _, _ = run_cli(copy, ["10", "--full", "200"], env={"VERI_ISSUE": "954"}, cwd=mutant)
    outside = sorted(str(p.relative_to(tmp_path)) for root in (decoy, mutant) for p in root.glob(".tdd/issue-*timeout"))
    pinned = repo / ".tdd" / "issue-954-timeout"
    settled = pinned.read_text() if pinned.exists() else None
    assert (outside, settled) == ([], "1200\n" if code == 0 else None)


def test_a_symlink_beside_no_scripts_still_finds_the_real_scripts_directory(tmp_path, monkeypatch, leaf_timeout):
    real = pathlib.Path(leaf_timeout.__file__).resolve()
    farm = tmp_path.resolve() / "farm" / "veri"
    farm.mkdir(parents=True)
    os.symlink(real, farm / "leaf_timeout.py")
    loaded = _load(farm / "leaf_timeout.py", "symlinked_leaf_timeout")
    monkeypatch.chdir(real.parent.parent)

    assert loaded.inside_own_scripts() is True
