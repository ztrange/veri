import ast
import collections

import pytest

import test_skill_green_readers
import test_skill_red_readers


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_two_readers_audits_in_one_session_parse_each_test_file_once_2168(tests_py_index, monkeypatch):
    test_file = type(tests_py_index[0])
    index = [test_file(entry.path) for entry in tests_py_index if "SKILL" in entry.text][:3]
    parsed = collections.Counter()
    real_parse = ast.parse

    def spy(source, *args, **kwargs):
        for entry in index:
            if source is entry.text:
                parsed[entry.path.name] += 1
        return real_parse(source, *args, **kwargs)

    monkeypatch.setattr(ast, "parse", spy)
    test_skill_red_readers.test_every_remaining_case_reading_the_red_subsection_by_its_content_is_on_the_mechanical_allow_list(index)
    test_skill_green_readers.test_every_remaining_case_reading_the_green_subsection_by_its_content_is_on_the_mechanical_allow_list(index)

    assert len(index) == 3, "the real test tree has fewer than three files naming SKILL"
    assert parsed == {entry.path.name: 1 for entry in index}, f"parses per test file: {dict(parsed)}"


@pytest.fixture(scope="session")
def _index_held_by_a_session_consumer(tests_py_index):
    return tests_py_index


@pytest.mark.tree_audit("every test file under skills/tdd/scripts/tests/py")
def test_a_session_scoped_consumer_and_a_case_get_the_one_index_object_of_the_process_2168(
        _index_held_by_a_session_consumer, tests_py_index):
    """Pins the fixture's session scope by behaviour: a session-scoped consumer may hold it only if it lives as long
    as the process (pytest refuses a narrower one with ScopeMismatch), and every case then gets that same object,
    so its entries' lazy parses happen once per process however many audits read them."""
    assert _index_held_by_a_session_consumer is tests_py_index
