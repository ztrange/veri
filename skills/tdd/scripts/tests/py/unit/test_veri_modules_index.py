"""The veri_modules_index fixture: every module of veri/ read and parsed once per session, for the audits that sweep them."""
import ast

import pytest

from conftest import SCRIPTS


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_the_index_names_every_python_module_of_veri_by_its_stem(veri_modules_index):
    expected = sorted(p.stem for p in (SCRIPTS / "veri").glob("*.py"))

    assert list(veri_modules_index.names) == expected
    assert "event_log" in veri_modules_index.names


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_a_module_is_asked_for_by_its_stem_for_its_path_text_and_tree(veri_modules_index):
    path = SCRIPTS / "veri" / "event_log.py"

    assert veri_modules_index.path("event_log") == path
    assert veri_modules_index.text("event_log") == path.read_text(encoding="utf-8")
    assert ast.dump(veri_modules_index.tree("event_log")) == ast.dump(ast.parse(path.read_text(encoding="utf-8")))


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_a_modules_tree_is_parsed_once_however_many_audits_ask(veri_modules_index):
    assert veri_modules_index.tree("event_log") is veri_modules_index.tree("event_log")


@pytest.fixture(scope="session")
def _index_held_by_a_session_consumer(veri_modules_index):
    return veri_modules_index


@pytest.mark.tree_audit("every module of skills/tdd/scripts/veri")
def test_a_session_scoped_consumer_and_a_case_get_the_one_index_object_of_the_process(
        _index_held_by_a_session_consumer, veri_modules_index):
    assert _index_held_by_a_session_consumer is veri_modules_index


def test_an_index_over_a_planted_directory_lists_only_its_python_modules_and_names_an_unknown_one(tmp_path):
    from tree_index import VeriModules

    (tmp_path / "b.py").write_text("'''b.'''\n")
    (tmp_path / "a.py").write_text("x = 1\n")
    (tmp_path / "README.md").write_text("not a module\n")
    index = VeriModules(tmp_path)

    assert list(index.names) == ["a", "b"]
    with pytest.raises(KeyError, match="nope"):
        index.text("nope")
