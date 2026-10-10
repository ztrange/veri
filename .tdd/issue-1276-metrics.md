### 📊 Metrics — issue 1276

Wall time for the issue: 4344 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1429.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1034 | 12489 | 34155 | 0.15 |
| red | 8 | 2 | 0 | 0 | 393 | 275 | 75 | 146 | 36742 | 4172618 | 426129 | 2.49 |
| pin | 4 | 4 | 0 | 0 | 80 | 62 | 22 | 44 | 7890 | 977046 | 172619 | 0.87 |
| green | 10 | 5 | 0 | 0 | 734 | 196 | 75 | 146 | 23957 | 3542247 | 445073 | 2.37 |
| refactor | 10 | 5 | 0 | 0 | 349 | 108 | 45 | 86 | 11968 | 1806084 | 424697 | 2.00 |
| diff | 2 | 1 | 0 | 0 | 161 | 44 | 15 | 28 | 5475 | 648109 | 85760 | 0.46 |
| predicate | 1 | 0 | 0 | 0 | 11 | 8 | 3 | 6 | 974 | 111566 | 41164 | 0.19 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 18 | 18 | 0 | 0 | 877 | 286 | 103 | 196 | 34729 | 4387886 | 761586 | 3.83 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 862 | 415 | 133 | 262 | 53311 | 6882273 | 868011 | 4.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 76 | 0.50 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A supervised leaf's launch environment — claude's argv carrying --model only when the run chose a model, and claude started without the caller's session variables — is pinned through run_cli in tests/py/test_supervise.py: replaces 'a supervised leaf's claude argv carries --model only when the run chose a model', 'a leaf launched as supervise.sh <name> run-leaf.sh starts claude without the caller's session variables (#621)' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 48 | 94 | 17286 | 2464717 | 280974 | 1.54 | 635 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| A launch event's skill_commit — the skill clone's own HEAD, or the literal unknown for a skill outside a git clone — is pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'a launch event carries the skill's own commit in skill_commit', 'a skill outside a git clone records skill_commit as the literal unknown' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 37 | 72 | 12345 | 1734174 | 265990 | 1.36 | 415 | unknown | 0/5 | nothing-structural |  |  | already-satisfied |
| A killed leaf is recovered from a terminal result record in its log — reported with the leaf's own outcome (0 on success, 1 on an error record), launched once with no stuck-retry, its captured stdout ending in the clean result text parse-verdict.sh reads — and with no such record is still exit 2 with its kill cause on stderr, and supervise.sh's header says a kill is not proof no answer was obtained — pinned through run_cli in tests/py/test_supervise.py: replaces 'a killed leaf whose log holds a terminal result record is reported with the leaf's own outcome, not killed-stuck', 'a killed leaf whose terminal result record is an error is reported exit 1, not exit 0', 'a leaf recovered from its terminal result record is launched exactly once, with no stuck-retry', 'a recovered leaf's captured stdout ends with the clean result text, so parse-verdict.sh reads its verdict', 'a killed leaf whose log holds no terminal result record is still exit 2 with its kill cause on stderr', 'supervise.sh's header records that a leaf's stream can finish before its rc file is written, so a kill is not proof that no answer was obtained' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 134 | 43 | 84 | 16812 | 2173918 | 288379 | 1.54 | 653 | unknown | 0/5 | nothing-structural |  |  | already-satisfied |
| supervise.sh writes its own pid to .tdd/<name>.pid before it launches the leaf, and a killed-stuck leaf preserves the relaunched attempt and the final one as their own trees and logs (a medium case marked @pytest.mark.process, since preservation writes git refs) — pinned through run_cli in tests/py/test_supervise.py: replaces 'supervise.sh records its own pid in .tdd/<name>.pid before it launches the leaf', 'a killed-stuck leaf preserves the relaunched attempt and the final one, each as its own tree and log' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 138 | 46 | 90 | 17252 | 2306473 | 288387 | 1.56 | 552 | unknown | 0/5 | nothing-structural |  |  | already-satisfied |
| supervise.test.sh's remaining cases still pass and the file stays for the other C4d groups, since cases remain after this group's removal; no guard table, roster, workflow comment or CLAUDE.md count loses a reference it still needs, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 52 | 18 | 34 | 6449 | 759675 | 126924 | 0.65 | 178 | unknown | unknown | unknown |  |  | full |
| fix the CI failure: skills/tdd/scripts/tests/py/test_supervise.py — FAILED test_supervise.py::test_cli_records_its_own_pid_before_the_leaf_launches_and_preserves_the_relaunched_attempt_and_the_final_one_each_as_its_own_tree_and_log - AssertionError: assert (2, ['63185',... 0, [], 0, []) == (2, ['63185',...2, ['1', '2']) (on the Linux CI runner no attempt was preserved: 0 refs, 0 log copies; it passes on macOS) ⟦ci-repair⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 14 | 28 | 6946 | 665478 | 91130 | 0.50 | unknown | unknown | unknown | unknown |  |  | full |
| fix the CI failure: the pid-and-preserved-attempts case in skills/tdd/scripts/tests/py/test_supervise.py (test_cli_records_its_own_pid_before_the_leaf_launches_and_preserves_the_relaunched_attempt_and_the_final_one_each_as_its_own_tree_and_log) gives its scratch repo a git identity with git config user.name/user.email, as the removed bash case did, so it preserves both attempts on a runner with no global git identity (CI: assert (2, ['63185',... 0, [], 0, []) == (2, ['63185',...2, ['1', '2'])); no production code changes ⟦ci-repair⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 29 | 54 | 9916 | 1153235 | 253658 | 1.23 | unknown | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A supervised leaf's launch environment — claude's argv carrying --model only when the run chose a model, and claude started without the caller's session variables — is pinned through run_cli in tests/py/test_supervise.py: replaces 'a supervised leaf's claude argv carries --model only when the run chose a model', 'a leaf launched as supervise.sh <name> run-leaf.sh starts claude without the caller's session variables (#621)' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 69 | 0.38 |
| A launch event's skill_commit — the skill clone's own HEAD, or the literal unknown for a skill outside a git clone — is pinned through run_cli in tests/py/test_supervise.py by medium cases marked @pytest.mark.process: replaces 'a launch event carries the skill's own commit in skill_commit', 'a skill outside a git clone records skill_commit as the literal unknown' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 73 | 0.41 |
| A killed leaf is recovered from a terminal result record in its log — reported with the leaf's own outcome (0 on success, 1 on an error record), launched once with no stuck-retry, its captured stdout ending in the clean result text parse-verdict.sh reads — and with no such record is still exit 2 with its kill cause on stderr, and supervise.sh's header says a kill is not proof no answer was obtained — pinned through run_cli in tests/py/test_supervise.py: replaces 'a killed leaf whose log holds a terminal result record is reported with the leaf's own outcome, not killed-stuck', 'a killed leaf whose terminal result record is an error is reported exit 1, not exit 0', 'a leaf recovered from its terminal result record is launched exactly once, with no stuck-retry', 'a recovered leaf's captured stdout ends with the clean result text, so parse-verdict.sh reads its verdict', 'a killed leaf whose log holds no terminal result record is still exit 2 with its kill cause on stderr', 'supervise.sh's header records that a leaf's stream can finish before its rc file is written, so a kill is not proof that no answer was obtained' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 74 | 0.41 |
| supervise.sh writes its own pid to .tdd/<name>.pid before it launches the leaf, and a killed-stuck leaf preserves the relaunched attempt and the final one as their own trees and logs (a medium case marked @pytest.mark.process, since preservation writes git refs) — pinned through run_cli in tests/py/test_supervise.py: replaces 'supervise.sh records its own pid in .tdd/<name>.pid before it launches the leaf', 'a killed-stuck leaf preserves the relaunched attempt and the final one, each as its own tree and log' in skills/tdd/scripts/tests/supervise.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 82 | 0.42 |
| fix the CI failure: the pid-and-preserved-attempts case in skills/tdd/scripts/tests/py/test_supervise.py (test_cli_records_its_own_pid_before_the_leaf_launches_and_preserves_the_relaunched_attempt_and_the_final_one_each_as_its_own_tree_and_log) gives its scratch repo a git identity with git config user.name/user.email, as the removed bash case did, so it preserves both attempts on a runner with no global git identity (CI: assert (2, ['63185',... 0, [], 0, []) == (2, ['63185',...2, ['1', '2'])); no production code changes ⟦ci-repair⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 51 | 0.38 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 26 | 21 | 5 | 5 | 26 | 19 | 5 | 22 | 17 | 5 | 5 | 24 | 6 | 5 | 23 | 25 | 24 | 18 | 25 | 8 | 8 | 6 | 7 | 6 | 6 | 6 |
| target | 0 | 0 | 1 | 0 | 0 | 3 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 1 | 2 | 0 |  |  |  |  |  |  |  |  |
| fast | 25 | 27 | 22 | 24 | 25 | 23 | 22 | 22 | 25 | 22 | 25 | 25 | 24 | 25 | 24 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 236 | 458 | 88040 | 11270159 | 1629597 | 8.53 |
