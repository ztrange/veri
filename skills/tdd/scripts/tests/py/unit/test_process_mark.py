"""The size marker conftest.py gives every suite under tests/py, read through a planted case collected in-process."""
import importlib
import pathlib
import re

import pytest

pytest_plugins = ("pytester",)


def unnamed_marks_fail_collection(pytester, mark):
    pytester.makepyfile(test_plant="""
        import pytest

        @pytest.mark.MARK
        def test_bare_MARK_mark():
            pass

        @pytest.mark.MARK("")
        def test_empty_MARK_mark():
            pass

        @pytest.mark.MARK(" \\t ")
        def test_blank_MARK_mark():
            pass
    """.replace("MARK", mark))

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.ret not in (pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED), output
    assert [name for name in ("test_%s_%s_mark" % (kind, mark) for kind in ("bare", "empty", "blank")) if name not in output] == [], output
    return result, output


def test_a_process_mark_with_no_boundary_or_an_empty_one_fails_collection_naming_the_test(pytester):
    result, output = unnamed_marks_fail_collection(pytester, "process")

    assert "passed" not in result.parseoutcomes(), output


def test_a_tree_audit_mark_with_no_argument_or_an_empty_one_fails_collection_naming_the_test(pytester):
    result, output = unnamed_marks_fail_collection(pytester, "tree_audit")

    assert "passed" not in result.parseoutcomes(), output


def test_an_unregistered_mark_fails_collection_naming_the_test_and_the_mark_while_process_is_registered(pytester):
    pytester.makepyfile(
        test_unregistered="""
            import pytest

            @pytest.mark.unregistered_size
            def test_with_unregistered_mark():
                pass
        """,
        test_registered="""
            import pytest

            @pytest.mark.process("git rebase conflict text")
            def test_with_process_mark():
                pass
        """,
    )

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.ret not in (pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED), output
    assert [name for name in ("test_with_unregistered_mark", "unregistered_size") if name not in output] == [], output
    assert "'process' not found" not in output, output


def test_a_tree_audit_mark_is_registered_and_make_units_selection_deselects_it_beside_process_cases(pytester):
    makefile = (pathlib.Path(__file__).resolve().parents[6] / "Makefile").read_text()
    selection = re.search(r'^unit: PY_SELECT = -m "([^"]*)"$', makefile, re.M).group(1)
    pytester.makepyfile(test_plant="""
        import pytest

        @pytest.mark.tree_audit("every bash suite")
        def test_sweeps_the_tree():
            pass

        @pytest.mark.process("a real pipe")
        def test_starts_a_process():
            pass

        def test_stays_small():
            pass
    """)

    result = pytester.runpytest_inprocess("-m", selection, plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.ret == pytest.ExitCode.OK, output
    assert result.parseoutcomes() == {"passed": 1, "deselected": 2}, output


def test_an_unmarked_case_that_lists_a_repository_directory_fails_naming_the_case_and_the_directory_while_a_marked_one_a_named_file_and_an_import_pass(pytester):
    root = pathlib.Path(__file__).resolve().parents[6]
    pytester.makepyfile(test_plant="""
        import pathlib

        import pytest

        ROOT = pathlib.Path(%r)

        def test_globs_the_scripts_directory():
            assert list((ROOT / "skills" / "tdd" / "scripts").glob("*.sh"))

        @pytest.mark.tree_audit("every script")
        def test_marked_globs_the_scripts_directory():
            assert list((ROOT / "skills" / "tdd" / "scripts").glob("*.sh"))

        def test_reads_one_named_file():
            assert (ROOT / "CLAUDE.md").read_text()

        def test_imports_a_module():
            import json
            assert json.dumps(1) == "1"
    """ % str(root))

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.parseoutcomes() == {"passed": 3, "failed": 1}, output
    assert [name for name in ("test_globs_the_scripts_directory", "skills/tdd/scripts") if name not in output] == [], output


def test_an_unmarked_case_that_drives_a_module_which_lists_a_repository_directory_fails_naming_the_case_and_the_directory_while_the_marked_case_passes(pytester):
    root = pathlib.Path(__file__).resolve().parents[6]
    pytester.makepyfile(sweeper="""
        import pathlib

        def count_scripts(root):
            return len(list((pathlib.Path(root) / "skills" / "tdd" / "scripts").iterdir()))
    """)
    pytester.makepyfile(test_plant="""
        import pytest

        import sweeper

        ROOT = %r

        def test_drives_the_sweeping_module():
            assert sweeper.count_scripts(ROOT)

        @pytest.mark.tree_audit("every script")
        def test_marked_drives_the_sweeping_module():
            assert sweeper.count_scripts(ROOT)
    """ % str(root))

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.parseoutcomes() == {"passed": 1, "failed": 1}, output
    assert [name for name in ("test_drives_the_sweeping_module", "skills/tdd/scripts") if name not in output] == [], output


def test_a_serial_mark_with_no_reason_or_a_blank_one_fails_collection_naming_the_test_and_the_missing_reason_2092(pytester):
    _, output = unnamed_marks_fail_collection(pytester, "serial")

    assert "unregistered mark" not in output, output
    assert "serial mark without a reason" in output, output
