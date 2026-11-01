"""The search-path setup conftest.py gives every suite under tests/py, read by a suite with none of its own."""
import importlib
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
from sys import path as search_path

import pytest


def test_a_suite_with_no_path_setup_reads_scripts_from_conftest_and_imports_veri_and_script_modules():
    conftest = importlib.import_module("conftest")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    entries = [str(scripts), str(scripts / "veri")]

    assert conftest.SCRIPTS == scripts
    assert [search_path.count(entry) for entry in entries] == [1, 1]
    assert sorted(search_path[:2]) == sorted(entries)
    assert importlib.import_module("ledger").__file__ == str(scripts / "veri" / "ledger.py")
    assert importlib.import_module("veri.ledger").__file__ == str(scripts / "veri" / "ledger.py")


def test_fake_processes_given_no_answer_records_every_entry_point_by_basename_and_answers_0_with_empty_output_starting_no_process(
        fake_processes, tmp_path):
    calls = fake_processes()
    entries = ("run", "Popen", "call", "check_call", "check_output")

    answers = [getattr(subprocess, entry)(["/usr/bin/touch", str(tmp_path / entry)]) for entry in entries]

    assert calls == ["touch %s" % (tmp_path / entry) for entry in entries]
    assert [(answer.returncode, answer.stdout, answer.stderr) for answer in answers] == [(0, "", "")] * len(entries)
    assert sorted(tmp_path.iterdir()) == []


def test_fake_processes_given_an_answer_hands_run_the_line_and_its_keyword_arguments_and_refuses_every_other_entry_point_naming_the_command(
        fake_processes, tmp_path):
    asked = []

    def answer(line, **kwargs):
        asked.append((line, kwargs))
        return 3, "out", "err"

    calls = fake_processes(answer)

    ran = subprocess.run(["/usr/bin/touch", str(tmp_path / "run")], capture_output=True, text=True)

    assert asked == [("touch %s" % (tmp_path / "run"), {"capture_output": True, "text": True})]
    assert (ran.returncode, ran.stdout, ran.stderr) == (3, "out", "err")
    for entry in ("Popen", "call", "check_call", "check_output"):
        line = "touch %s" % (tmp_path / entry)
        try:
            getattr(subprocess, entry)(["/usr/bin/touch", str(tmp_path / entry)])
        except AssertionError as refused:
            assert line in str(refused), entry
        else:
            raise AssertionError("%s answered rather than refusing" % entry)
    assert calls[0] == "touch %s" % (tmp_path / "run")
    assert sorted(tmp_path.iterdir()) == []


