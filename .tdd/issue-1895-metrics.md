### 📊 Metrics — issue 1895

Wall time for the issue: 3520 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2085.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 15 | 3 | 6 | 1844 | 81055 | 17091 | 0.07 |
| red | 23 | 9 | 1 | 0 | 608 | 408 | 115 | 226 | 44825 | 3459079 | 436494 | 2.25 |
| green | 27 | 7 | 5 | 0 | 1031 | 440 | 139 | 268 | 42942 | 3887210 | 411275 | 2.34 |
| refactor | 14 | 7 | 0 | 0 | 195 | 86 | 37 | 74 | 6492 | 921742 | 185648 | 0.62 |
| diff | 4 | 2 | 0 | 0 | 242 | 96 | 36 | 72 | 9990 | 1193274 | 74364 | 0.41 |
| red-missing | 2 | 0 | 0 | 0 | 49 | 36 | 11 | 22 | 4119 | 343083 | 36857 | 0.17 |
| pin | 4 | 3 | 1 | 0 | 87 | 49 | 19 | 38 | 5039 | 527154 | 46509 | 0.22 |
| cover | 1 | 0 | 0 | 0 | 30 | 14 | 5 | 10 | 1424 | 137322 | 14377 | 0.06 |
| predicate | 1 | 0 | 0 | 0 | 8 | 6 | 3 | 6 | 510 | 74887 | 11508 | 0.04 |
| structural | 1 | 0 | 0 | 0 | 28 | 9 | 5 | 10 | 1077 | 138745 | 14566 | 0.06 |
| transform | 1 | 1 | 0 | 0 | 36 | 14 | 5 | 10 | 1367 | 133646 | 13442 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 37 | 30 | 7 | 0 | 930 | 397 | 138 | 274 | 40144 | 3677572 | 474283 | 1.96 |
| developer | claude-sonnet-5-5 | 30 | 0 | 0 | 0 | 913 | 497 | 161 | 316 | 50692 | 4872887 | 508457 | 2.39 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 488 | 279 | 79 | 152 | 28793 | 2346738 | 279391 | 1.95 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 127 | 0.55 | 0 | 0.00 |
| green | 958 | 2.12 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 48 | 0.11 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 127 | 47 | 92 | 13442 | 1398516 | 137278 | 0.75 | 468 | 1/2 | 0/5 | nothing-left |  |  | full |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 30 | 60 | 9578 | 888546 | 95981 | 0.42 | 228 | unknown | 0/5 | nothing-left |  |  | full |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 80 | 32 | 62 | 7819 | 837258 | 122031 | 0.58 | 215 | 1/2 | 0/5 | nothing-left |  |  | full |
| The `_boundaries` fixture in skills/tdd/scripts/tests/py/test_parallel_conductors.py puts its fake `.git` (and its `git worktree list` answer and the exclude-file path) at `tmp_path/repo`, the directory every case runs from, so no older case runs from what reads as a subdirectory of the repo; every case keeps its name and outcome; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 2619 | 293569 | 32534 | 0.14 | 81 | n/a | n/a | n/a |  |  | full |
| parallel_conductors.py run with its working directory a subdirectory of the repo writes `parallel.exit` and its conductor logs under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 16 | 4 | 3 | 0 | 0 | 0 | 278 | 81 | 158 | 26599 | 2377541 | 265282 | 1.50 | 583 | green 2/2, red 2/2 | 0/5 | nothing-left |  |  | full |
| run_conductor.py run with its working directory a subdirectory of the repo creates `.tdd/` and its seeded `.tdd/.gitignore` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 29 | 58 | 8695 | 871879 | 101031 | 0.43 | 268 | unknown | 0/5 | nothing-left |  |  | full |
| The skills-are-skills audit does not report an empty `.tdd/` directly under skills/, nor a directory under skills/ holding only an empty `.tdd/`, as a skill missing its SKILL.md, while a real skill directory without SKILL.md still is reported; small cases over a tmp_path skills tree, in a test module of their own beside the audit, pin both halves ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skills_are_skills.py⟧ ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 113 | 28 | 52 | 10597 | 698957 | 105295 | 0.52 | 258 | 1/2 | 0/5 | nothing-left |  |  | full |
| The skills-are-skills audit does not report a directory under skills/ that holds only a non-empty `.tdd/` (one holding run-state files such as `red-prediction.md`) as a skill missing its SKILL.md; a small case over a tmp_path skills tree, in the same test module as the empty-`.tdd/` cases, pins it ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skills_are_skills.py⟧ ⟦added⟧ ⟦criterion 4⟧ | 10 | 4 | 0 | 0 | 0 | 0 | 89 | 29 | 58 | 9453 | 747790 | 144676 | 0.59 | 243 | 1/2 | 0/5 | nothing-left |  |  | full |
| The skills-are-skills audit never reports a non-empty `.tdd/` directory directly under skills/ (one holding run-state files such as `red-prediction.md`) as a skill missing its SKILL.md; a small case over a tmp_path skills tree with a non-empty `.tdd/`, in the same test module as the empty-`.tdd/` cases, pins it ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skills_are_skills.py⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 7 | 14 | 2416 | 187821 | 28817 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| build-develop-prompt.sh names every run-state file a developer prompt tells the leaf to write (`red-prediction.md` and `red-run-output.txt`, in the red, red-supersede, red-missing and revise prompts) by an absolute path under the run's own `.tdd/` at the repo root, resolved the way event.py resolves its root, so a leaf whose shell is in a subdirectory still writes them there ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 26 | 52 | 7371 | 899705 | 41830 | 0.27 | 199 | n/a | n/a | n/a |  |  | full |
| Prompt cases pin that build-develop-prompt.sh's red, red-supersede, red-missing and revise-red prompts, built from a repo, name `red-prediction.md` and `red-run-output.txt` by absolute paths under that repo root's `.tdd/` and never as a bare relative `.tdd/` path ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 16 | 30 | 5865 | 501071 | 42954 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_build_develop_prompt_process.py — FAILED test_cli_run_through_a_symlink_to_the_scripts_directory_answers_red_green_and_diff_as_in_place_but_names_the_symlink_in_the_timed_test_run_path: AssertionError: assert ['red differs through the link'] == [] ⟦suite-repair⟧ ⟦criterion 3⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 122 | 40 | 80 | 13331 | 1113489 | 127331 | 0.70 | unknown | 1/2 | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.py run with its working directory a subdirectory of the repo creates and writes its run state (`.tdd/<name>.log`, `.rc`, `.exit`, `.pid`) under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.08 |
| verify.py run with its working directory a subdirectory of the repo writes its verifier prompt and run state under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 21 | 0.08 |
| pin_fast_tier.py run with its working directory a subdirectory of the repo writes `verify-pin.reason` under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 27 | 0.09 |
| parallel_conductors.py run with its working directory a subdirectory of the repo writes `parallel.exit` and its conductor logs under `.tdd/` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 29 | 0.09 |
| run_conductor.py run with its working directory a subdirectory of the repo creates `.tdd/` and its seeded `.tdd/.gitignore` at the repo root and leaves no `.tdd/` in the subdirectory; run from the root it behaves as before ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.09 |
| The skills-are-skills audit does not report an empty `.tdd/` directly under skills/, nor a directory under skills/ holding only an empty `.tdd/`, as a skill missing its SKILL.md, while a real skill directory without SKILL.md still is reported; small cases over a tmp_path skills tree, in a test module of their own beside the audit, pin both halves ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skills_are_skills.py⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 29 | 0.09 |
| The skills-are-skills audit does not report a directory under skills/ that holds only a non-empty `.tdd/` (one holding run-state files such as `red-prediction.md`) as a skill missing its SKILL.md; a small case over a tmp_path skills tree, in the same test module as the empty-`.tdd/` cases, pins it ⟦guard-subject: skills/tdd/scripts/tests/py/unit/test_skills_are_skills.py⟧ ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 27 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 9 | 9 | 2 | 51 | 8 | 3 | 9 | 4 | 3 | 3 | 3 | 3 | 3 | 6 | 6 | 0 | 5 | 4 | 3 | 5 | 3 | 4 | 4 | 4 | 5 | 5 | 4 | 5 | 4 | 4 | 5 | 3 | 4 | 5 | 5 | 4 | 4 | 4 | 16 | 16 | 15 | 15 | 15 | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | 4 | 14 | 16 | 3 | 16 |
| fast | 5 | 7 | 4 | 5 | 5 | 6 | 5 | 6 | 5 | 4 | 5 | 5 | 6 | 6 | 7 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 6 | 5 | 5 | 5 | 4 | 5 | 5 | 6 | 5 | 5 | 5 | 6 | 5 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 5 | 15 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 378 | 742 | 119629 | 10897197 | 1262131 | 6.30 |
