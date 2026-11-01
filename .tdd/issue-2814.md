# Plan for #2814 — pin-recheck replays a pin recorded through a run's scratch copy of the skill

- [x] A mutations record whose command begins with a `timed-test-run.sh` path that no longer exists is replayed through the current skill's `timed-test-run.sh`, and a pin that still catches its mutant is not reported "needs a look" ⟦criterion 1⟧
- [x] A mutations record whose command still cannot run prints "needs a look" as today, whether or not its command begins with a `timed-test-run.sh` path that no longer exists ⟦criterion 2⟧
- [x] fix the CI failure: skills/tdd/scripts/tests/py/test_parallel_conductors.py — FAILED test_a_launch_run_through_a_symlink_to_the_skills_directory_from_another_cwd_answers_as_it_does_in_place_and_prints_no_leaf_role_refusal - FileNotFoundError: No such file or directory: <tmp>/in-place/.tdd/wt/7/.tdd/events.jsonl (CI run 41298867502, its log in .tdd/ci-repair-job.log) ⟦ci-repair⟧ ⟦criterion 2⟧
