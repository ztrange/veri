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

file 37
skills/tdd/scripts/veri/prose_owed.py
old 53
if graded_signature(u) != grade_prose.signature(p, u)
new 53
if graded_signature(u) == grade_prose.signature(p, u)
command 342
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py::test_prose_owed_sh_on_a_copy_of_the_tip_with_no_ledger_reports_no_unit_owed_and_no_orphan_graded_line

file 37
skills/tdd/scripts/veri/prose_owed.py
old 26
if fields[0] not in units:
new 22
if fields[0] in units:
command 342
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_prd_016_short_names.py::test_prose_owed_sh_on_a_copy_of_the_tip_with_no_ledger_reports_no_unit_owed_and_no_orphan_graded_line

file 52
skills/tdd/scripts/tests/py/unit/test_grade_prose.py
old 47
renamed = sorted(root.glob("skills/v*/GRADED"))
new 51
renamed = sorted(root.glob("skills/veri-*/GRADED"))
command 308
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp7p3jmoc0/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/unit/test_grade_prose.py make test TESTS=skills/tdd/scripts/tests/py/unit/test_grade_prose.py::test_every_committed_graded_line_names_the_grader_template_it_was_signed_under_2474

