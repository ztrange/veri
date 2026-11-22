"""In-process cases for veri/case_identity.py: when a case in the current tree is "the same case" as a recorded one.

Pure-text rules take strings; the rules that ask the history run against a faked case_history; the ones that
look for a moved file run inside tmp_path. No case starts git or a process."""
import importlib

import pytest


@pytest.fixture
def case_identity(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    return importlib.import_module("veri.case_identity")


@pytest.fixture
def digest():
    return importlib.import_module("veri.frozen_record").body_digest


PY_HELPER = "def check_one(x):\n    assert x == 1\n\n\n"
PY_CASE = "def test_a():\n    check_one(1)\n"


def test_squeezed_drops_every_run_of_whitespace(case_identity):
    assert case_identity.squeezed(" a \t b\n\n c ") == "abc"


def test_assertion_lines_keeps_the_assert_expect_and_go_check_lines_squeezed_and_nothing_else(case_identity):
    body = "def test_a():\n    x = 1\n    assert  x == 1\n  expect(x).toBe(1)\n\tt.Fatal(\"no\")\n    require.Equal(t, 1, x)\n"

    assert case_identity.assertion_lines(body) == ["assertx==1", "expect(x).toBe(1)", 't.Fatal("no")',
                                                   "require.Equal(t,1,x)"]


def test_bodies_of_lists_every_same_named_case_in_order_and_none_for_an_unknown_name(case_identity):
    text = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"

    assert case_identity.bodies_of(text, "test_b") == ["def test_b():\n    assert 2"]
    assert case_identity.bodies_of(text, "test_missing") == []


def test_helpers_in_returns_the_definition_of_a_helper_the_body_calls_up_to_the_next_definition(case_identity):
    text = PY_HELPER + PY_CASE

    assert case_identity.helpers_in(text, PY_CASE) == PY_HELPER


def test_helpers_in_ignores_a_helper_the_body_never_calls_and_a_test_function_the_body_calls(case_identity):
    text = "def other():\n    assert 0\n\n\ndef test_b():\n    assert 2\n\n\ndef test_a():\n    test_b()\n"

    assert case_identity.helpers_in(text, "def test_a():\n    test_b()\n") == ""


def test_helpers_in_never_collects_a_go_test_function_but_collects_a_go_helper(case_identity):
    text = ("func TestB(t *testing.T) {\n\tt.Fatal(\"b\")\n}\n\nfunc helper(t *testing.T) {\n\tt.Fatal(\"h\")\n}\n\n"
            "func TestA(t *testing.T) {\n\tTestB(t)\n\thelper(t)\n}\n")

    assert case_identity.helpers_in(text, "func TestA(t *testing.T) {\n\tTestB(t)\n\thelper(t)\n}\n") == (
        "func helper(t *testing.T) {\n\tt.Fatal(\"h\")\n}\n\n")


def test_helpers_in_legacy_ends_a_helper_only_at_a_go_func_so_a_python_helper_swallows_the_next_def(case_identity):
    text = "def one():\n    assert 1\n\n\ndef two():\n    assert 2\n\n\ndef test_a():\n    one()\n"
    body = "def test_a():\n    one()\n"

    assert (case_identity.helpers_in(text, body), case_identity.helpers_in(text, body, legacy=True)) == (
        "def one():\n    assert 1\n\n\n", text)


@pytest.mark.parametrize("opener", ["const sharedBase = () => {", "const sharedBase = async () => {",
                                    "const sharedBase = x => {"])
def test_helpers_in_takes_an_arrow_const_the_body_calls_for_a_helper(case_identity, opener):
    helper = opener + "\n  expect(x).toBe(1);\n};\n"
    body = "it('one', () => {\n  sharedBase();\n});\n"

    assert case_identity.helpers_in(body + helper, body) == helper


@pytest.mark.parametrize("definition", ["const y = 2;\n", "let sharedBase = 1;\n", "return sharedBase;\n",
                                        "const sharedBase = wrap(() => {\n  expect(x).toBe(9);\n});\n"])
def test_helpers_in_takes_neither_a_non_arrow_const_nor_a_let_or_return_line_for_a_helper(case_identity, definition):
    text = definition + "it('one', () => {\n  sharedBase();\n});\n"

    assert case_identity.helpers_in(text, "it('one', () => {\n  sharedBase();\n});\n") == ""


@pytest.mark.parametrize("word", ["constants", "functional"])
def test_helpers_in_does_not_end_a_helper_at_a_column_0_line_that_merely_starts_with_a_keyword(case_identity, word):
    helper = "const sharedBase = () => {\n  expect(x).toBe(1);\n%s\n  expect(x).toBe(3);\n};\n" % word
    body = "it('one', () => {\n  sharedBase();\n});\n"

    assert case_identity.helpers_in(body + helper, body) == helper


def test_helpers_in_does_not_count_the_assertions_of_a_function_after_the_helper_as_the_helpers(case_identity):
    helper = "function sharedBase() {\n  expect(x).toBe(1);\n}\n"
    text = helper + "function unrelated() {\n  expect(x).toBe(9);\n}\n"

    assert case_identity.helpers_in(text, "it('one', () => {\n  sharedBase();\n});\n") == helper


def test_helper_digest_is_the_body_digest_of_the_sorted_squeezed_assertion_lines_of_the_called_helpers(
        case_identity, digest):
    text = "def check(x):\n    assert  x == 2\n    assert x == 1\n\n\n" + PY_CASE.replace("check_one", "check")
    body = PY_CASE.replace("check_one", "check")

    assert case_identity.helper_digest(text, body) == digest("assertx==1\nassertx==2")


def test_helper_digest_ignores_the_order_of_a_helpers_assertion_lines_and_sees_a_deleted_one(case_identity):
    body = "def test_a():\n    check()\n"
    ordered = "def check():\n    assert 1\n    assert 2\n\n\n" + body
    reordered = "def check():\n    assert 2\n    assert 1\n\n\n" + body
    deleted = "def check():\n    assert 2\n\n\n" + body

    digests = [case_identity.helper_digest(text, body) for text in (ordered, reordered, deleted)]

    assert (digests[0] == digests[1], digests[0] == digests[2]) == (True, False)


def test_helper_digest_legacy_differs_from_the_current_one_when_a_python_helper_is_followed_by_another_def(
        case_identity):
    text = "def one():\n    assert 1\n\n\ndef two():\n    assert 2\n\n\ndef test_a():\n    one()\n"
    body = "def test_a():\n    one()\n"

    assert case_identity.helper_digest(text, body) != case_identity.helper_digest(text, body, legacy=True)


def test_root_variants_yields_the_body_then_its_parents_lookup_at_each_depth_0_to_9(case_identity):
    variants = list(case_identity.root_variants("root = Path(__file__).parents[4]"))

    assert variants == ["root = Path(__file__).parents[4]"] + [
        "root = Path(__file__).parents[%d]" % k for k in range(10)]


def test_as_recorded_returns_the_variant_whose_digest_was_recorded_else_the_body_itself(case_identity, digest):
    body = "root = Path(__file__).parents[5]"
    recorded = {digest("root = Path(__file__).parents[4]")}

    assert case_identity.as_recorded(body, recorded) == "root = Path(__file__).parents[4]"
    assert case_identity.as_recorded(body, {digest("something else")}) == body


MOVED = "def test_moved_3284():\n    assert 1 == 1\n"


def _recorded(digest, text, case="test_moved_3284"):
    return {digest(body) for body in importlib.import_module("veri.case_identity").bodies_of(text, case)}


def _write(tmp_path, relative, text):
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_moved_path_is_the_name_itself_while_that_file_exists_even_when_a_copy_elsewhere_holds_the_case(
        case_identity, digest, tmp_path):
    _write(tmp_path, "tests/moved_cases.py", "def test_other():\n    assert True\n")
    _write(tmp_path, "tests/unit/moved_cases.py", MOVED)

    assert case_identity.moved_path("tests/moved_cases.py", "test_moved_3284", _recorded(digest, MOVED)) == (
        "./tests/unit/moved_cases.py")


def test_moved_path_finds_a_file_of_the_same_basename_in_another_directory_that_holds_the_recorded_case(
        case_identity, digest, tmp_path):
    _write(tmp_path, "tests/unit/moved_cases.py", MOVED)

    assert case_identity.moved_path("tests/moved_cases.py", "test_moved_3284", _recorded(digest, MOVED)) == (
        "./tests/unit/moved_cases.py")


def test_moved_path_finds_a_file_of_another_basename_when_none_of_the_same_basename_holds_the_case(
        case_identity, digest, tmp_path):
    _write(tmp_path, "moved_cases.py", "def test_unrelated():\n    assert True\n")
    _write(tmp_path, "tests/unit/renamed_cases.py", MOVED)

    assert case_identity.moved_path("tests/moved_cases.py", "test_moved_3284", _recorded(digest, MOVED)) == (
        "./tests/unit/renamed_cases.py")


def test_moved_path_ignores_a_copy_in_a_hidden_directory_and_answers_the_name(case_identity, digest, tmp_path):
    _write(tmp_path, ".hidden/gone_cases.py", MOVED)

    assert case_identity.moved_path("tests/gone_cases.py", "test_moved_3284", _recorded(digest, MOVED)) == (
        "tests/gone_cases.py")


def test_moved_path_answers_the_name_when_the_moved_case_body_changed_since_the_record(case_identity, digest, tmp_path):
    _write(tmp_path, "tests/unit/moved_cases.py", MOVED.replace("1 == 1", "1 == 2"))

    assert case_identity.moved_path("tests/moved_cases.py", "test_moved_3284", _recorded(digest, MOVED)) == (
        "tests/moved_cases.py")


def test_moved_path_matches_a_case_whose_only_change_is_its_parents_root_lookup_depth(case_identity, digest, tmp_path):
    case = "def test_roots_3284():\n    root = Path(__file__).parents[4]\n    assert root.name\n"
    _write(tmp_path, "tests/unit/suite_cases.py", case.replace("parents[4]", "parents[5]"))

    assert case_identity.moved_path("tests/suite_cases.py", "test_roots_3284", _recorded(digest, case, "test_roots_3284")) == (
        "./tests/unit/suite_cases.py")


def test_path_holding_restricts_itself_to_the_given_basename_and_answers_none_when_nothing_holds_the_case(
        case_identity, digest, tmp_path):
    _write(tmp_path, "a/x_cases.py", "def test_other():\n    assert True\n")
    _write(tmp_path, "b/y_cases.py", MOVED)
    held = _recorded(digest, MOVED)

    assert (case_identity.path_holding("test_moved_3284", held, only="x_cases.py"),
            case_identity.path_holding("test_moved_3284", held, only="y_cases.py"),
            case_identity.path_holding("test_moved_3284", held)) == (None, "./b/y_cases.py", "./b/y_cases.py")


class History:
    """Stands in for case_history on one file: `versions` is {rev: source}, newest first; `subjects` {rev: subject}."""

    def __init__(self, monkeypatch, case_identity, versions, subjects=None):
        self.versions, self.subjects, self.quiet = versions, subjects or {}, []
        history = case_identity.case_history
        monkeypatch.setattr(history, "revisions", lambda path, since=None: list(self.versions))
        monkeypatch.setattr(history, "cases_at", self.cases_at)
        monkeypatch.setattr(history, "text_at", self.text_at)
        monkeypatch.setattr(history, "subject", lambda rev: self.subjects.get(rev, ""))

    def text_at(self, rev, path, quiet=False):
        self.quiet.append(quiet)
        return self.versions.get(rev, "")

    def cases_at(self, rev, path):
        if rev == "HEAD":
            rev = next(iter(self.versions))
        return dict(importlib.import_module("veri.case_reader").cut_cases(self.versions.get(rev, "")))


OLD = "def test_a():\n    assert 1 == 1\n"


def test_renamed_to_names_the_case_of_the_current_text_that_is_the_recorded_one_but_for_its_name(
        case_identity, digest, monkeypatch):
    History(monkeypatch, case_identity, {"r1": OLD})
    consumed = set()

    other = case_identity.renamed_to("f.py", "test_a", digest("def test_a():\n    assert 1 == 1"),
                                     "def test_b():\n    assert 1 == 1\n", consumed)

    assert (other, consumed) == ("test_b", {"test_b"})


def test_renamed_to_answers_none_when_no_revision_held_the_case_under_the_recorded_digest(
        case_identity, digest, monkeypatch):
    History(monkeypatch, case_identity, {"r1": OLD})

    assert case_identity.renamed_to("f.py", "test_a", digest("some other body"),
                                    "def test_b():\n    assert 1 == 1\n", set()) is None


def test_renamed_to_answers_none_for_a_renamed_case_whose_body_changed_with_its_name(
        case_identity, digest, monkeypatch):
    History(monkeypatch, case_identity, {"r1": OLD})
    consumed = set()

    other = case_identity.renamed_to("f.py", "test_a", digest("def test_a():\n    assert 1 == 1"),
                                     "def test_b():\n    assert 1 == 2\n", consumed)

    assert (other, consumed) == (None, set())


def test_renamed_to_skips_a_successor_an_earlier_rename_already_consumed(case_identity, digest, monkeypatch):
    History(monkeypatch, case_identity, {"r1": OLD})
    current = "def test_b():\n    assert 1 == 1\n\n\ndef test_c():\n    assert 1 == 1\n"
    consumed = {"test_b"}

    other = case_identity.renamed_to("f.py", "test_a", digest("def test_a():\n    assert 1 == 1"), current, consumed)

    assert (other, consumed) == ("test_c", {"test_b", "test_c"})


def test_renamed_to_uses_the_newest_revision_that_held_the_recorded_body(case_identity, digest, monkeypatch):
    History(monkeypatch, case_identity, {"r2": "def test_a():\n    assert 1 == 1\n\n\ndef test_b():\n    assert 2 == 2\n",
                                         "r1": "def test_a():\n    assert 0 == 0\n"})

    other = case_identity.renamed_to("f.py", "test_a", digest("def test_a():\n    assert 1 == 1"),
                                     "def test_c():\n    assert 1 == 1\n", set())

    assert other == "test_c"


def _refactor_history(monkeypatch, case_identity, bodies, subjects):
    versions = {rev: ("def test_a():\n    assert %s\n" % body) for rev, body in bodies.items()}
    return History(monkeypatch, case_identity, versions, subjects)


def test_changed_by_refactor_is_true_when_the_newest_revision_that_changed_the_case_is_a_refactor_commit(
        case_identity, monkeypatch):
    _refactor_history(monkeypatch, case_identity, {"r3": "x == 2", "r2": "x == 2", "r1": "x == 1"},
                      {"r3": "feat: later\n", "r2": "refactor: tidy the cases\n", "r1": "feat: first\n"})

    assert case_identity.changed_by_refactor("f.py", "test_a") is True


def test_changed_by_refactor_is_false_when_the_newest_change_was_not_a_refactor_even_if_an_older_one_was(
        case_identity, monkeypatch):
    _refactor_history(monkeypatch, case_identity, {"r3": "x == 3", "r2": "x == 2", "r1": "x == 1"},
                      {"r3": "fix: edit\n", "r2": "refactor: tidy\n", "r1": "feat: first\n"})

    assert case_identity.changed_by_refactor("f.py", "test_a") is False


def test_changed_by_refactor_is_false_for_a_case_no_revision_ever_changed_or_one_gone_from_head(
        case_identity, monkeypatch):
    _refactor_history(monkeypatch, case_identity, {"r2": "x == 1", "r1": "x == 1"},
                      {"r2": "refactor: tidy\n", "r1": "feat: first\n"})

    assert (case_identity.changed_by_refactor("f.py", "test_a"),
            case_identity.changed_by_refactor("f.py", "test_gone")) == (False, False)


def test_changed_by_refactor_is_false_when_the_history_cannot_be_read(case_identity, monkeypatch):
    def refuse(rev, path):
        raise OSError("git show failed")
    monkeypatch.setattr(case_identity.case_history, "cases_at", refuse)

    assert case_identity.changed_by_refactor("f.py", "test_a") is False


def test_called_helpers_reads_the_file_at_the_revision_quietly_and_returns_the_helpers_the_body_calls(
        case_identity, monkeypatch):
    history = History(monkeypatch, case_identity, {"r1": PY_HELPER + PY_CASE})

    assert (case_identity.called_helpers("r1", "f.py", PY_CASE), history.quiet) == (PY_HELPER, [True])
