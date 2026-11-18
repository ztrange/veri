"""In-process cases for veri/case_reader.py."""
import importlib

import pytest


def test_strip_param_suffix_strips_a_trailing_bracket_and_leaves_a_plain_name_unchanged():
    case_reader = importlib.import_module("veri.case_reader")

    assert case_reader.strip_param_suffix("test_x[a-b]") == "test_x"
    assert case_reader.strip_param_suffix("test_x") == "test_x"


def test_file_defines_with_classes_answers_for_the_class_chain_and_only_its_own_methods(tmp_path):
    case_reader = importlib.import_module("veri.case_reader")
    source = tmp_path / "test_x.py"
    source.write_text("class TestK:\n    def test_b(self):\n        pass\n\n    class TestInner:\n"
                      "        def test_c(self):\n            pass\n\n\ndef test_a():\n    pass\n")
    broken = tmp_path / "test_broken.py"
    broken.write_text("class TestK:\n    def test_b(self:\n")

    answers = {args: case_reader.file_defines(str(source), args[1], args[0]) for args in (
        (("TestK",), "test_b"), (("TestK",), "test_a"), (("TestNope",), "test_a"),
        (("TestK", "TestInner"), "test_c"), (("TestInner",), "test_c"))}
    assert answers == {
        (("TestK",), "test_b"): True, (("TestK",), "test_a"): False, (("TestNope",), "test_a"): False,
        (("TestK", "TestInner"), "test_c"): True, (("TestInner",), "test_c"): False}
    assert case_reader.file_defines(str(broken), "test_b", ("TestK",)) is False


def test_cut_cases_4050_reads_no_name_line_as_a_case():
    case_reader = importlib.import_module("veri.case_reader")

    assert case_reader.cut_cases('name="a bash case"\n') == []


def test_cut_cases_cuts_a_case_holding_a_regex_literal_with_a_paren_at_its_own_closing_call_4294():
    case_reader = importlib.import_module("veri.case_reader")
    text = ("it('b', () => {\n  const r = /\\(/;\n  expect(r.test('(')).toBe(true);\n});\n"
            "it('c', () => {\n  expect(1).toBe(1);\n});\n")

    cases = case_reader.cut_cases(text)

    assert cases == [("b", "it('b', () => {\n  const r = /\\(/;\n  expect(r.test('(')).toBe(true);\n})"),
                     ("c", "it('c', () => {\n  expect(1).toBe(1);\n})")]


@pytest.mark.parametrize("division", ["a / b", "f(x) / 2", "arr[0] / 2", "a$ / 2"])
def test_cut_cases_still_cuts_a_case_holding_a_division_and_a_line_comment_as_before_4294(division):
    case_reader = importlib.import_module("veri.case_reader")
    first = "it('d', () => {\n  const q = %s;\n  // ) closes nothing\n  expect(q).toBe(q);\n})" % division
    second = "it('e', () => {\n  expect(1).toBe(1);\n})"

    cases = case_reader.cut_cases(first + ";\n" + second + ";\n")

    assert cases == [("d", first), ("e", second)]


def test_cut_cases_returns_every_case_when_one_returns_a_quote_bearing_regex_before_a_string_holding_a_brace_4294():
    case_reader = importlib.import_module("veri.case_reader")
    first = ("it('f', () => {\n  const pick = () => { return /'/; };\n  expect(pick().test('a}')).toBe(false);\n"
             "  expect('}}').toBe('}}');\n})")
    divides = "it('d', () => {\n  const q = unreturn / 2;\n  // ) closes nothing\n  expect(q).toBe(q);\n})"
    second = "it('g', () => {\n  expect(1).toBe(1);\n})"

    cases = case_reader.cut_cases(first + ";\n" + divides + ";\n" + second + ";\n")

    assert cases == [("f", first), ("d", divides), ("g", second)]


def test_cut_cases_reads_an_escaped_slash_inside_a_regex_literal_as_part_of_it_4294():
    case_reader = importlib.import_module("veri.case_reader")
    first = "it('h', () => {\n  const r = /\\/(/;\n  expect(r.test('/(')).toBe(true);\n})"
    second = "it('i', () => {\n  expect(1).toBe(1);\n})"

    cases = case_reader.cut_cases(first + ";\n" + second + ";\n")

    assert cases == [("h", first), ("i", second)]


def test_cut_cases_reads_a_slash_inside_a_regex_character_class_as_part_of_it_4294():
    case_reader = importlib.import_module("veri.case_reader")
    first = "it('j', () => {\n  const r = /[/(]/;\n  expect(r.test('(')).toBe(true);\n})"
    second = "it('k', () => {\n  expect(1).toBe(1);\n})"

    cases = case_reader.cut_cases(first + ";\n" + second + ";\n")

    assert cases == [("j", first), ("k", second)]


def test_cut_cases_reads_a_slash_with_no_closing_slash_on_its_line_as_a_division_4294():
    case_reader = importlib.import_module("veri.case_reader")
    first = "it('l', () => {\n  let n = 1;\n  const q = n++ / 2;\n  // ) closes nothing\n  expect(q).toBe(0.5);\n})"
    second = "it('m', () => {\n  expect(1).toBe(1);\n})"

    cases = case_reader.cut_cases(first + ";\n" + second + ";\n")

    assert cases == [("l", first), ("m", second)]
