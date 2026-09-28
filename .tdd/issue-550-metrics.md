### 📊 Metrics — issue 550

Wall time for the issue: 5178 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/551.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 11 | 2 | 4 | 1025 | 54673 | 35938 | 0.32 |
| red | 10 | 5 | 0 | 0 | 555 | 369 | 85 | 166 | 36408 | 4218296 | 478193 | 5.40 |
| green | 12 | 5 | 1 | 0 | 2312 | 367 | 103 | 206 | 36033 | 4786013 | 477603 | 5.50 |
| refactor | 10 | 5 | 0 | 0 | 795 | 264 | 72 | 142 | 25577 | 3205531 | 424873 | 4.55 |
| structural | 4 | 0 | 0 | 0 | 101 | 47 | 12 | 24 | 4268 | 411581 | 142442 | 1.31 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 846 | 1.50 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wait-ci.sh` takes the head sha it waits for as an argument, and while the PR's reported `headRefOid` is a different commit it exits 3 (pending) at the end of its slice even when that other commit's checks all completed SUCCESS ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 217 | 58 | 114 | 20968 | 2611625 | 305604 | 3.39 | 1180 | 1/2 | 1/5 | structural-owed |  |  | full |
| `wait-ci.sh`'s total bound is recorded against the head sha it was given, not the PR's reported head: a later call for the same sha that still finds the PR reporting a different head past that recorded deadline exits 2 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 189 | 44 | 88 | 18013 | 2041926 | 261480 | 2.86 | 524 | unknown | 2/5 | nothing-structural |  |  | full |
| SKILL.md's Draft PR step passes the sha it just pushed (`git rev-parse HEAD`) to every `wait-ci.sh` call ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 230 | 59 | 116 | 22420 | 2897332 | 276739 | 3.24 | 1131 | unknown | 1/5 | structural-owed |  |  | full |
| a legacy StatusContext row carrying no `state` key makes `wait-ci.sh` exit 2 (no answer could be obtained) on its first read, instead of waiting out the bound ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 41 | 80 | 13069 | 1764505 | 250875 | 2.62 | 474 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md's Draft PR step bails on the `metrics:` push's CI wait with a command in its block — `ci-red` on exit 1, `ci-timeout` on exit 2 — not only in prose after the `done` mark | 6 | 3 | 0 | 0 | 0 | 0 | 223 | 58 | 116 | 23548 | 2894452 | 285971 | 3.34 | 816 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wait-ci.sh` takes the head sha it waits for as an argument, and while the PR's reported `headRefOid` is a different commit it exits 3 (pending) at the end of its slice even when that other commit's checks all completed SUCCESS ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 122 | 0.94 |
| `wait-ci.sh`'s total bound is recorded against the head sha it was given, not the PR's reported head: a later call for the same sha that still finds the PR reporting a different head past that recorded deadline exits 2 ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 165 | 0.95 |
| SKILL.md's Draft PR step passes the sha it just pushed (`git rev-parse HEAD`) to every `wait-ci.sh` call ⟦criterion 2⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 218 | 0.91 |
| a legacy StatusContext row carrying no `state` key makes `wait-ci.sh` exit 2 (no answer could be obtained) on its first read, instead of waiting out the bound ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.84 |
| SKILL.md's Draft PR step bails on the `metrics:` push's CI wait with a command in its block — `ci-red` on exit 1, `ci-timeout` on exit 2 — not only in prose after the `done` mark | 1 | 0/5 | nothing-left | PASS | 0 | 211 | 0.91 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 0 | 15 | 18 | 18 | 18 | 15 | 0 | 15 | 16 | 16 | 16 | 16 | 20 | 17 | 0 | 21 | 0 | 3 | 3 | 0 | 144 | 0 | 435 | 135 | 3 | 22 | 22 | 19 | 19 | 0 | 19 | 3 | 3 | 0 | 140 | 136 | 0 | 144 | 17 | 3 | 17 | 2 |
| fast | 6 | 6 | 6 | 7 | 6 | 6 | 8 | 7 | 12 | 8 | 8 | 8 | 9 | 8 | 9 | 7 | 8 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 16 | 0 | 16 | 0 | 16 | 3 | 20 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 541 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 274 | 542 | 103311 | 12676094 | 1559049 | 17.08 |
