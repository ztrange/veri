"""The search-path setup conftest.py gives every suite under tests/py, read by a suite with none of its own."""
import importlib
import json
import os
import pathlib
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


def child_pytest(tmp_path, probe, env):
    env = {**env, "PYTHONPATH": str(pathlib.Path(__file__).resolve().parent)}
    return subprocess.run([sys.executable, "-m", "pytest", "-p", "conftest", "-p", "no:cacheprovider", "-q",
                           "--rootdir", str(tmp_path), str(probe)],
                          env=env, cwd=tmp_path, capture_output=True, text=True)


@pytest.mark.process("a child pytest session started with ambient VERI_, CLAUDE_, GH_ and GIT_ variables")
def test_every_case_starts_with_no_veri_claude_gh_or_git_variable_set_but_veri_venv_whatever_the_shell_had(tmp_path):
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
    assert json.loads(seen.read_text()) == ["VERI_VENV"]


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


@pytest.mark.process("a child pytest session whose case starts bash on a *.test.sh under a tests/ directory")
def test_a_case_that_starts_a_bash_suite_under_tests_fails_naming_the_case_and_the_command_without_the_suite_running(tmp_path):
    suite = tmp_path / "tests" / "nested.test.sh"
    suite.parent.mkdir()
    ran_marker = tmp_path / "suite-ran"
    suite.write_text("touch %s\n" % ran_marker)
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('bash on a suite under tests/')\n"
        "def test_probe():\n"
        "    subprocess.run(['bash', %r])\n" % str(suite))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert "bash %s" % suite in output, output
    assert not ran_marker.exists()


@pytest.mark.process("a child pytest session whose case starts python3 -m pytest")
def test_a_case_that_starts_pytest_as_a_process_fails_naming_the_case_and_the_command_without_the_inner_session_running(tmp_path):
    inner = tmp_path / "test_inner.py"
    ran_marker = tmp_path / "inner-ran"
    inner.write_text("def test_inner():\n    open(%r, 'w').close()\n" % str(ran_marker))
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import subprocess, sys\n"
        "import pytest\n"
        "@pytest.mark.process('python3 -m pytest')\n"
        "def test_probe():\n"
        "    subprocess.run([sys.executable, '-m', 'pytest', %r])\n" % str(inner))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert "-m pytest %s" % inner in output, output
    assert not ran_marker.exists()


@pytest.mark.process("a child pytest session whose case hands echo a suite path, a pytest node id and a launcher name as arguments")
def test_a_case_that_only_carries_a_suite_path_or_a_pytest_node_id_as_an_argument_to_a_process_that_is_not_a_test_runner_passes_the_guard(tmp_path):
    suite = tmp_path / "tests" / "nested.test.sh"
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('echo with test-runner names as data')\n"
        "def test_probe():\n"
        "    ran = subprocess.run(['echo', %r, 'tests/py/test_x.py::test_y', 'pytest_leg.py'], capture_output=True, text=True)\n"
        "    assert ran.returncode == 0\n" % str(suite))

    ran = child_pytest(tmp_path, probe, os.environ)

    assert ran.returncode == 0, ran.stdout + ran.stderr


@pytest.mark.process("a child pytest session whose case starts git with -C on the repository the tests live in")
def test_a_case_that_starts_git_against_the_repository_the_tests_live_in_fails_naming_the_case_and_the_path(tmp_path):
    repository = pathlib.Path(__file__).resolve().parents[4]
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('git -C on the repository root')\n"
        "def test_probe():\n"
        "    subprocess.run(['git', '-C', %r, 'rev-parse', 'HEAD'], capture_output=True)\n" % str(repository / "skills"))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert str(repository / "skills") in output, output


@pytest.mark.process("a child pytest session whose case starts git with no -C from the directory of the module under test")
def test_a_case_that_starts_git_from_the_directory_of_the_module_under_test_fails_naming_the_case_and_the_path(tmp_path):
    module_directory = pathlib.Path(__file__).resolve().parents[2] / "veri"
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('git with no -C after a chdir to the module directory')\n"
        "def test_probe():\n"
        "    os.chdir(%r)\n"
        "    subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True)\n" % str(module_directory))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert str(module_directory) in output, output


