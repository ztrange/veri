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
