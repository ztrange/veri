# Plan for #757 — test_status.py stops reading status.test.sh's source text

- [x] `test_status.py` holds no case that reads `tests/status.test.sh` or any other `*.test.sh` — `test_status_test_sh_keeps_only_the_adr_0027_survivors_and_the_floor` and `test_status_test_sh_floor_holds_an_exit_2_case_and_a_bad_argument_stderr_case` are deleted, and `STATUS_SUITE`, `STATUS_SUITE_FLOOR` and `STATUS_SUITE_CUT` are gone with them ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] every other case in `test_status.py` keeps its name and its assertions, and `test_no_case_in_this_suite_calls_a_function_of_veri_status_other_than_main` stays ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] `tests/status.test.sh` is unchanged by the branch ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] `status.test.sh`'s exit-2 case and bad-argument stderr case still pass: `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧
