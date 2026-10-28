"""The run_cli fixture conftest.py gives every suite under tests/py, read through a planted module's main."""
import importlib
import os
import types

import pytest

pytest_plugins = ("pytester",)


def module_of(source):
    module = types.ModuleType("exp_planted")
    exec(source, module.__dict__)
    return module


def planted_module():
    return module_of(
        "import os, sys\n"
        "def main(argv):\n"
        "    sys.stdout.write('argv=%s\\n' % ' '.join(argv))\n"
        "    sys.stdout.write('stdin=%s' % sys.stdin.read())\n"
        "    sys.stdout.write('env=%s\\n' % os.environ.get('EXP_RUN_CLI_WORD', '<unset>'))\n"
        "    sys.stdout.write('cwd=%s\\n' % os.getcwd())\n"
        "    sys.stderr.write('planted: said its piece\\n')\n"
        "    return 4\n"
    )


def test_run_cli_calls_main_with_the_argv_stdin_environment_and_cwd_given_and_answers_its_exit_code_stdout_and_stderr(
        run_cli, tmp_path):
    cwd = os.path.realpath(tmp_path)

    code, out, err = run_cli(planted_module(), ["one", "two words"], stdin="piped text\n",
                             env={"EXP_RUN_CLI_WORD": "added"}, cwd=cwd)

    assert (code, out, err) == (
        4,
        "argv=one two words\nstdin=piped text\nenv=added\ncwd=%s\n" % cwd,
        "planted: said its piece\n",
    )


def test_run_cli_answers_the_code_a_main_that_raises_system_exit_carries(run_cli):
    module = module_of("def main(argv):\n    raise SystemExit(3)\n")

    code, _, _ = run_cli(module, [])

    assert code == 3


def test_run_cli_answers_the_integer_a_main_returns_or_raises_as_system_exit_as_the_exit_code_1389(run_cli):
    returning = module_of("def main(argv):\n    return 7\n")
    raising = module_of("def main(argv):\n    raise SystemExit(5)\n")

    assert (run_cli(returning, [])[0], run_cli(raising, [])[0]) == (7, 5)


def test_run_cli_answers_0_when_a_main_returns_none_or_raises_system_exit_with_no_code_or_none_1389(run_cli):
    sources = ("def main(argv):\n    return None\n",
               "def main(argv):\n    raise SystemExit()\n",
               "def main(argv):\n    raise SystemExit(None)\n")
    modules = [module_of(source) for source in sources]

    assert tuple(run_cli(module, [])[0] for module in modules) == (0, 0, 0)


def test_run_cli_answers_1_and_writes_the_text_to_stderr_when_a_main_raises_system_exit_with_a_message_1389(run_cli):
    module = module_of("def main(argv):\n    raise SystemExit('planted: refused')\n")

    code, _, err = run_cli(module, [])

    assert (code, err) == (1, "planted: refused\n")


def test_run_cli_answers_1_and_writes_the_text_to_stderr_when_a_main_raises_system_exit_with_a_float_or_a_tuple_1389(
        run_cli):
    sources = ("def main(argv):\n    raise SystemExit(2.5)\n",
               "def main(argv):\n    raise SystemExit((4, 'planted'))\n")
    modules = [module_of(source) for source in sources]

    answers = [run_cli(module, []) for module in modules]

    assert [(code, err) for code, _, err in answers] == [(1, "2.5\n"), (1, "(4, 'planted')\n")]


def test_run_cli_answers_2_and_the_one_line_entry_run_writes_when_a_main_raises_an_uncaught_exception_1401(run_cli):
    module = types.ModuleType("exp_refusing")
    exec(compile("def main(argv):\n    raise ValueError('planted   refusal\\n  here')\n",
                 "/exp/exp_refusing.py", "exec"), module.__dict__)

    code, _, err = run_cli(module, [])

    assert (code, len(err.splitlines()), err.startswith("exp-refusing.sh: ValueError: planted refusal here")) == (2, 1, True)


def test_run_cli_answers_1_and_writes_the_string_to_stderr_when_a_main_returns_a_string_1401(run_cli):
    module = module_of("def main(argv):\n    return 'planted: refused'\n")

    code, _, err = run_cli(module, [])

    assert (code, err) == (1, "planted: refused\n")


def test_run_cli_answers_141_when_a_main_raises_broken_pipe_error_1401(run_cli):
    module = module_of("def main(argv):\n    raise BrokenPipeError('planted pipe')\n")

    code, _, err = run_cli(module, [])

    assert (code, err) == (141, "")


@pytest.mark.process("a child writing to the inherited stdout and stderr")
def test_run_cli_includes_in_order_what_a_child_the_module_starts_writes_to_the_inherited_stdout_and_stderr(run_cli):
    module = module_of(
        "import subprocess, sys\n"
        "def main(argv):\n"
        "    sys.stdout.write('parent out before\\n')\n"
        "    sys.stderr.write('parent err before\\n')\n"
        "    subprocess.run(['/bin/sh', '-c', 'echo child out; echo child err >&2'])\n"
        "    sys.stdout.write('parent out after\\n')\n"
        "    sys.stderr.write('parent err after\\n')\n"
        "    return 0\n"
    )

    code, out, err = run_cli(module, [])

    assert (code, out, err) == (
        0,
        "parent out before\nchild out\nparent out after\n",
        "parent err before\nchild err\nparent err after\n",
    )


def test_run_cli_leaves_no_environment_or_cwd_change_made_through_it_or_by_main_behind_the_case(pytester, monkeypatch):
    for name in ("EXP_RUN_CLI_ADDED", "EXP_MAIN_SET"):
        monkeypatch.setenv(name, "outer")
        monkeypatch.delenv(name)
    pytester.makepyfile(test_plant="""
        import os
        import types

        START = os.getcwd()


        def planted(source):
            module = types.ModuleType("exp_mutating")
            exec(source, module.__dict__)
            return module


        def test_changes_through_run_cli(run_cli, tmp_path):
            run_cli(planted("def main(argv):\\n    return 0\\n"), [],
                    env={"EXP_RUN_CLI_ADDED": "added"}, cwd=str(tmp_path))


        def test_changes_by_main(run_cli):
            os.mkdir("exp-main-moved")
            run_cli(planted(
                "import os\\n"
                "def main(argv):\\n"
                "    os.environ['EXP_MAIN_SET'] = 'leaked'\\n"
                "    os.chdir('exp-main-moved')\\n"
                "    return 0\\n"), [])


        def test_nothing_outlived_the_cases():
            assert (os.environ.get("EXP_RUN_CLI_ADDED"), os.environ.get("EXP_MAIN_SET"), os.getcwd()) == (None, None, START)
    """)

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.parseoutcomes() == {"passed": 3}, output