def test_fake_processes_hands_output_back_in_the_calls_mode_merges_stderr_on_request_and_raises_on_check(
        fake_processes):
    answers = {"text": (0, b"out", b"err"), "bytes": (0, "out", "err"), "merge": (0, "out", "err"),
               "check": (3, "out", "err")}
    fake_processes(lambda line, **_: answers[line.split()[1]])

    def output(args, **kwargs):
        ran = subprocess.run(args, **kwargs)
        return ran.stdout, ran.stderr

    observed = [
        output(["tool", "text"], text=True),
        output(["tool", "text"], encoding="utf-8"),
        output(["tool", "text"], universal_newlines=True),
        output(["tool", "bytes"]),
        output(["tool", "merge"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True),
    ]

    assert observed == [("out", "err")] * 3 + [(b"out", b"err"), ("outerr", None)]
    try:
        subprocess.run(["tool", "check"], check=True, text=True)
    except subprocess.CalledProcessError as raised:
        assert (raised.returncode, raised.cmd, raised.output, raised.stderr) == (3, ["tool", "check"], "out", "err")
    else:
        raise AssertionError("a non-zero answer under check=True returned rather than raising")


def child_pytest(tmp_path, probe, env, select=(), plugins=()):
    here = pathlib.Path(__file__).resolve().parent
    env = {**env, "PYTHONPATH": os.pathsep.join([str(here), str(here.parents[1])] if plugins else [str(here)])}
    loaded = [arg for plugin in plugins for arg in ("-p", plugin)]
    return subprocess.run([sys.executable, "-m", "pytest", "-p", "conftest", *loaded, "-p", "no:cacheprovider", "-q",
                           "--rootdir", str(tmp_path), *select, str(probe)],
                          env=env, cwd=tmp_path, capture_output=True, text=True)


@pytest.mark.process("a child pytest session started with ambient VERI_, CLAUDE_, GH_ and GIT_ variables")
def test_every_case_starts_with_no_veri_claude_gh_or_git_variable_set_but_veri_venv_and_its_own_legs_registry_whatever_the_shell_had(tmp_path):
    probe = tmp_path / "test_probe.py"
    seen = tmp_path / "seen.json"
    probe.write_text(
        "import json, os\n"
        "def test_probe():\n"
        "    names = [n for n in os.environ if n.startswith(('VERI_', 'CLAUDE_', 'GH_', 'GIT_'))]\n"
        "    open(%r, 'w').write(json.dumps(sorted(names)))\n" % str(seen))
    ambient = {name: "1" for name in ("VERI_ISSUE", "VERI_VENV", "CLAUDE_X", "GH_TOKEN", "GIT_DIR")}
    env = {**{k: v for k, v in os.environ.items()
              if not k.startswith("GIT_CONFIG_") and k not in ("GIT_TEMPLATE_DIR", "GIT_EXEC_PATH")}, **ambient}

    ran = child_pytest(tmp_path, probe, env)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert json.loads(seen.read_text()) == ["VERI_HOME", "VERI_MIN_FREE_GB", "VERI_PYTEST_LEGS", "VERI_VENV"]


@pytest.mark.process("a child pytest session started with GIT_TEMPLATE_DIR and GIT_EXEC_PATH set beside other GIT_ variables")
@pytest.mark.parametrize("kept", ["GIT_TEMPLATE_DIR", "GIT_EXEC_PATH"])
def test_a_case_still_sees_the_git_variable_make_test_sets_for_apple_git_at_the_same_value_while_other_git_variables_are_cleared(tmp_path, kept):
    probe = tmp_path / "test_probe.py"
    seen = tmp_path / "seen.json"
    probe.write_text(
        "import json, os\n"
        "def test_probe():\n"
        "    git = {n: v for n, v in os.environ.items() if n.startswith('GIT_') and not n.startswith('GIT_CONFIG_')}\n"
        "    open(%r, 'w').write(json.dumps(git))\n" % str(seen))
    ambient = {kept: str(tmp_path / "share" / "git-core"), "GIT_DIR": "1", "GIT_WORK_TREE": "1"}
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **ambient}

    ran = child_pytest(tmp_path, probe, env)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert json.loads(seen.read_text()) == {kept: str(tmp_path / "share" / "git-core")}


@pytest.mark.process("a child pytest session started with an ambient locale")
def test_every_case_starts_under_lc_all_c_with_every_other_lc_variable_and_lang_unset_whatever_the_shell_had(tmp_path):
    probe = tmp_path / "test_probe.py"
    seen = tmp_path / "seen.json"
    probe.write_text(
        "import json, os\n"
        "def test_probe():\n"
        "    locale = {n: v for n, v in os.environ.items() if n == 'LANG' or n.startswith('LC_')}\n"
        "    open(%r, 'w').write(json.dumps(locale))\n" % str(seen))
    ambient = {"LC_ALL": "en_US.UTF-8", "LANG": "en_US.UTF-8", "LC_TIME": "de_DE.UTF-8"}
    env = {**os.environ, **ambient}

    ran = child_pytest(tmp_path, probe, env)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert json.loads(seen.read_text()) == {"LC_ALL": "C"}


@pytest.mark.process("a child pytest session whose case runs a real git against an https remote")
def test_a_medium_cases_git_still_refuses_a_remote_url_after_the_fixture_clears_git_variables_because_it_restores_the_offline_git_settings(tmp_path):
    probe = tmp_path / "test_probe.py"
    seen = tmp_path / "seen.json"
    probe.write_text(
        "import json, subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('git against an https remote')\n"
        "def test_probe():\n"
        "    ran = subprocess.run(['git', 'ls-remote', 'https://127.0.0.1:1/x.git'], capture_output=True, text=True)\n"
        "    open(%r, 'w').write(json.dumps(ran.stderr))\n" % str(seen))
    offline = {"GIT_CONFIG_COUNT": "2",
               "GIT_CONFIG_KEY_0": "protocol.allow", "GIT_CONFIG_VALUE_0": "never",
               "GIT_CONFIG_KEY_1": "protocol.file.allow", "GIT_CONFIG_VALUE_1": "always"}
    env = {**os.environ, **offline}

    ran = child_pytest(tmp_path, probe, env)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert "not allowed" in json.loads(seen.read_text())


