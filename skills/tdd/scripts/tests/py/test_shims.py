"""The one check that every top-level skills/tdd/scripts/*.sh is the canonical shim over a module under veri/."""
import importlib
import os
import platform
import re
import shutil
import subprocess
import sys

import pytest

from conftest import FLOOR_SOURCE, INTERPRETER_VENV, SCRIPTS, VENV_PREFIX, shim_problems

EXEMPT = {
    "build-develop-prompt.sh": "a spelling difference; canonicalising it is a change of its own",
    "build-verify-prompt.sh": "a spelling difference; canonicalising it is a change of its own",
    "run-leaf.sh": "the locale preamble must act before the interpreter starts, so it cannot move into the module",
    "run-verdict.sh": "the locale preamble must act before the interpreter starts, so it cannot move into the module",
    "stop-run.sh": "records the caller's directory before anything can change it",
}


def shim(path, *lines):
    path.write_text("#!/bin/sh\n# %s — a shim.\n%s\n" % (path.name, "\n".join(lines)))


def test_shim_problems_names_each_script_with_logic_in_it_or_a_missing_module_and_passes_a_canonical_shim(tmp_path):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "logic.sh", 'export EXP_SHIM_WORD=1', 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "orphaned.sh", 'exec python3 "$(dirname "$0")/veri/gone.py" "$@"')
    (tmp_path / "bash.sh").write_text('#!/bin/bash\nexec python3 "$(dirname "$0")/veri/kept.py" "$@"\n')

    problems = shim_problems(tmp_path)

    assert [line.split(":")[0] for line in problems] == ["bash.sh", "logic.sh", "orphaned.sh"]
    assert "not the canonical shim" in problems[0] and "not the canonical shim" in problems[1]
    assert "veri/gone.py" in problems[2] and "does not exist" in problems[2]


@pytest.mark.tree_audit("every scripts/*.sh against the shim exemption table")
def test_every_real_script_is_the_canonical_shim_or_a_listed_exemption():
    assert shim_problems(SCRIPTS, EXEMPT) == []


def test_the_exemption_table_lists_the_six_non_canonical_shims_with_a_reason_each_and_a_stale_row_fails_naming_the_script(tmp_path):
    assert len(EXEMPT) == 5 and all(reason.strip() for reason in EXEMPT.values())

    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "preamble.sh", 'export EXP_SHIM_WORD=1', 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')

    problems = shim_problems(tmp_path, {"canonical.sh": "a reason", "preamble.sh": "a reason", "gone.sh": "a reason"})

    assert sorted(line.split(":")[0] for line in problems) == ["canonical.sh", "gone.sh"]
    assert all("stale exemption" in line for line in problems)


def test_shim_problems_names_the_shim_that_feeds_python3_a_heredoc_or_a_dash_c_string_and_passes_the_canonical_one(tmp_path):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "heredoc.sh", "python3 - <<'PY'", "print('hi')", "PY")
    shim(tmp_path / "dashc.sh", "python3 -c 'print(1)'")

    problems = shim_problems(tmp_path)

    assert [line.split(":")[0] for line in problems] == ["dashc.sh", "heredoc.sh"]
    assert all("not the canonical shim" in line for line in problems)


def test_shim_problems_names_the_shim_that_hands_python3_a_gh_json_document_as_an_argument_and_passes_the_canonical_one(tmp_path):
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "kept.py").write_text("")
    shim(tmp_path / "canonical.sh", 'exec python3 "$(dirname "$0")/veri/kept.py" "$@"')
    shim(tmp_path / "argv.sh", 'issue_json="$(gh issue view 7 --json body)"', 'python3 "$(dirname "$0")/veri/kept.py" "$issue_json"')

    problems = shim_problems(tmp_path)

    assert [line.split(":")[0] for line in problems] == ["argv.sh"]
    assert "not the canonical shim" in problems[0]


