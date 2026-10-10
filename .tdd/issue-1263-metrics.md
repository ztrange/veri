### 📊 Metrics — issue 1263

Wall time for the issue: 7954 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1414.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 10 | 1 | 2 | 1209 | 12193 | 43647 | 0.19 |
| red | 3 | 0 | 0 | 0 | 356 | 269 | 45 | 84 | 25222 | 3142075 | 229830 | 2.97 |
| pin | 3 | 3 | 0 | 0 | 147 | 63 | 23 | 46 | 7012 | 1185309 | 151502 | 0.79 |
| green | 6 | 3 | 0 | 0 | 1164 | 169 | 52 | 100 | 15865 | 2746072 | 308389 | 2.60 |
| refactor | 6 | 3 | 0 | 0 | 578 | 157 | 39 | 78 | 13701 | 2020162 | 305932 | 2.41 |
| diff | 2 | 1 | 0 | 0 | 346 | 29 | 11 | 22 | 2379 | 511187 | 86971 | 0.65 |
| predicate | 1 | 0 | 0 | 0 | 22 | 16 | 4 | 8 | 1500 | 185121 | 48423 | 0.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 11 | 0 | 0 | 1154 | 197 | 66 | 128 | 21135 | 3164336 | 527149 | 2.64 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 1474 | 516 | 109 | 212 | 45753 | 6637783 | 647545 | 7.42 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Launch and hung leaf: `verify.sh` driven through `run_cli` in `tests/py/test_verify.py` builds the blind prompt carrying the spec and passes it to the leaf (small), and a hung verifier leaf is killed-stuck with exit 2 and runs exactly once even under an ambient `VERI_STUCK_RETRIES=3` (medium, `@pytest.mark.process`): replaces 'spec reaches the leaf (blind prompt built + passed)', 'hung verifier leaf → killed-stuck exit 2', 'ambient VERI_STUCK_RETRIES=3 → hung verifier leaf still runs exactly once' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 268 | 57 | 110 | 24284 | 3446828 | 341993 | 3.15 | 1757 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| Tree-tamper check: a verifier leaf that changes a tracked file, leaves an untracked file or moves HEAD in a real scratch repository exits 2 naming what changed and leaves the tree, HEAD and the developer's uncommitted work as it was handed; a verifier that restored its own mutation gets its verdict's normal exit code; and a `VERIFY_LEAF_ARGS` override reaching the leaf does not switch the check off (medium, `@pytest.mark.process`): replaces 'a verifier leaf that left the tree changed exits 2 naming what changed', 'after the exit 2 the tree and HEAD are back to what the verifier was handed, uncommitted work included', 'a verifier that restored its own mutation gets its verdict's normal exit code', 'VERIFY_LEAF_ARGS overriding the leaf's flags does not switch the tree check off' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 51 | 100 | 18208 | 2904227 | 330499 | 2.84 | 1520 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| Run state under the repo's own `.gitignore` (#569): run state left in a nested `.tdd/` is accepted with the verdict's PASS or REJECT, while an edited root ledger, or a modified, deleted or added tracked path, is refused with exit 2 naming each, and under that `.gitignore` the root ledger is not ignored and the root blind spec is (medium, `@pytest.mark.process`): replaces '#569: a verifier whose run leaves $subdir_state/events.jsonl behind under the repo's own .gitignore has its PASS accepted', '#569: a verifier whose run leaves $deep_state/run.log behind under the repo's own .gitignore has its REJECT accepted', '#569: a verifier that edits the root ledger $ledger is refused naming it, even when its run also leaves $subdir_state/events.jsonl behind', '#569: a verifier that modifies src.txt, deletes $doomed and adds $added under the repo's own .gitignore is refused naming each, even when its run also leaves $subdir_state/events.jsonl behind', '#569: under the repo's own .gitignore the root ledger $ledger is not ignored and the root blind spec $root_spec is' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 201 | 51 | 98 | 19308 | 2742563 | 323161 | 2.78 | 1312 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |
| `verify.test.sh`'s remaining 26 cases still pass and the file stays, so no guard table, roster, workflow comment or `CLAUDE.md` count changes for it ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 45 | 15 | 30 | 3879 | 696308 | 135394 | 1.10 | 373 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Launch and hung leaf: `verify.sh` driven through `run_cli` in `tests/py/test_verify.py` builds the blind prompt carrying the spec and passes it to the leaf (small), and a hung verifier leaf is killed-stuck with exit 2 and runs exactly once even under an ambient `VERI_STUCK_RETRIES=3` (medium, `@pytest.mark.process`): replaces 'spec reaches the leaf (blind prompt built + passed)', 'hung verifier leaf → killed-stuck exit 2', 'ambient VERI_STUCK_RETRIES=3 → hung verifier leaf still runs exactly once' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 185 | 0.75 |
| Tree-tamper check: a verifier leaf that changes a tracked file, leaves an untracked file or moves HEAD in a real scratch repository exits 2 naming what changed and leaves the tree, HEAD and the developer's uncommitted work as it was handed; a verifier that restored its own mutation gets its verdict's normal exit code; and a `VERIFY_LEAF_ARGS` override reaching the leaf does not switch the check off (medium, `@pytest.mark.process`): replaces 'a verifier leaf that left the tree changed exits 2 naming what changed', 'after the exit 2 the tree and HEAD are back to what the verifier was handed, uncommitted work included', 'a verifier that restored its own mutation gets its verdict's normal exit code', 'VERIFY_LEAF_ARGS overriding the leaf's flags does not switch the tree check off' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 183 | 0.77 |
| Run state under the repo's own `.gitignore` (#569): run state left in a nested `.tdd/` is accepted with the verdict's PASS or REJECT, while an edited root ledger, or a modified, deleted or added tracked path, is refused with exit 2 naming each, and under that `.gitignore` the root ledger is not ignored and the root blind spec is (medium, `@pytest.mark.process`): replaces '#569: a verifier whose run leaves $subdir_state/events.jsonl behind under the repo's own .gitignore has its PASS accepted', '#569: a verifier whose run leaves $deep_state/run.log behind under the repo's own .gitignore has its REJECT accepted', '#569: a verifier that edits the root ledger $ledger is refused naming it, even when its run also leaves $subdir_state/events.jsonl behind', '#569: a verifier that modifies src.txt, deletes $doomed and adds $added under the repo's own .gitignore is refused naming each, even when its run also leaves $subdir_state/events.jsonl behind', '#569: under the repo's own .gitignore the root ledger $ledger is not ignored and the root blind spec $root_spec is' in skills/tdd/scripts/tests/verify.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 210 | 0.89 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 63 | 60 | 63 | 10 | 9 | 63 | 58 | 0 | 58 | 14 | 66 | 66 | 64 | 69 |
| target | 1 | 2 | 0 | 1 | 12 | 12 | 12 | 12 | 8 | 5 | 5 | 7 | 6 |  |  |  |
| fast | 59 | 62 | 60 | 56 | 59 | 63 | 59 | 63 | 59 | 62 | 59 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 175 | 340 | 66888 | 9802119 | 1174694 | 10.06 |
