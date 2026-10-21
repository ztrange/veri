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


def test_the_directory_listing_guard_fails_a_planted_unmarked_case_that_lists_a_repository_directory_naming_the_case_while_a_tree_audit_mark_passes(pytester):
    repository = pathlib.Path(conftest.__file__).resolve().parents[5]
    pytester.makepyfile(test_planted="""
        import os
        import pytest

        def test_lists_unmarked():
            os.listdir(%r)

        @pytest.mark.tree_audit("the repository root")
        def test_lists_marked():
            os.listdir(%r)
    """ % (str(repository), str(repository)))

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=1, passed=1)
    output = result.stdout.str()
    assert "test_planted.py::test_lists_unmarked lists the repository directory %s: mark it tree_audit" % repository in output
    assert "test_lists_marked lists" not in output


def test_the_push_backoff_guard_fails_a_planted_small_case_that_reaches_the_retry_backoff_without_veri_push_backoff_naming_the_case(pytester):
    pytester.makepyfile(test_planted="""
        import subprocess

        def test_waits_the_default_backoff(monkeypatch):
            import veri.push_branch as push_branch

            def fake_run(args, **kwargs):
                return subprocess.CompletedProcess(args, 1, stdout="boom\\n")

            monkeypatch.setattr(subprocess, "run", fake_run)
            push_branch.main([])
    """)

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=1)
    assert "test_planted.py::test_waits_the_default_backoff reached the push backoff without setting VERI_PUSH_BACKOFF" in result.stdout.str()