@pytest.mark.process("leaf-role.sh run through a symlink to the skills directory")
def test_a_shim_run_through_a_symlink_to_the_skills_directory_from_another_cwd_gives_its_modules_exit_code_and_stdout(
        run_cli, tmp_path):
    (tmp_path / "skills").symlink_to(SCRIPTS.parents[1], target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    ran = subprocess.run([str(tmp_path / "skills" / "tdd" / "scripts" / "leaf-role.sh"), "verify-green-2"],
                         cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL, capture_output=True, text=True)
    code, out, _ = run_cli(importlib.import_module("veri.leaf_role"), ["verify-green-2"])

    assert (ran.returncode, ran.stdout) == (code, out) == (0, "VERI_ACTOR=verifier VERI_PHASE=green VERI_ATTEMPT=2\n")


def test_entry_bypass_problems_names_the_module_whose_main_block_exits_bare_as_module_and_line_and_passes_one_calling_entry_run(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "bare.sh", 'exec python3 "$(dirname "$0")/veri/bare.py" "$@"')
    shim(tmp_path / "wrapped.sh", 'exec python3 "$(dirname "$0")/veri/wrapped.py" "$@"')
    (tmp_path / "veri" / "bare.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n")
    (tmp_path / "veri" / "wrapped.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["bare.py:8"]


def test_entry_bypass_problems_ignores_the_one_line_pycache_prefix_main_guard_and_still_names_the_bare_block_after_it_2405(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    prefix = 'if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")\n'
    (tmp_path / "veri").mkdir()
    shim(tmp_path / "bare.sh", 'exec python3 "$(dirname "$0")/veri/bare.py" "$@"')
    shim(tmp_path / "wrapped.sh", 'exec python3 "$(dirname "$0")/veri/wrapped.py" "$@"')
    (tmp_path / "veri" / "bare.py").write_text(
        '"""doc."""\n' + prefix + "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n")
    (tmp_path / "veri" / "wrapped.py").write_text(
        '"""doc."""\n' + prefix + "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["bare.py:10"]


def test_entry_bypass_problems_names_the_module_whose_single_quoted_main_test_block_exits_bare_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "quoted.sh", 'exec python3 "$(dirname "$0")/veri/quoted.py" "$@"')
    (tmp_path / "veri" / "quoted.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == '__main__':\n    sys.exit(main(sys.argv[1:]))\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["quoted.py:8"]


def test_entry_bypass_problems_names_the_module_whose_only_entry_run_in_its_main_block_is_a_comment_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "commented.sh", 'exec python3 "$(dirname "$0")/veri/commented.py" "$@"')
    (tmp_path / "veri" / "commented.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    # entry.run(main)\n    sys.exit(main(sys.argv[1:]))\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["commented.py:8"]


def test_entry_bypass_problems_names_the_module_whose_only_entry_run_is_in_a_function_defined_after_its_main_block_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "late.sh", 'exec python3 "$(dirname "$0")/veri/late.py" "$@"')
    (tmp_path / "veri" / "late.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n\n\ndef later():\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["late.py:8"]


def test_entry_bypass_problems_names_the_module_whose_only_entry_run_is_a_trailing_comment_on_its_bare_exit_as_module_and_line(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "trailing.sh", 'exec python3 "$(dirname "$0")/veri/trailing.py" "$@"')
    (tmp_path / "veri" / "trailing.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))  # entry.run(main, sys.argv[1:])\n")

    problems = entry_bypass_problems(tmp_path)

    assert [line.split(" ")[0] for line in problems] == ["trailing.py:8"]


def test_entry_bypass_problems_reports_a_problem_for_a_scripts_tree_holding_no_shim(tmp_path):
    """Its subject is source text: a planted scripts tree with no shim in it, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    (tmp_path / "plain.txt").write_text("not a shim\n")

    problems = entry_bypass_problems(tmp_path)

    assert problems


def test_entry_bypass_problems_names_the_planted_bare_module_as_module_and_line_leaves_the_entry_run_one_alone_and_passes_once_the_offender_is_removed(tmp_path):
    """Its subject is source text: planted shims and module files, read as text and never run."""
    from conftest import entry_bypass_problems

    (tmp_path / "veri").mkdir()
    shim(tmp_path / "probe-bare.sh", 'exec python3 "$(dirname "$0")/veri/probe_bare.py" "$@"')
    shim(tmp_path / "probe-entry.sh", 'exec python3 "$(dirname "$0")/veri/probe_entry.py" "$@"')
    (tmp_path / "veri" / "probe_bare.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    sys.exit(main(sys.argv[1:]))\n")
    (tmp_path / "veri" / "probe_entry.py").write_text(
        "import sys\n\n\ndef main(argv):\n    return 0\n\n\nif __name__ == \"__main__\":\n    import entry\n    entry.run(main, sys.argv[1:])\n")

    planted = entry_bypass_problems(tmp_path)
    (tmp_path / "probe-bare.sh").unlink()
    (tmp_path / "veri" / "probe_bare.py").unlink()
    removed = entry_bypass_problems(tmp_path)

    assert ([line.split(" ")[0] for line in planted], removed) == (["probe_bare.py:8"], [])


@pytest.mark.tree_audit("every scripts/*.sh and the module each execs, read as text")
def test_every_module_a_shim_execs_goes_through_the_shared_entry_point():
    """Its subject is source text: the real scripts tree, read as text and never run."""
    from conftest import entry_bypass_problems

    assert entry_bypass_problems(SCRIPTS) == []


def plant_into_stop_run_copy(tmp_path, planted):
    from conftest import shim_source_problems

    original = (SCRIPTS / "stop-run.sh").read_text()
    (tmp_path / "stop-run.sh").write_text(original)
    unplanted = shim_source_problems(tmp_path)
    (tmp_path / "stop-run.sh").write_text(original + planted + "\n")
    return unplanted, shim_source_problems(tmp_path), original


@pytest.mark.parametrize("planted", [
    "python3 - <<'PY'\nprint('hi')\nPY",
    "python3 -c 'print(1)'",
    "python3 -I -c 'print(1)'",
    "gh issue view 7 --json body",
    'issue_json="$(gh api repos/o/r/issues/7)"\npython3 "$(dirname "$0")/veri/stop_run.py" "$issue_json"',
])
def test_shim_source_problems_names_stop_run_and_line_for_each_violation_planted_into_a_copy_and_passes_the_unplanted_copy(tmp_path, planted):
    """Its subject is source text: a copy of the real stop-run.sh with a violation planted in it, read as text and never run."""
    unplanted, problems, original = plant_into_stop_run_copy(tmp_path, planted)

    assert unplanted == []
    assert [line.split(" ")[0] for line in problems][:1] == ["stop-run.sh:%d" % (original.count("\n") + 1)]


@pytest.mark.parametrize("planted", [
    "gh issue view 7",
    "gh pr list",
    "gh repo view",
    "gh auth status",
])
def test_shim_source_problems_names_stop_run_and_line_for_each_graphql_gh_call_planted_into_a_copy_and_passes_the_unplanted_copy(tmp_path, planted):
    """Its subject is source text: a copy of the real stop-run.sh with a gh call planted in it, read as text and never run."""
    unplanted, problems, original = plant_into_stop_run_copy(tmp_path, planted)

    assert unplanted == []
    assert [line.split(" ")[0] for line in problems] == ["stop-run.sh:%d" % (original.count("\n") + 1)]


def test_shim_source_problems_names_stop_run_and_line_of_the_python3_call_handed_a_gh_json_document_planted_into_a_copy_and_passes_the_unplanted_copy(tmp_path):
    """Its subject is source text: a copy of the real stop-run.sh with a gh JSON document handed to python3 as an argument, read as text and never run."""
    planted = 'issue_json="$(gh_json issue_view 7)"\npython3 "$(dirname "$0")/veri/stop_run.py" "$issue_json"'
    unplanted, problems, original = plant_into_stop_run_copy(tmp_path, planted)

    assert unplanted == []
    assert [line.split(" ")[0] for line in problems] == ["stop-run.sh:%d" % (original.count("\n") + 2)]


@pytest.mark.parametrize("assigned", [
    'issue_json="$(cat "$VERI_GH_JSON/issue.json")"',
    'if ! issue_json="$(gh_json issue_view 7)"; then exit 2; fi',
    '! issue_json="$(gh_json issue_view 7)" || exit 2',
])
def test_shim_source_problems_names_the_python3_call_handed_a_fixture_sourced_or_if_bang_assigned_gh_json_document_planted_into_a_copy(tmp_path, assigned):
    """Its subject is source text: a copy of the real stop-run.sh with a gh JSON document handed to python3 as an argument, read as text and never run."""
    planted = assigned + '\npython3 "$(dirname "$0")/veri/stop_run.py" "$issue_json"'
    unplanted, problems, original = plant_into_stop_run_copy(tmp_path, planted)

    assert unplanted == []
    assert [line.split(" ")[0] for line in problems] == ["stop-run.sh:%d" % (original.count("\n") + 2)]


def test_shim_source_problems_names_a_lib_script_handing_python3_a_gh_json_document_planted_into_a_copy(tmp_path):
    """Its subject is source text: a copy of the real lib/watch.sh with a gh JSON document handed to python3 as an argument, read as text and never run."""
    from conftest import shim_source_problems

    original = (SCRIPTS / "lib" / "watch.sh").read_text()
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "watch.sh").write_text(original)
    unplanted = shim_source_problems(tmp_path)
    (tmp_path / "lib" / "watch.sh").write_text(
        original + 'issue_json="$(gh api repos/o/r/issues/7)"\npython3 "$VERI_SCRIPTS/veri/stop_run.py" "$issue_json"\n')

    assert unplanted == []
    assert [line.split(" ")[0] for line in shim_source_problems(tmp_path)] == ["lib/watch.sh:%d" % (original.count("\n") + 2)]


@pytest.mark.tree_audit("every scripts/*.sh, the six exempt shims included, read as text")
def test_the_every_shim_guard_finds_no_offender_among_the_real_scripts_including_the_exempt_ones():
    """Its subject is source text: the real scripts tree, read as text and never run."""
    from conftest import shim_source_problems

    assert (SCRIPTS / "stop-run.sh").is_file()
    assert shim_source_problems(SCRIPTS) == []


def python3_script(path, runs_real):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\nexec "%s" "$@"\n' % sys.executable if runs_real else "#!/bin/sh\nexit 9\n")
    path.chmod(0o755)


def run_leaf_role(tmp_path, path_python_runs, venv_python_runs=None, venv_under_home=False):
    """leaf-role.sh develop-red on a fixed PATH whose first python3 is real or a stub exiting 9, beside a venv
    under VERI_VENV (or, VERI_VENV unset, under a scratch HOME) whose bin/python3 is real, a stub, or absent (None)."""
    python3_script(tmp_path / "path" / "python3", path_python_runs)
    home = tmp_path / "home"
    venv = home / ".veri-tools" / "venv" if venv_under_home else tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    if venv_python_runs is not None:
        python3_script(venv / "bin" / "python3", venv_python_runs)
    env = {"PATH": "%s:/usr/bin:/bin:/usr/local/bin" % (tmp_path / "path"), "HOME": str(home)}
    if not venv_under_home:
        env["VERI_VENV"] = str(venv)

    result = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)
    return result.returncode, result.stdout, result.stderr


@pytest.mark.process("leaf-role.sh started with VERI_VENV naming a directory that has no bin/python3")
def test_issue_2106_shim_with_a_venv_lacking_python3_runs_its_module_on_the_python3_on_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("leaf-role.sh started with a fixed PATH whose first python3 is a stub exiting 9")
def test_issue_2106_shim_runs_its_module_on_the_venv_python3_not_the_stub_python3_first_on_a_fixed_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=False, venv_python_runs=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("leaf-role.sh started with VERI_VENV unset, a scratch HOME holding the venv and a stub python3 exiting 9 on PATH")
def test_issue_2106_shim_with_veri_venv_unset_finds_the_venv_python3_under_home_not_on_path(tmp_path):
    assert run_leaf_role(tmp_path, path_python_runs=False, venv_python_runs=True, venv_under_home=True) == (
        0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


@pytest.mark.process("the canonical shim preamble run by sh on the process suites' fixed PATH and scratch HOME,"
                     " with conftest's INTERPRETER_VENV as VERI_VENV")
def test_issue_2106_interpreter_venv_gives_a_shim_on_a_fixed_path_and_scratch_home_a_python3_at_the_3_12_floor(tmp_path):
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n%s\nexec "$py" "$(dirname "$0")/probe.py"\n' % "\n".join(VENV_PREFIX))
    shim.chmod(0o755)
    (tmp_path / "probe.py").write_text("import sys\nprint('%d.%d' % sys.version_info[:2])\n")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV}

    ran = subprocess.run([str(shim)], capture_output=True, text=True, env=env)

    assert tuple(int(part) for part in ran.stdout.split(".")) >= (3, 12), (ran.stdout, ran.stderr)


@pytest.mark.process("the floor-checking canonical shim started with a venv python3 stub reporting 3.9 and a real python3 on PATH")
def test_issue_2106_shim_runs_its_module_on_the_path_python3_when_the_venv_python3_reports_3_9(tmp_path):
    (tmp_path / "lib").symlink_to(SCRIPTS / "lib", target_is_directory=True)
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py" "$@"\n')
    shim.chmod(0o755)
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "probe.py").write_text("print('probe ran')\n")
    python3_script(tmp_path / "path" / "python3", True)
    venv_python = tmp_path / "venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text('#!/bin/sh\n[ "$1" = --version ] && { echo "Python 3.9.6"; exit 0; }\nexit 9\n')
    venv_python.chmod(0o755)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(shim)], capture_output=True, text=True, env=env)

    assert (ran.returncode, ran.stdout) == (0, "probe ran\n"), ran.stderr


def python3_reporting_3_9(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\n[ "$1" = --version ] && { echo "Python 3.9.6"; exit 0; }\nexit 9\n')
    path.chmod(0o755)


@pytest.mark.process("leaf-role.sh started with a venv python3 and a PATH python3 that both report 3.9")
def test_issue_2106_shim_with_both_python3s_below_the_floor_exits_2_without_its_module_naming_each_interpreter_its_source_and_version(tmp_path):
    python3_reporting_3_9(tmp_path / "path" / "python3")
    python3_reporting_3_9(tmp_path / "venv" / "bin" / "python3")
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    named = [line for line in ran.stderr.splitlines() if "3.9.6" in line]
    assert (ran.returncode, ran.stdout, [("venv" in line, "PATH" in line) for line in named]) == (
        2, "", [(True, False), (False, True)]), ran.stderr


def venv_floor():
    return re.search("^VENV_FLOOR=(.*)$", (SCRIPTS / "lib" / "venv-python.sh").read_text(), re.M).group(1)


def path_with_dirname(directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "dirname").symlink_to(shutil.which("dirname"))
    return str(directory)


@pytest.mark.process("leaf-role.sh started with no venv python3 and a PATH holding only dirname")
def test_issue_2106_shim_with_no_venv_python3_and_none_on_path_exits_2_naming_where_it_looked_for_each(tmp_path):
    env = {"PATH": path_with_dirname(tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    refusal = "%s: veri needs Python %s or newer; " % (SCRIPTS / "leaf-role.sh", venv_floor())
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sno venv python3 at %s/venv/bin/python3.\n%sno python3 on PATH.\n" % (refusal, tmp_path, refusal))


@pytest.mark.process("leaf-role.sh started with a venv python3 and a PATH python3 that both exit 1 printing nothing")
def test_issue_2106_shim_with_both_python3s_exiting_1_silently_exits_2_naming_each_interpreter_and_an_unknown_version(tmp_path):
    for python3 in (tmp_path / "path" / "python3", tmp_path / "venv" / "bin" / "python3"):
        python3.parent.mkdir(parents=True, exist_ok=True)
        python3.write_text("#!/bin/sh\nexit 1\n")
        python3.chmod(0o755)
    env = {"PATH": path_with_dirname(tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run([str(SCRIPTS / "leaf-role.sh"), "develop-red"], capture_output=True, text=True, env=env)

    refusal = "%s: veri needs Python %s or newer; " % (SCRIPTS / "leaf-role.sh", venv_floor())
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sthe venv python3 at %s/venv/bin/python3 is version unknown.\n%sthe python3 on PATH is version unknown.\n"
        % (refusal, tmp_path, refusal))


def floor_probe(tmp_path, floor_line):
    """The canonical shim over lib/shim-python.sh beside a copy of lib/venv-python.sh whose VENV_FLOOR line is
    floor_line (None drops the file), a venv without python3 and a real python3 on PATH."""
    (tmp_path / "lib").mkdir()
    shutil.copy(SCRIPTS / "lib" / "shim-python.sh", tmp_path / "lib" / "shim-python.sh")
    if floor_line is not None:
        lib = (SCRIPTS / "lib" / "venv-python.sh").read_text()
        (tmp_path / "lib" / "venv-python.sh").write_text(re.sub("^VENV_FLOOR=.*$", floor_line, lib, count=1, flags=re.M))
    shim = tmp_path / "probe.sh"
    shim.write_text('#!/bin/sh\n. "$(dirname "$0")/lib/shim-python.sh"\nexec "$py" "$(dirname "$0")/veri/probe.py" "$@"\n')
    shim.chmod(0o755)
    (tmp_path / "veri").mkdir()
    (tmp_path / "veri" / "probe.py").write_text("print('probe ran')\n")
    python3_script(tmp_path / "path" / "python3", True)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}
    return subprocess.run([str(shim)], capture_output=True, text=True, env=env), shim


@pytest.mark.process("the floor-checking canonical shim beside a venv-python.sh whose VENV_FLOOR is 3.99, a real python3 on PATH")
def test_issue_2106_shim_refuses_by_the_venv_floor_in_lib_venv_python_sh_not_a_floor_of_its_own(tmp_path):
    ran, shim = floor_probe(tmp_path, "VENV_FLOOR=3.99")

    refusal = "%s: veri needs Python 3.99 or newer; " % shim
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        2, "", "%sno venv python3 at %s/venv/bin/python3.\n%sthe python3 on PATH is version %s.\n"
        % (refusal, tmp_path, refusal, platform.python_version()))


@pytest.mark.process("the floor-checking canonical shim with no lib/venv-python.sh beside it, or one whose VENV_FLOOR is no version")
@pytest.mark.parametrize("floor_line", [None, "VENV_FLOOR=3.12 # floor", 'VENV_FLOOR="3.12"'])
def test_issue_2106_shim_without_a_readable_venv_floor_exits_2_naming_lib_venv_python_sh(tmp_path, floor_line):
    ran, shim = floor_probe(tmp_path, floor_line)

    assert (ran.returncode, ran.stdout, ran.stderr.splitlines()[-1:]) == (
        2, "", ["%s: cannot read VENV_FLOOR from %s/lib/venv-python.sh." % (shim, tmp_path)])


@pytest.mark.process("leaf-role.sh started by sh as a bare name from the scripts directory, a real python3 on PATH")
def test_issue_2106_shim_started_by_a_name_without_a_slash_finds_its_lib_in_the_current_directory(tmp_path):
    python3_script(tmp_path / "path" / "python3", True)
    env = {"PATH": "%s:/usr/bin:/bin" % (tmp_path / "path"), "HOME": str(tmp_path / "home"), "VERI_VENV": str(tmp_path / "venv")}

    ran = subprocess.run(["sh", "leaf-role.sh", "develop-red"], capture_output=True, text=True, env=env, cwd=SCRIPTS)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "VERI_ACTOR=developer VERI_PHASE=red VERI_ATTEMPT=1\n", "")


PATH_PYTHON3_EXEC = re.compile(
    r"""^\s*exec\s+(?:(?:command|(?:/usr)?(?:/bin/)?env)\s+(?:-\S+\s+|\w+=\S*\s+)*)*['"]?python3['"]?(?:\s|$)""")


@pytest.mark.parametrize("line, runs_path_python3", [
    ('exec python3 "$(dirname "$0")/veri/x.py" "$@"', True),
    ('exec env python3 "$(dirname "$0")/veri/x.py" "$@"', True),
    ('exec /usr/bin/env python3 "$(dirname "$0")/veri/x.py" "$@"', True),
    ('exec env -i LC_ALL=C python3 x.py', True),
    ('exec "python3" x.py', True),
    ("exec 'python3' x.py", True),
    ("  exec command python3 x.py", True),
    ('exec "$py" "$(dirname "$0")/veri/x.py" "$@"', False),
    ('exec python3.12 x.py', False),
    ('# exec python3 x.py', False),
])
def test_issue_2106_the_path_python3_exec_pattern_catches_every_spelling_of_exec_and_spares_the_venv_one(line, runs_path_python3):
    assert bool(PATH_PYTHON3_EXEC.match(line)) is runs_path_python3


@pytest.mark.tree_audit("every scripts/*.sh, the exempt shims included, read as text for an unconditional exec of PATH's python3")
def test_issue_2106_no_shim_execs_the_python3_on_path_unconditionally():
    offenders = sorted(
        path.name for path in SCRIPTS.glob("*.sh")
        if any(PATH_PYTHON3_EXEC.match(line) for line in path.read_text().splitlines()))

    assert offenders == []


@pytest.mark.tree_audit("every ported scripts/**/*.sh shim, the exempt ones included, read as text for the floor-checking canonical shim")
def test_issue_2106_every_ported_shim_sources_the_floor_check_then_execs_the_py_it_sets():
    def floor_checked(lines):
        code = [line for line in lines if line.strip() and not line.startswith("#")]
        return FLOOR_SOURCE in code and code[-1].startswith('exec "$py" ') and code.index(FLOOR_SOURCE) < len(code) - 1

    offenders = sorted(
        str(path.relative_to(SCRIPTS)) for path in SCRIPTS.rglob("*.sh")
        if "tests" not in path.relative_to(SCRIPTS).parts and re.search(r"/veri/\w+\.py", path.read_text())
        and not floor_checked(path.read_text().splitlines()))

    assert offenders == []
