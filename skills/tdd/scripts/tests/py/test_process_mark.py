"""The size marker conftest.py gives every suite under tests/py, read through a planted case collected in-process."""
import importlib

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
