### 📊 Metrics — issue 1513

Wall time for the issue: 6909 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1556.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 16 | 1 | 2 | 1756 | 12193 | 44459 | 0.20 |
| red | 7 | 3 | 0 | 0 | 193 | 142 | 36 | 72 | 14925 | 1830300 | 350447 | 1.73 |
| green | 6 | 3 | 0 | 0 | 1977 | 130 | 34 | 64 | 12881 | 1630747 | 295195 | 1.47 |
| refactor | 6 | 3 | 0 | 0 | 1193 | 92 | 29 | 58 | 8634 | 1392686 | 285030 | 1.37 |
| diff | 8 | 3 | 1 | 0 | 1758 | 334 | 89 | 176 | 34105 | 5314760 | 443443 | 3.12 |
| pin | 1 | 1 | 0 | 0 | 21 | 16 | 5 | 10 | 1529 | 240081 | 47363 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 14 | 1 | 0 | 1734 | 297 | 78 | 154 | 28916 | 3792325 | 720203 | 3.55 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 2879 | 262 | 75 | 146 | 26564 | 3828437 | 606422 | 3.07 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 549 | 171 | 41 | 82 | 18350 | 2800005 | 139312 | 1.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 886 | 2.15 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A pytest case marked `@pytest.mark.tree_audit("<what it sweeps>")` is deselected by `make unit` and run by `make test`: the mark is registered in conftest.py's `pytest_configure` beside `process`, and `make unit`'s selection deselects tree audits beside `process` cases ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 25 | 48 | 8956 | 1112915 | 286621 | 1.35 | 657 | unknown | 0/5 | nothing-left |  |  | full |
| A `tree_audit` mark with no argument, or an empty one, is refused at collection with a usage error naming the test, before any case runs, as a `process` mark without a boundary is ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 104 | 32 | 64 | 9931 | 1584048 | 289479 | 1.42 | 1095 | unknown | 1/5 | nothing-left |  |  | full |
| Every pytest case on the tree that lists a directory under the repository root outside its `tmp_path` — by its own code or through the module it drives — carries `@pytest.mark.tree_audit("<what it sweeps>")` naming what it sweeps, including the three sweeps in `test_comment_class.py`, `test_unreachable.py`'s scan of this repository, `test_shims.py`'s exemption-table case and the `test_build_develop_prompt.py` / `test_build_verify_prompt.py` cases that glob `veri/` or `prompts/`; no case is rewritten and no production code changes ⟦diff-checked⟧ ⟦criterion 3⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 250 | 64 | 126 | 26893 | 4048278 | 250542 | 2.15 | 945 | 1/2 | unknown | unknown |  |  | full |
| `test_entry.py`'s real closed-pipe case (`test_run_leaves_nothing_for_shutdown_to_flush_so_a_real_closed_pipe_still_exits_141_with_an_empty_stderr_1150`) and `test_run_leaf.py`'s process-group SIGTERM case (`test_main_launches_the_leaf_in_its_callers_process_group_with_sigpipe_and_sigxfsz_as_handed_and_on_sigterm_removes_both_temp_files`) carry `@pytest.mark.process("<boundary>")` naming a real closed pipe at interpreter shutdown and SIGTERM reaching a real process group respectively, and are not otherwise rewritten ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 11 | 22 | 2950 | 530248 | 89723 | 0.44 | 693 | n/a | n/a | n/a |  |  | full |
| An unmarked pytest case whose own code lists a directory under the repository root outside its `tmp_path` fails, naming the case and the directory: a planted case that globs `skills/tdd/scripts/` fails that way, and the same case marked `tree_audit` passes under `make test`; a case that reads one named file under the root, or imports a module, still passes ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 34 | 66 | 13801 | 1696036 | 299333 | 1.51 | 1806 | unknown | 1/5 | structural-owed |  |  | full |
| An unmarked pytest case that drives a module which itself lists a directory under the repository root outside the case's `tmp_path` fails the same way, naming the case and the directory ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 26 | 5281 | 700815 | 102602 | 0.53 | unknown | unknown | unknown | unknown |  |  | pin |
| `CLAUDE.md`'s *Testing idiom* says that a case marked `tree_audit` runs in the full suite (`make test`) and not in a leaf's fast tier (`make unit`), what counts as a tree audit, and why: the operator accepted on 2026-10-11 that a tree-audit break surfaces at the full suite, run once per PR and on CI, rather than costing a sweep in every leaf's `make unit` ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 14 | 28 | 4262 | 736234 | 103178 | 0.53 | 237 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A pytest case marked `@pytest.mark.tree_audit("<what it sweeps>")` is deselected by `make unit` and run by `make test`: the mark is registered in conftest.py's `pytest_configure` beside `process`, and `make unit`'s selection deselects tree audits beside `process` cases ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 137 | 0.41 |
| A `tree_audit` mark with no argument, or an empty one, is refused at collection with a usage error naming the test, before any case runs, as a `process` mark without a boundary is ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 327 | 0.48 |
| An unmarked pytest case whose own code lists a directory under the repository root outside its `tmp_path` fails, naming the case and the directory: a planted case that globs `skills/tdd/scripts/` fails that way, and the same case marked `tree_audit` passes under `make test`; a case that reads one named file under the root, or imports a module, still passes ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 729 | 0.47 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 47 | 111 | 54 | 1 | 0 | 496 | 1 | 8 | 51 | 509 | 3 | 2 | 501 | 111 | 520 | 0 | 112 | 4 | 39 | 3 | 0 | 3 |
| fast | 58 | 56 | 55 | 54 | 57 | 57 | 52 | 51 | 52 | 52 | 52 | 55 | 52 | 53 | 51 | 51 | 52 | 53 |  |  |  |  |  |  |
| target | 56 | 1 | 4 | 0 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 194 | 382 | 73830 | 10420767 | 1465937 | 8.11 |
