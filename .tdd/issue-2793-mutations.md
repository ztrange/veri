file 21
skills/vstop/SKILL.md
old 11
name: vstop
new 15
name: veri-stop
command 239
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py

file 19
skills/tdd/SKILL.md
old 9
name: tdd
new 10
name: vtdd
command 310
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py::test_skills_tdd_exists_and_its_skill_md_frontmatter_name_is_still_tdd

file 9
README.md
old 14
set to a fresh
new 26
set to a veri-status fresh
command 249
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py make test TESTS=skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py

file 65
skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py
old 149
:(exclude)specs", ":(exclude).tdd"],
        capture_output=True,
        text=True,
    )
    assert run.returncode in (0, 1), run.stderr
    return
new 130
:(exclude).tdd"],
        capture_output=True,
        text=True,
    )
    assert run.returncode in (0, 1), run.stderr
    return
command 164
make test TESTS=skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py::test_the_sweep_reports_a_tracked_file_holding_a_long_name_and_not_one_under_specs

file 21
skills/vstatus/GRADED
old 16
fea182ee1c730d0f
new 16
fea182ee1c730d00
command 374
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py::test_each_of_the_11_renamed_units_with_a_requirements_list_has_a_graded_line_under_its_new_path_signed_from_its_current_text_and_rows

