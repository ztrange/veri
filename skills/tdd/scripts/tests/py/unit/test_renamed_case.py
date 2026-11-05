"""In-process cases for veri/renamed_case.py."""
from veri import renamed_case


def test_renamed_to_returns_the_new_name_of_a_go_func_test_case_renamed_with_its_body_unchanged():
    old = 'func TestAdd(t *testing.T) {\n\tif Add(1, 2) != 3 {\n\t\tt.Fatal("bad")\n\t}\n}\n'
    new = old.replace("TestAdd", "TestSum")

    assert renamed_case.renamed_to("TestAdd", old, new, set()) == "TestSum"
