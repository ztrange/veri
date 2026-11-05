"""In-process cases for veri/renamed_case.py."""
from veri import renamed_case


def test_renamed_to_returns_the_new_name_of_a_go_func_test_case_renamed_with_its_body_unchanged():
    old = 'func TestAdd(t *testing.T) {\n\tif Add(1, 2) != 3 {\n\t\tt.Fatal("bad")\n\t}\n}\n'
    new = old.replace("TestAdd", "TestSum")

    assert renamed_case.renamed_to("TestAdd", old, new, set()) == "TestSum"


def test_renamed_to_returns_the_new_title_of_a_js_it_case_renamed_with_its_body_unchanged():
    old = 'it("adds two numbers", () => {\n  expect(add(1, 2)).toBe(3);\n});\n'
    new = old.replace("adds two numbers", "sums two numbers")

    assert renamed_case.renamed_to("adds two numbers", old, new, set()) == "sums two numbers"


def test_renamed_to_returns_the_new_title_of_a_js_test_case_renamed_with_its_body_unchanged():
    old = 'test("adds two numbers", () => {\n  expect(add(1, 2)).toBe(3);\n});\n'
    new = old.replace("adds two numbers", "sums two numbers")

    assert renamed_case.renamed_to("adds two numbers", old, new, set()) == "sums two numbers"


def test_renamed_to_returns_the_new_title_of_an_indented_js_case_with_single_quote_or_backtick_title():
    old = ("describe('math', () => {\n"
           "  it('adds', () => {\n    expect(add(1, 2)).toBe(3);\n  });\n\n"
           "  test(`subtracts`, () => {\n    expect(sub(3, 1)).toBe(2);\n  });\n"
           "});\n")
    new = old.replace("adds", "sums").replace("subtracts", "takes away")

    assert renamed_case.renamed_to("adds", old, new, set()) == "sums"
    assert renamed_case.renamed_to("subtracts", old, new, set()) == "takes away"


def test_renamed_and_changed_to_returns_the_new_name_of_a_go_func_test_case_renamed_with_its_body_changed():
    old = 'func TestAdd(t *testing.T) {\n\tif Add(1, 2) != 3 {\n\t\tt.Fatal("bad")\n\t}\n}\n'
    new = 'func TestSum(t *testing.T) {\n\tif Add(2, 2) != 4 {\n\t\tt.Fatal("bad")\n\t}\n}\n'

    assert renamed_case.renamed_to("TestAdd", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("TestAdd", old, new, set()) == "TestSum"


def test_renamed_and_changed_to_returns_the_new_title_of_a_js_it_case_renamed_with_its_body_changed():
    old = 'it("adds two numbers", () => {\n  expect(add(1, 2)).toBe(3);\n});\n'
    new = 'it("sums two numbers", () => {\n  expect(add(2, 2)).toBe(4);\n});\n'

    assert renamed_case.renamed_to("adds two numbers", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("adds two numbers", old, new, set()) == "sums two numbers"


def test_a_js_case_renamed_with_its_closing_call_line_changed_is_not_a_pure_rename():
    old = 'it("a", () => {\n  expect(add(1, 2)).toBe(3);\n});\n'
    new = 'it("b", () => {\n  expect(add(1, 2)).toBe(3);\n}, 5000);\n'

    assert renamed_case.renamed_to("a", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("a", old, new, set()) == "b"


def test_a_renamed_go_func_that_is_not_a_test_is_not_recognised_as_a_case_rename():
    old = 'func helper() {\n\tdo()\n}\n'
    new = old.replace("helper", "assist")

    assert renamed_case.renamed_to("helper", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("helper", old, new, set()) is None


def test_an_indented_go_func_test_is_not_taken_as_a_case_head():
    old = 'x := `\n  func TestAdd(t *testing.T) {\n\tdo()\n  }\n`\n'
    new = old.replace("TestAdd", "TestSum")

    assert renamed_case.renamed_to("TestAdd", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("TestAdd", old, new, set()) is None


def test_an_indented_js_case_renamed_with_its_indented_closing_call_line_changed_is_not_a_pure_rename():
    old = 'describe("m", () => {\n  it("a", () => {\n    expect(add(1, 2)).toBe(3);\n  });\n});\n'
    new = 'describe("m", () => {\n  it("b", () => {\n    expect(add(1, 2)).toBe(3);\n  }, 5000);\n});\n'

    assert renamed_case.renamed_to("a", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("a", old, new, set()) == "b"


def test_a_js_case_at_end_of_file_with_no_closing_line_is_a_pure_rename():
    old = 'it("a", () => {\n  expect(add(1, 2)).toBe(3);'
    new = old.replace('"a"', '"b"')

    assert renamed_case.renamed_to("a", old, new, set()) == "b"


def test_a_js_case_renamed_with_a_closing_line_starting_with_a_paren_changed_is_not_a_pure_rename():
    old = 'it("a", () =>\n  expect(add(1, 2)).toBe(3)\n);\n'
    new = 'it("b", () =>\n  expect(add(1, 2)).toBe(3)\n), 5000);\n'

    assert renamed_case.renamed_to("a", old, new, set()) is None
    assert renamed_case.renamed_and_changed_to("a", old, new, set()) == "b"


def test_a_one_line_js_case_followed_by_its_suites_closing_line_changed_is_still_a_pure_rename():
    old = 'describe("m", () => {\n  it("a", () => expect(1).toBe(1));\n});\n'
    new = 'describe("m", () => {\n  it("b", () => expect(1).toBe(1));\n}, 5000);\n'

    assert renamed_case.renamed_to("a", old, new, set()) == "b"


def test_a_js_case_with_a_closing_line_is_unaffected_by_a_changed_line_after_it():
    old = 'it("a", () => {\n  expect(1).toBe(1);\n});\nit("c", () => {});\n'
    new = 'it("b", () => {\n  expect(1).toBe(1);\n});\nit("d", () => {});\n'

    assert renamed_case.renamed_to("a", old, new, set()) == "b"