@pytest.mark.process("a child pytest session started from the repository root and again from skills/tdd/scripts")
def test_a_case_reading_a_cwd_relative_path_gives_the_same_outcome_started_from_the_repository_root_as_from_skills_tdd_scripts(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pathlib\n"
        "def test_probe():\n"
        "    assert pathlib.Path('Makefile').is_file()\n")
    scripts = pathlib.Path(__file__).resolve().parents[2]
    env = {**os.environ, "PYTHONPATH": str(pathlib.Path(__file__).resolve().parent)}

    def started_from(cwd):
        return subprocess.run([sys.executable, "-m", "pytest", "-p", "conftest", "-p", "no:cacheprovider", "-q",
                               "--rootdir", str(tmp_path), str(probe)],
                              env=env, cwd=cwd, capture_output=True, text=True).returncode

    outcomes = {"repository root": started_from(scripts.parents[2]), "skills/tdd/scripts": started_from(scripts)}

    assert outcomes["skills/tdd/scripts"] == outcomes["repository root"], outcomes


@pytest.mark.process("a child pytest session started from the repository root and again from skills/tdd/scripts with a relative test path")
def test_the_path_setup_case_gives_the_same_outcome_started_from_skills_tdd_scripts_with_a_relative_path_as_from_the_repository_root():
    scripts = pathlib.Path(__file__).resolve().parents[2]
    case = "test_conftest.py::test_a_suite_with_no_path_setup_reads_scripts_from_conftest_and_imports_veri_and_script_modules"

    def started_from(cwd, path):
        return subprocess.run([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "%s/%s" % (path, case)],
                              cwd=cwd, capture_output=True, text=True).returncode

    outcomes = {"repository root": started_from(scripts.parents[2], "skills/tdd/scripts/tests/py"),
                "skills/tdd/scripts": started_from(scripts, "tests/py")}

    assert outcomes["skills/tdd/scripts"] == outcomes["repository root"], outcomes


@pytest.mark.process("a real sleep launched through the process-case PATH shim by a parent that only names push_branch in its arguments")
def test_a_process_case_whose_sleep_parent_only_names_push_branch_in_its_arguments_is_not_failed_for_reaching_the_push_backoff():
    done = subprocess.run(["sh", "-c", "sleep 0; echo $?", "push_branch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert (done.returncode, done.stdout, done.stderr) == (0, b"0\n", b"")


@pytest.mark.process("a child pytest session whose process case starts push-branch.sh against an unreachable origin with VERI_PUSH_BACKOFF unset")
def test_a_process_case_that_starts_push_branch_sh_into_its_backoff_without_veri_push_backoff_fails_at_teardown_naming_the_case(tmp_path):
    repo = tmp_path / "run"
    repo.mkdir()
    for args in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "initial"],
                 ["checkout", "-q", "-b", "tdd/1376-probe"], ["remote", "add", "origin", str(tmp_path / "no-such-remote.git")]):
        done = subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                              capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os, subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('push-branch.sh pushing to an unreachable origin')\n"
        "def test_probe():\n"
        "    env = {**os.environ, 'VERI_PUSH_RETRIES': '1', 'VERI_ISSUE': '1376', 'VERI_ACTOR': 'conductor'}\n"
        "    subprocess.run([%r], cwd=%r, env=env, capture_output=True)\n"
        % (str(pathlib.Path(__file__).resolve().parents[2] / "push-branch.sh"), str(repo)))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode == 1, output
    assert "1 passed, 1 error" in output, output
    assert "test_probe.py::test_probe reached the push backoff without setting VERI_PUSH_BACKOFF" in output, output


@pytest.mark.process("a child pytest session whose unmarked and tree_audit-marked cases list a repository directory")
def test_an_unmarked_case_that_lists_a_repository_directory_outside_its_tmp_path_fails_naming_the_case_and_the_directory_while_a_tree_audit_case_passes(tmp_path):
    listed = pathlib.Path(__file__).resolve().parent
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "import pytest\n"
        "def test_unmarked():\n"
        "    os.listdir(%r)\n"
        "@pytest.mark.tree_audit('the tests directory')\n"
        "def test_marked():\n"
        "    os.listdir(%r)\n" % (str(listed), str(listed)))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "FAILED test_probe.py::test_unmarked" in output, output
    assert "lists the repository directory %s" % listed in output, output
    assert "test_probe.py::test_marked" not in output, output


