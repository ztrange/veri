"""The run_cli fixture conftest.py gives every suite under tests/py, read through a planted module's main."""
import os
import types


def planted_module():
    module = types.ModuleType("exp_planted")
    exec(
        "import os, sys\n"
        "def main(argv):\n"
        "    sys.stdout.write('argv=%s\\n' % ' '.join(argv))\n"
        "    sys.stdout.write('stdin=%s' % sys.stdin.read())\n"
        "    sys.stdout.write('env=%s\\n' % os.environ.get('EXP_RUN_CLI_WORD', '<unset>'))\n"
        "    sys.stdout.write('cwd=%s\\n' % os.getcwd())\n"
        "    sys.stderr.write('planted: said its piece\\n')\n"
        "    return 4\n",
        module.__dict__,
    )
    return module


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
    module = types.ModuleType("exp_exiting")
    exec("def main(argv):\n    raise SystemExit(3)\n", module.__dict__)

    code, _, _ = run_cli(module, [])

    assert code == 3
