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