@pytest.mark.process("a child pytest session whose unmarked, faking and process-marked cases read pid_file's process listing")
def test_2832_an_unmarked_case_that_reaches_pid_files_real_process_listing_fails_naming_it_while_a_case_that_fakes_it_passes_and_a_process_case_may_read_it(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pytest\n"
        "from veri import pid_file\n"
        "def test_unmarked():\n"
        "    pid_file.starting_runs(%r)\n"
        "def test_faked(monkeypatch):\n"
        "    monkeypatch.setattr(pid_file, '_conductors', lambda: [])\n"
        "    assert pid_file.starting_runs(%r) == []\n"
        "@pytest.mark.process('the real ps')\n"
        "def test_process():\n"
        "    pid_file.starting_runs(%r)\n" % (str(tmp_path), str(tmp_path), str(tmp_path)))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "FAILED test_probe.py::test_unmarked" in output, output
    assert "process listing" in output, output
    assert "test_probe.py::test_faked" not in output, output
    assert "test_probe.py::test_process" not in output, output
    assert "1 failed, 2 passed" in output, output


@pytest.mark.process("a child pytest session whose unmarked case reaches the process listing through watch_runs's own pid_file import")
def test_2832_an_unmarked_case_that_reaches_the_process_listing_through_the_pid_file_module_watch_runs_imports_fails_naming_it(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import importlib\n"
        "def test_unmarked():\n"
        "    watch_runs = importlib.import_module('veri.watch_runs')\n"
        "    watch_runs.pid_file.starting_runs(%r)\n" % str(tmp_path))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "FAILED test_probe.py::test_unmarked" in output, output
    assert "process listing" in output, output


@pytest.mark.process("a child pytest session run with the unit recipe's own -m selection over an unmarked, a process and a tree_audit case")
def test_the_unit_recipes_selection_runs_only_the_unmarked_case_and_deselects_the_process_and_tree_audit_cases(tmp_path):
    makefile = pathlib.Path(__file__).resolve().parents[5] / "Makefile"
    recipe = re.search(r"^unit: PY_SELECT = (.*)$", makefile.read_text(), re.M).group(1)
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pytest\n"
        "def test_unmarked():\n"
        "    pass\n"
        "@pytest.mark.process('a probe process')\n"
        "def test_process():\n"
        "    raise SystemExit(1)\n"
        "@pytest.mark.tree_audit('a probe sweep')\n"
        "def test_tree_audit():\n"
        "    raise SystemExit(1)\n")

    ran = child_pytest(tmp_path, probe, os.environ, shlex.split(recipe))

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert "1 passed, 2 deselected" in output, output


@pytest.mark.process("a child pytest session run with --timeout=30 over an unmarked, a process and a process case with its own timeout mark")
def test_a_process_case_without_its_own_timeout_mark_gets_90_s_while_an_unmarked_case_keeps_the_session_timeout_and_an_explicit_mark_wins(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pytest\n"
        "def seen(request):\n"
        "    mark = request.node.get_closest_marker('timeout')\n"
        "    print('TIMEOUT %s %s' % (request.node.name, mark.args[0] if mark else 'session'))\n"
        "def test_unmarked(request):\n"
        "    seen(request)\n"
        "@pytest.mark.process('a probe process')\n"
        "def test_process(request):\n"
        "    seen(request)\n"
        "@pytest.mark.process('a probe process')\n"
        "@pytest.mark.timeout(5)\n"
        "def test_explicit(request):\n"
        "    seen(request)\n")

    ran = child_pytest(tmp_path, probe, os.environ, ["--timeout=30", "-s"])

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert sorted(re.findall(r"TIMEOUT \S+ \S+", ran.stdout)) == [
        "TIMEOUT test_explicit 5", "TIMEOUT test_process 90", "TIMEOUT test_unmarked session"], output


@pytest.mark.process("a child pytest session whose parametrized pair and third case each write a file into their tmp_path")
def test_each_case_gets_a_private_empty_tmp_path_that_exists_and_a_file_left_in_one_is_absent_from_the_next(tmp_path):
    seen = tmp_path / "seen.txt"
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pathlib\n"
        "import pytest\n"
        "SEEN = pathlib.Path(%r)\n"
        "def check(tmp_path):\n"
        "    assert tmp_path.exists() and tmp_path.is_dir()\n"
        "    assert list(tmp_path.iterdir()) == []\n"
        "    (tmp_path / 'left.txt').write_text('left')\n"
        "    with SEEN.open('a') as log:\n"
        "        log.write(str(tmp_path) + '\\n')\n"
        "@pytest.mark.parametrize('n', [1, 2])\n"
        "def test_pair(tmp_path, n):\n"
        "    check(tmp_path)\n"
        "def test_third(tmp_path):\n"
        "    check(tmp_path)\n" % str(seen))

    ran = child_pytest(tmp_path, probe, os.environ, plugins=["veri.private_tmp_path"])

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert "3 passed" in output, output
    paths = seen.read_text().split()
    assert len(paths) == 3 and len(set(paths)) == 3, paths
