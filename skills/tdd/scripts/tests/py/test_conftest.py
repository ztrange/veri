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
    env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_")}, **ambient}

    ran = child_pytest(tmp_path, probe, env)

    assert ran.returncode == 0, ran.stdout + ran.stderr
    assert json.loads(seen.read_text()) == ["VERI_VENV"]


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
