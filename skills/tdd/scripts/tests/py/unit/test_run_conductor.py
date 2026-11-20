"""In-process cases for veri/run_conductor.py, the module run-conductor.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys
import pytest


SCRIPTS = pathlib.Path(__file__).resolve().parents[3]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


@pytest.fixture(autouse=True)
def issue_body_fetch_answers_empty(request, monkeypatch):
    """The pre-launch issue-body gh call answered with an empty body, so the row-ID check finds no rows."""
    if "reaches_issue_body_boundary" in request.fixturenames:
        return
    import github
    real = github.gh_issue_view

    def view(number, field):
        return "" if field == "body" else real(number, field)

    monkeypatch.setattr(github, "gh_issue_view", view)


@pytest.fixture(autouse=True)
def state_label_clearing_answers_removed(request, monkeypatch):
    """The launch's gh calls taking bailed and pr-ready off the issue answered as removed."""
    if "reaches_state_label_boundary" in request.fixturenames:
        return
    import github
    monkeypatch.setattr(github, "gh_issue_remove_label", lambda number, label: None)


def past_the_guards(monkeypatch):
    """The bash and Python floors met, and claude named fake-claude."""
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    monkeypatch.setenv("CLAUDE_BIN", "fake-claude")


def test_main_with_no_issue_returns_2_with_the_usage_line_alone_and_starts_no_process(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_BASH_MAJOR", "5")
    monkeypatch.setenv("VERI_PYTHON_VERSION", "3.12.0")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code = run_conductor.main([])

    captured = capfdbinary.readouterr()
    assert (code, captured.out, captured.err, calls) == (2, b"", b"usage: run-conductor.sh <issue>\n", [])


def test_main_refuses_on_bash_before_the_python_floor_and_on_the_floor_before_the_usage_line_with_the_run_conductor_prefix_on_a_module_parsing_as_python_3_9(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    import ast
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_VENV", str(tmp_path / "no-venv"))
    fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")
    answers = []
    for major, python in (("3", "3.12.0"), ("3", "3.11.9"), ("5", "3.11.9")):
        monkeypatch.setenv("VERI_BASH_MAJOR", major)
        monkeypatch.setenv("VERI_PYTHON_VERSION", python)
        code = run_conductor.main([])
        captured = capfdbinary.readouterr()
        answers.append((code, captured.out, [line.split(b";")[0] for line in captured.err.splitlines()]))
    module = SCRIPTS / "veri" / "run_conductor.py"
    tree = ast.parse(module.read_text())
    imported = [alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names]
    sources = [module] + [SCRIPTS / "veri" / (name + ".py") for name in imported
                          if (SCRIPTS / "veri" / (name + ".py")).exists()]
    unparsable = []
    for source in sources:
        try:
            ast.parse(source.read_text(), feature_version=(3, 9))
        except SyntaxError as error:
            unparsable.append((source.name, str(error)))
    assert (answers, "launch_floor" in imported, unparsable) == ([
        (2, b"", [b"run-conductor: veri needs bash 5 or newer"]),
        (2, b"", [b"run-conductor: veri needs bash 5 or newer"]),
        (2, b"", [b"run-conductor: veri needs Python 3.12 or newer"]),
    ], True, [])


def test_cli_a_revise_budget_that_is_not_a_whole_number_exits_2_with_one_stderr_line_naming_it_before_any_process_starts_2705(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("REVISE_BUDGET", "three")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    lines = stderr.splitlines()
    assert (code, len(lines), "REVISE_BUDGET" in stderr, calls) == (2, 1, True, []), stderr


def test_cli_a_revise_budget_that_is_not_a_whole_number_refuses_before_the_bash_version_probe_with_veri_bash_major_unset_2705(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.delenv("VERI_BASH_MAJOR", raising=False)
    monkeypatch.setenv("REVISE_BUDGET", "three")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "REVISE_BUDGET" in stderr, calls) == (2, True, []), stderr


def test_cli_a_skip_verify_naming_plan_exits_2_naming_plan_on_stderr_before_any_process_starts(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_SKIP_VERIFY", "plan")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "plan" in stderr, calls) == (2, True, ["ps -o lstart= -p %d" % os.getpid()]), stderr


def test_cli_a_skip_verify_naming_branch_is_not_refused_as_a_phase_that_cannot_be_skipped_while_plan_still_is(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")
    refusals = {}

    for word in ("branch", "plan"):
        monkeypatch.setenv("VERI_SKIP_VERIFY", word)
        try:
            _, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)
        except BaseException as error:
            stderr = "raised %r" % (error,)
        refusals[word] = "cannot be skipped" in stderr

    assert refusals == {"branch": False, "plan": True}


def test_cli_a_skip_verify_naming_surround_exits_2_naming_surround_on_stderr_before_any_process_starts_4107(

        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_SKIP_VERIFY", "refactor,surround")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "'surround'" in stderr, calls) == (2, True, ["ps -o lstart= -p %d" % os.getpid()]), stderr


def test_cli_a_skip_verify_naming_a_word_no_phase_has_exits_2_naming_it_on_stderr_before_any_process_starts(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    monkeypatch.setenv("VERI_SKIP_VERIFY", "lint")
    calls = fake_processes()
    run_conductor = importlib.import_module("veri.run_conductor")

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, "'lint'" in stderr, calls) == (2, True, ["ps -o lstart= -p %d" % os.getpid()]), stderr


def test_cli_a_claim_whose_ps_gives_no_start_time_writes_the_pid_alone_on_one_line_to_conductor_pid_3996(
        tmp_path, monkeypatch, run_cli, fake_processes):
    past_the_guards(monkeypatch)
    fake_processes.answers({"ps -o lstart= -p %d" % os.getpid(): (0, "\n", "")}, exact=True)
    run_conductor = importlib.import_module("veri.run_conductor")
    claimed = []

    def read_the_claim(argv, *_):
        claimed.append(pathlib.Path(run_conductor.pid_file_path(argv[0])).read_bytes())
        return 0

    monkeypatch.setattr(run_conductor, "preflight_and_launch", read_the_claim)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, claimed) == (0, [b"%d\n" % os.getpid()]), stderr


@pytest.mark.parametrize("ending", [0, 1, 2, 3, "raises"])
def test_main_ending_by_any_exit_code_or_an_exception_removes_its_own_claim_and_the_directories_it_made_keeping_one_that_existed_4304(
        tmp_path, monkeypatch, run_cli, fake_processes, ending):
    past_the_guards(monkeypatch)
    fake_processes.answers({"ps -o lstart= -p %d" % os.getpid(): (0, "Tue Oct 27 13:40:12 2026\n", "")}, exact=True)
    run_conductor = importlib.import_module("veri.run_conductor")
    (tmp_path / ".tdd").mkdir()
    claimed = []

    def ending_the_run(argv, *_):
        claimed.append(pathlib.Path(run_conductor.pid_file_path(argv[0])).is_file())
        if ending == "raises":
            raise RuntimeError("preflight broke")
        return ending

    monkeypatch.setattr(run_conductor, "preflight_and_launch", ending_the_run)

    code, _, stderr = run_cli(run_conductor, ["4242"], cwd=tmp_path)

    assert (code, claimed, (tmp_path / ".tdd").is_dir(), (tmp_path / ".tdd" / "wt").exists()) == (
        2 if ending == "raises" else ending, [True], True, False), stderr


def test_prompt_with_revise_budget_unset_holds_no_line_naming_a_revise_budget_value_2705(tmp_path, monkeypatch):
    base = tmp_path / "s"
    base.mkdir()
    (base / "SKILL.md").write_text("# skill\n")
    monkeypatch.delenv("REVISE_BUDGET", raising=False)
    run_conductor = importlib.import_module("veri.run_conductor")

    text = run_conductor.prompt(str(base), "4242", None).decode()

    named = [line for line in text.splitlines() if "revise" in line.lower() and not line.startswith("Base directory")]
    assert named == [], text


def test_prompt_with_revise_budget_set_holds_one_line_naming_it_and_its_value_2705(tmp_path, monkeypatch):
    base = tmp_path / "s"
    base.mkdir()
    (base / "SKILL.md").write_text("# skill\n")
    monkeypatch.setenv("REVISE_BUDGET", "3")
    run_conductor = importlib.import_module("veri.run_conductor")

    text = run_conductor.prompt(str(base), "4242", None).decode()

    named = [line for line in text.splitlines() if "REVISE_BUDGET" in line]
    assert len(named) == 1 and "3" in named[0], text


def test_run_conductor_imports_no_leg_module_and_reads_the_directory_the_leg_pins_from_veri_4051():
    """A run must not import test plumbing (PRD 025.16, PL3): the free-space check's pinned directory comes from
    veri/leg_tmpdir.py, the module the pytest leg pins TMPDIR from, never from the leg itself."""
    import ast
    tree = ast.parse((SCRIPTS / "veri" / "run_conductor.py").read_text())
    leg_modules = {"pytest_leg", "network_guard", "small_case_guard", "serial_seen", "private_tmp_path"}
    named = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    imported = {alias.name.split(".")[-1] for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names} | {(node.module or "").split(".")[-1] for node in ast.walk(tree)
                                            if isinstance(node, ast.ImportFrom)}
    leg_tmpdir = importlib.import_module("veri.leg_tmpdir")
    run_conductor = importlib.import_module("veri.run_conductor")

    assert (sorted(leg_modules & (named | imported)), run_conductor.pinned_tmpdir()) == ([], leg_tmpdir.PINNED_TMPDIR)


REAL_RUN, REAL_POPEN = subprocess.run, subprocess.Popen