@pytest.mark.process("a child pytest session whose case fakes subprocess.run and runs git from the module's own directory")
def test_a_case_that_fakes_subprocess_run_still_fails_naming_the_case_and_the_path_when_its_subject_runs_git_from_the_module_directory(tmp_path):
    module_directory = pathlib.Path(__file__).resolve().parents[2] / "veri"
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('subprocess.run faked, git run with cwd= the module directory')\n"
        "def test_probe(monkeypatch):\n"
        "    monkeypatch.setattr(subprocess, 'run', lambda args, **kwargs: subprocess.CompletedProcess(args, 0, '', ''))\n"
        "    subprocess.run(['git', 'worktree', 'list', '--porcelain'], cwd=%r)\n" % str(module_directory))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert str(module_directory) in output, output


@pytest.mark.process("a child pytest session whose case fakes subprocess.run and runs git with no cwd from the repository root")
def test_a_case_that_fakes_subprocess_run_still_fails_naming_the_case_and_the_path_when_its_subject_runs_git_with_no_cwd_inside_the_repository(tmp_path):
    repository = pathlib.Path(__file__).resolve().parents[4]
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('subprocess.run faked, git run with no cwd after a chdir to the repository root')\n"
        "def test_probe(monkeypatch):\n"
        "    monkeypatch.setattr(subprocess, 'run', lambda args, **kwargs: subprocess.CompletedProcess(args, 0, '', ''))\n"
        "    os.chdir(%r)\n"
        "    subprocess.run(['git', 'rev-parse', '--show-toplevel'])\n" % str(repository))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert str(repository) in output, output


@pytest.mark.process("a child pytest session whose case fakes subprocess.run by its dotted string and runs git with no cwd from the repository root")
def test_a_case_that_fakes_subprocess_run_by_its_dotted_string_still_fails_naming_the_case_and_the_path_when_its_subject_runs_git_with_no_cwd_inside_the_repository(tmp_path):
    repository = pathlib.Path(__file__).resolve().parents[4]
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "import subprocess\n"
        "import pytest\n"
        "@pytest.mark.process('subprocess.run faked by string, git run with no cwd after a chdir to the repository root')\n"
        "def test_probe(monkeypatch):\n"
        "    monkeypatch.setattr('subprocess.run', lambda args, **kwargs: subprocess.CompletedProcess(args, 0, '', ''))\n"
        "    os.chdir(%r)\n"
        "    subprocess.run(['git', 'rev-parse', '--show-toplevel'])\n" % str(repository))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py::test_probe" in output, output
    assert str(repository) in output, output


@pytest.mark.process("a child pytest session whose case takes the permission bits off a file with os.chmod")
def test_a_case_that_forces_a_failure_through_permission_bits_fails_naming_the_file_and_line_of_the_chmod_call(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "def test_probe(tmp_path):\n"
        "    target = tmp_path / 'unreadable'\n"
        "    target.write_text('x')\n"
        "    os.chmod(target, 0o000)\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py:5" in output, output
    assert "chmod" in output, output


@pytest.mark.process("a child pytest session whose case reads a system location outside its tmp_path")
def test_a_case_that_reads_a_system_location_outside_its_tmp_path_fails_naming_the_file_and_line_of_the_call(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "def test_probe():\n"
        "    open('/etc/hosts').read()\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "test_probe.py:2" in output, output
    assert "/etc/hosts" in output, output


@pytest.mark.process("a child pytest session whose case reads a system location outside its tmp_path")
@pytest.mark.parametrize("location", ["/.veri-probe-absent", "/root/.profile", "/proc/self/status"])
def test_a_case_that_reads_the_filesystem_root_root_or_proc_fails_naming_the_location_and_the_line(tmp_path, location):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "def test_probe():\n"
        "    open(%r).read()\n" % location)

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "opens the system location %s at " % location in output, output
    assert "test_probe.py:2" in output, output


@pytest.mark.process("a child pytest session whose case reads a system location through pathlib")
@pytest.mark.parametrize("read", ["read_text()", "open().read()"])
def test_a_case_that_reads_a_system_location_through_pathlib_fails_naming_its_own_line_not_pathlibs(tmp_path, read):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pathlib\n"
        "def test_probe():\n"
        "    pathlib.Path('/etc/hosts').%s\n" % read)

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "opens the system location /etc/hosts at " in output, output
    assert "test_probe.py:3" in output, output


