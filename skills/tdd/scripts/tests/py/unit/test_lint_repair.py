"""In-process cases for veri/lint_repair.py, the module lint-repair.sh is a shim over (#4123, PRD 032.10 LR1)."""
import importlib

import pytest


@pytest.fixture
def lint_repair(monkeypatch, tmp_path):
    module = importlib.import_module("veri.lint_repair")
    home = tmp_path / "home" / "laneuser"
    home.mkdir(parents=True)
    monkeypatch.setattr(module.run_records, "_sensitive", lambda run: (
        (("<repo>", [str(tmp_path / "repo"), "/srv/main-clone"]), ("<tmp>", ["/scratch/tmp"]), ("~", [str(home)])),
        {"lanehost"}, {"laneuser"}))
    return module


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "CLAUDE.md").write_text("veri: lint: `ruff check .`\n")
    monkeypatch.chdir(root)
    return root


def test_4123_step_prints_the_repair_step_naming_the_declared_command_and_the_first_finding_line(repo, run_cli, lint_repair):
    code, out, err = run_cli(lint_repair, ["step"], stdin="\n\nsrc/a.py:3:1: E501 line too long\nsrc/b.py:1:1: F401\n")

    assert (code, err) == (0, "")
    assert out == "make `ruff check .` pass: src/a.py:3:1: E501 line too long ⟦diff-checked⟧ ⟦lint-repair⟧\n"


def test_4123_step_redacts_every_local_path_the_host_and_the_account_from_the_finding(repo, tmp_path, run_cli, lint_repair):
    for finding, want in (
            (f"{repo}/src/a.py:3:1: E501", "<repo>/src/a.py:3:1: E501"),
            ("/srv/main-clone/src/a.py:3: E501", "<repo>/src/a.py:3: E501"),
            ("/scratch/tmp/x.py:1: F401", "<tmp>/x.py:1: F401"),
            (f"{tmp_path}/home/laneuser/a.py:1: E1", "~/a.py:1: E1"),
            ("lanehost: laneuser broke src/a.py", "<host>: <user> broke src/a.py")):
        code, out, err = run_cli(lint_repair, ["step"], stdin=finding + "\n")

        assert (code, out) == (0, f"make `ruff check .` pass: {want} ⟦diff-checked⟧ ⟦lint-repair⟧\n"), finding


def test_4123_step_caps_the_finding_at_200_characters_never_splitting_one(repo, run_cli, lint_repair):
    code, out, err = run_cli(lint_repair, ["step"], stdin="é" * 300 + "\n")

    assert (code, out) == (0, "make `ruff check .` pass: " + "é" * 200 + " ⟦diff-checked⟧ ⟦lint-repair⟧\n")


def test_4123_step_with_no_output_says_so_and_with_no_declared_lint_command_exits_3(repo, run_cli, lint_repair):
    assert run_cli(lint_repair, ["step"], stdin="\n \n") == (
        0, "make `ruff check .` pass: the command printed nothing ⟦diff-checked⟧ ⟦lint-repair⟧\n", "")
    (repo / "CLAUDE.md").write_text("veri: all tests: make test\n")
    assert run_cli(lint_repair, ["step"], stdin="E501\n") == (3, "", "")


def test_4123_bad_arguments_exit_2_with_the_usage_line(repo, run_cli, lint_repair):
    for argv in ([], ["steps"], ["step", "extra"]):
        assert run_cli(lint_repair, argv, stdin="E501\n") == (2, "", "usage: lint-repair.sh step < <lint-output>\n"), argv
