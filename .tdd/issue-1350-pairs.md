# Mutation-parity pairs proven for #1350

Every row below is `proven` by the conductor's own `mutation-parity.sh` run against the step's pre-deletion tree with its new pytest file added.

## Step 1 — classify-bail.test.sh (4/4, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| killed-stuck is system | `unit/test_classify_bail.py::test_main_classifies_every_known_cause_as_system_or_process_with_0` | `killed-stuck` moved from the system causes to the process ones in `veri/classify_bail.py` | proven |
| unknown cause exits non-zero | `unit/test_classify_bail.py::test_main_prints_the_category_of_a_known_cause_and_refuses_an_unknown_or_missing_one_with_2` | an unknown cause returns 0 instead of 2 | proven |
| an unknown cause writes its refusal and the usage line on stderr, nothing on stdout, exit 2 | `unit/test_classify_bail.py::test_main_prints_the_category_of_a_known_cause_and_refuses_an_unknown_or_missing_one_with_2` | the refusal drops the usage line | proven |
| classify-bail.sh run through a symlink to the skill directory and from another working directory answers killed-stuck and an unknown cause as it does in place | `test_classify_bail_process.py::test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place` | the shim exits 5 unless its working directory holds `skills/` | proven |