@pytest.mark.process("a child pytest session whose case creates a directory at a system location")
def test_a_case_that_creates_a_directory_at_a_system_location_with_os_mkdir_fails_naming_the_file_and_line_of_the_call(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "def test_probe():\n"
        "    os.mkdir('/.tdd')\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "creates the system location /.tdd at " in output, output
    assert "test_probe.py:3" in output, output


@pytest.mark.process("a child pytest session whose case creates a directory at a system location through pathlib")
def test_a_case_that_creates_a_directory_at_a_system_location_with_path_mkdir_parents_fails_naming_the_file_and_line_of_the_call(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import pathlib\n"
        "def test_probe():\n"
        "    pathlib.Path('/.tdd/x').mkdir(parents=True)\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "creates the system location /.tdd at " in output, output
    assert "test_probe.py:3" in output, output


@pytest.mark.process("a child pytest session whose case creates a file at a system location")
def test_a_case_that_creates_a_file_at_a_system_location_with_os_open_o_creat_fails_naming_the_file_and_line_of_the_call(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "def test_probe():\n"
        "    os.open('/.veri-probe-absent', os.O_CREAT | os.O_WRONLY)\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "creates the system location /.veri-probe-absent at " in output, output
    assert "test_probe.py:3" in output, output


@pytest.mark.process("child pytest sessions whose permission-bits exemption table carries a good, a reasonless and a stale entry")
@pytest.mark.parametrize("entry, reason, mode, named", [
    ("test_probe.py::test_probe", "the chmod is the subject, run on a scratch file", 0o000, None),
    ("test_probe.py::test_probe", "", 0o000, "test_probe.py::test_probe"),
    ("test_probe.py::test_gone", "a reason for a case renamed away", 0o644, "test_probe.py::test_gone"),
])
def test_a_permission_bits_exemption_with_a_reason_naming_an_existing_case_passes_and_one_with_no_reason_or_no_such_case_fails_the_run_naming_it(
        tmp_path, entry, reason, mode, named):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os\n"
        "import conftest\n"
        "conftest.PERMISSION_BITS_EXEMPT[%r] = %r\n"
        "def test_probe(tmp_path):\n"
        "    target = tmp_path / 'unreadable'\n"
        "    target.write_text('x')\n"
        "    os.chmod(target, 0o%o)\n" % (entry, reason, mode))

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    if named is None:
        assert ran.returncode == 0, output
    else:
        assert ran.returncode != 0, output
        assert "exemption" in output and named in output, output


@pytest.mark.process("a child pytest session whose case touches the platform temp directory when it is /tmp")
def test_a_case_that_creates_at_the_platform_temp_directory_when_it_is_tmp_passes(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import os, tempfile\n"
        "import pytest\n"
        "def test_probe(monkeypatch):\n"
        "    monkeypatch.setattr(tempfile, 'tempdir', '/tmp')\n"
        "    with pytest.raises(FileExistsError):\n"
        "        os.mkdir(tempfile.gettempdir())\n"
        "    with pytest.raises(FileExistsError):\n"
        "        os.mkdir('/tmp')\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert "1 passed" in output, output


@pytest.mark.process("a child pytest session whose case opens a tempfile.TemporaryFile under /tmp, its open of /tmp attributed to the case")
def test_a_case_that_opens_a_tempfile_temporaryfile_passes_the_system_location_guard(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import inspect, tempfile, textwrap\n"
        "def test_probe(monkeypatch):\n"
        "    monkeypatch.setattr(tempfile, 'tempdir', '/tmp')\n"
        "    scope = dict(vars(tempfile))\n"
        "    exec(compile(textwrap.dedent(inspect.getsource(tempfile.TemporaryFile)), __file__, 'exec'), scope)\n"
        "    with scope['TemporaryFile']() as handle:\n"
        "        handle.write(b'x')\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert "1 passed" in output, output


@pytest.mark.process("a child pytest session whose system-location exemption table carries a reasonless entry")
def test_a_system_location_exemption_with_no_reason_fails_the_run_naming_the_entry(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import conftest\n"
        "conftest.SYSTEM_LOCATION_EXEMPT['test_probe.py::test_probe'] = ''\n"
        "def test_probe():\n"
        "    pass\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "exemption" in output and "test_probe.py::test_probe" in output, output


@pytest.mark.process("child pytest sessions whose starts-pytest or starts-git exemption table carries a reasonless entry")
@pytest.mark.parametrize("table", ["STARTS_PYTEST_EXEMPT", "STARTS_GIT_IN_REPOSITORY_EXEMPT"])
def test_a_starts_pytest_or_starts_git_exemption_with_no_reason_fails_the_run_naming_the_entry(tmp_path, table):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import conftest\n"
        "conftest.%s['test_probe.py::test_probe'] = ''\n"
        "def test_probe():\n"
        "    pass\n" % table)

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "exemption" in output and "test_probe.py::test_probe" in output, output


@pytest.mark.process("a child pytest session whose starts-git exemption table carries a whole-file entry with the RUNS_GIT_WITH_NO_CWD reason")
def test_a_starts_git_whole_file_exemption_with_the_runs_git_with_no_cwd_reason_fails_the_run_naming_the_entry(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import conftest\n"
        "conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT['test_probe.py'] = conftest.RUNS_GIT_WITH_NO_CWD\n"
        "def test_probe():\n"
        "    pass\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode != 0, output
    assert "exemption" in output and "test_probe.py" in output, output


@pytest.mark.process("a child pytest session whose starts-git exemption table carries a case-level RUNS_GIT_WITH_NO_CWD entry and a whole-file entry with another reason")
def test_a_starts_git_case_level_runs_git_with_no_cwd_entry_and_a_whole_file_entry_with_another_reason_pass_the_run(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import conftest\n"
        "conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT['test_probe.py::test_probe'] = conftest.RUNS_GIT_WITH_NO_CWD\n"
        "conftest.STARTS_GIT_IN_REPOSITORY_EXEMPT['test_probe.py'] = 'another reason'\n"
        "def test_probe():\n"
        "    pass\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode == 0, output
    assert "1 passed" in output, output


@pytest.mark.process("a real sleep launched through the process-case PATH shim by a parent that only names push_branch in its arguments")
def test_a_process_case_whose_sleep_parent_only_names_push_branch_in_its_arguments_is_not_failed_for_reaching_the_push_backoff():
    done = subprocess.run(["sh", "-c", "sleep 0; echo $?", "push_branch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert (done.returncode, done.stdout, done.stderr) == (0, b"0\n", b"")


@pytest.mark.process("a child pytest session whose small case drives push_branch.main into its retry backoff with VERI_PUSH_BACKOFF unset")
def test_a_small_case_that_drives_push_branch_into_its_backoff_without_veri_push_backoff_fails_naming_the_case(tmp_path):
    probe = tmp_path / "test_probe.py"
    probe.write_text(
        "import importlib\n"
        "def test_probe(tmp_path, monkeypatch, fake_processes, events):\n"
        "    push_branch = importlib.import_module('veri.push_branch')\n"
        "    fake_processes(lambda line, **_: (128, 'fatal: unable to access origin\\n', '')\n"
        "                   if line.startswith('git push') else (0, '', ''))\n"
        "    events.refuse_event_sh()\n"
        "    monkeypatch.chdir(tmp_path)\n"
        "    monkeypatch.setenv('VERI_PUSH_RETRIES', '1')\n"
        "    push_branch.main([])\n")

    ran = child_pytest(tmp_path, probe, os.environ)

    output = ran.stdout + ran.stderr
    assert ran.returncode == 1, output
    assert "test_probe.py::test_probe reached the push backoff without setting VERI_PUSH_BACKOFF" in output, output


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
