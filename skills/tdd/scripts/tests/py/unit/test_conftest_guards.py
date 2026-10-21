"""The guards conftest.py enforces, driven in-process through pytester with conftest as a plugin."""
import pathlib

import conftest

pytest_plugins = ["pytester"]


def test_the_no_test_runner_guard_fails_a_planted_case_that_starts_pytest_or_a_bash_suite_naming_the_case_and_command(pytester):
    pytester.makepyfile(test_planted="""
        import subprocess

        def test_starts_pytest():
            subprocess.run(["python3", "-m", "pytest", "inner_probe.py"])

        def test_starts_suite():
            subprocess.run(["bash", "skills/tdd/scripts/tests/inner.test.sh"])
    """)

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=2)
    output = result.stdout.str()
    assert "test_planted.py::test_starts_pytest starts pytest: python3 -m pytest inner_probe.py" in output
    assert "test_planted.py::test_starts_suite starts a bash suite: bash skills/tdd/scripts/tests/inner.test.sh" in output


def test_the_no_test_runner_guard_fails_a_planted_case_that_starts_git_with_dash_c_on_the_repository_or_from_the_module_directory_naming_the_case_and_path(pytester):
    repository = pathlib.Path(conftest.__file__).resolve().parents[5]
    module_directory = pathlib.Path(conftest.__file__).resolve().parents[3] / "veri"
    pytester.makepyfile(test_planted="""
        import subprocess

        def test_starts_git_with_dash_c():
            subprocess.run(["git", "-C", %r, "status"])

        def test_starts_git_from_the_module_directory():
            subprocess.run(["git", "status"], cwd=%r)
    """ % (str(repository), str(module_directory)))

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=2)
    output = result.stdout.str()
    assert "test_planted.py::test_starts_git_with_dash_c starts git against the repository the tests live in: %s (git -C %s status)" % (repository, repository) in output
    assert "test_planted.py::test_starts_git_from_the_module_directory starts git against the repository the tests live in: %s (git status)" % module_directory in output
