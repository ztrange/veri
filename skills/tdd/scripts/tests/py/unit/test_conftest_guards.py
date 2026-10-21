"""The guards conftest.py enforces, driven in-process through pytester with conftest as a plugin."""
import os
import pathlib
import subprocess

import conftest
import small_case_guard

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


def test_the_small_case_guard_fails_a_planted_unmarked_case_that_starts_git_naming_the_case_before_any_process_starts_while_a_process_marked_case_is_not_refused(pytester, monkeypatch):
    started = []

    def record(self, args, *rest, **kwargs):
        started.append(list(args))

    monkeypatch.setattr(subprocess.Popen, "__init__", record)
    pytester.makepyfile(test_planted="""
        import subprocess
        import pytest

        def test_starts_git_unmarked():
            subprocess.Popen(["git", "--version"])

        @pytest.mark.process("git as a child")
        def test_starts_git_marked():
            subprocess.Popen(["git", "--version"])
    """)

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", "-rf", plugins=[conftest, small_case_guard])

    result.assert_outcomes(failed=1, passed=1)
    assert "FAILED test_planted.py::test_starts_git_unmarked - AssertionError: a small case started git" in result.stdout.str()
    assert started == [["git", "--version"]]


def test_the_permission_bits_guard_fails_a_planted_case_that_chmods_a_file_naming_the_file_and_line_and_a_reasonless_or_caseless_exemption_fails_the_run_while_a_good_one_passes(pytester, monkeypatch):
    source = (
        "import os\n"
        "\n"
        "def test_takes_bits(tmp_path):\n"
        "    victim = tmp_path / 'victim'\n"
        "    victim.write_text('x')\n"
        "    os.chmod(victim, 0o444)\n"
    )
    line = source.splitlines().index("    os.chmod(victim, 0o444)") + 1
    path = pytester.makepyfile(test_planted=source)

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=1)
    output = result.stdout.str()
    assert "test_planted.py::test_takes_bits takes permission bits off" in output
    assert "victim with chmod at %s:%d" % (path, line) in output

    exempt = "test_planted.py::test_takes_bits"
    monkeypatch.setitem(conftest.PERMISSION_BITS_EXEMPT, exempt, "")
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])
    assert "permission-bits exemption table: %s: exemption carries no reason" % exempt in result.stderr.str()

    monkeypatch.setitem(conftest.PERMISSION_BITS_EXEMPT, exempt, "the case plants the chmod")
    monkeypatch.setitem(conftest.PERMISSION_BITS_EXEMPT, "test_planted.py::test_gone", "names nothing")
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])
    assert "test_planted.py::test_gone: exemption names no existing case" in result.stderr.str()

    monkeypatch.delitem(conftest.PERMISSION_BITS_EXEMPT, "test_planted.py::test_gone")
    monkeypatch.setattr(os, "chmod", lambda *args, **kwargs: None)
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])
    result.assert_outcomes(passed=1)


def test_the_system_location_guard_fails_planted_cases_that_read_mkdir_or_create_a_system_location_naming_the_file_and_line_while_tmp_and_tempfile_cases_pass_and_a_reasonless_exemption_fails_the_run(pytester, monkeypatch):
    calls = {
        "reads": "open('/etc/veri-planted').read()",
        "mkdirs": "os.mkdir('/veri-planted')",
        "creates": "os.open('/etc/veri-planted', os.O_CREAT | os.O_WRONLY)",
        "reads_through_pathlib": "pathlib.Path('/etc/veri-planted').read_text()",
        "mkdirs_through_pathlib": "pathlib.Path('/veri-planted').mkdir()",
    }
    source = "import os\nimport pathlib\nimport tempfile\n\n"
    for name, call in calls.items():
        source += "def test_%s():\n    %s\n\n" % (name, call)
    source += (
        "def test_creates_under_tmp(tmp_path):\n"
        "    made = pathlib.Path('/tmp') / ('veri-planted-' + str(os.getpid()))\n"
        "    made.mkdir()\n"
        "    made.rmdir()\n"
        "\n"
        "def test_opens_a_tempfile():\n"
        "    with tempfile.TemporaryFile() as handle:\n"
        "        handle.write(b'x')\n"
    )
    lines = source.splitlines()
    path = pytester.makepyfile(test_planted=source)

    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])

    result.assert_outcomes(failed=len(calls), passed=2)
    output = result.stdout.str()
    for name, call in calls.items():
        line = lines.index("    " + call) + 1
        assert "the system location" in output
        assert "at %s:%d" % (path, line) in output
        assert "test_planted.py::test_%s " % name in output

    exempt = "test_planted.py::test_reads"
    monkeypatch.setitem(conftest.SYSTEM_LOCATION_EXEMPT, exempt, "")
    result = pytester.runpytest_inprocess("-p", "no:cacheprovider", plugins=[conftest])
    assert "system-location exemption table: %s: exemption carries no reason" % exempt in result.stderr.str()
