"""The size marker conftest.py gives every suite under tests/py, read through a planted case collected in-process."""
import importlib
import pathlib
import re

import pytest

pytest_plugins = ("pytester",)


def test_a_process_mark_with_no_boundary_or_an_empty_one_fails_collection_naming_the_test(pytester):
    pytester.makepyfile(test_plant="""
        import pytest

        @pytest.mark.process
        def test_bare_process_mark():
            pass

        @pytest.mark.process("")
        def test_empty_process_mark():
            pass
    """)

    result = pytester.runpytest_inprocess(plugins=[importlib.import_module("conftest")])
    output = result.stdout.str() + result.stderr.str()

    assert result.ret not in (pytest.ExitCode.OK, pytest.ExitCode.TESTS_FAILED), output
    assert "passed" not in result.parseoutcomes(), output
    assert [name for name in ("test_bare_process_mark", "test_empty_process_mark") if name not in output] == [], output


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
    makefile = (pathlib.Path(__file__).resolve().parents[5] / "Makefile").read_text()
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
