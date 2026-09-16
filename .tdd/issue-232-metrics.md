### 📊 Metrics — issue 232

Wall time for the issue: unknown s, from the first event of the log to the mark that ended the run.
Steps done: 8 of 11 planned.
Outcome: unknown — the log carries no mark ending the run.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 19 | 8 | 0 | 0 | 986 | 700 | 109 | 212 | 61885 | 4695900 | 744842 | 8.90 |
| green | 16 | 8 | 0 | 0 | 7323 | 482 | 120 | 226 | 36118 | 5563958 | 603915 | 6.71 |
| refactor | 16 | 8 | 0 | 0 | 4869 | 625 | 111 | 220 | 35919 | 5565007 | 564788 | 7.38 |
| pin | 3 | 3 | 0 | 0 | 178 | 85 | 30 | 60 | 6903 | 1581794 | 113052 | 0.85 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 171 | 1.88 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 178 | 0.85 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Unreachable origin with VERI_PUSH_RETRIES=2 VERI_PUSH_BACKOFF=0: push attempted 3 times, exit 0, one stderr line naming the failure and attempt count, one push-failed event; HEAD, commit count and ledger unchanged | 6 | 3 | 0 | 0 | 0 | 285 | 40 | 80 | 19398 | 2024152 | 203293 | 2.72 | 2127 | unknown | unknown | unknown |
| Unreachable origin with VERI_PUSH_RETRIES unset and VERI_PUSH_BACKOFF=0 is attempted 4 times, counted by a git stub on PATH | 2 | 1 | 0 | 0 | 0 | 43 | 13 | 26 | 4054 | 620581 | 77245 | 0.79 | unknown | unknown | unknown | unknown |
| Origin failing the first attempt and succeeding on the second ends with exit 0, the remote branch at HEAD, and no push-failed event | 2 | 1 | 0 | 0 | 0 | 62 | 15 | 28 | 6103 | 668424 | 77197 | 0.86 | unknown | unknown | unknown | unknown |
| Backoff is VERI_PUSH_BACKOFF seconds doubled per retry; with VERI_PUSH_BACKOFF=0 a 3-retry failure completes in under 2 s | 6 | 3 | 0 | 0 | 0 | 207 | 43 | 80 | 13716 | 1985553 | 243967 | 2.49 | 1426 | unknown | unknown | unknown |
| Non-integer VERI_PUSH_RETRIES or VERI_PUSH_BACKOFF exits 2 without attempting a push | 6 | 3 | 0 | 0 | 0 | 185 | 38 | 74 | 14700 | 1732075 | 236343 | 2.48 | 1317 | unknown | unknown | unknown |
| Non-fast-forward rejection (remote holds a commit the local branch amended) exits 1 after exactly one attempt, stderr carries the remote branch's full sha, and a push-rejected event records remote_sha | 6 | 3 | 0 | 0 | 0 | 253 | 33 | 62 | 11125 | 1492451 | 195949 | 2.91 | 1492 | unknown | unknown | unknown |
| A successful push exits 0, writes nothing to stderr beyond git's own output, and appends no event | 2 | 1 | 0 | 0 | 0 | 76 | 18 | 36 | 7098 | 923333 | 88154 | 1.08 | unknown | unknown | unknown | unknown |
| A failing event write (unwritable .tdd or failing event.sh) exits 2 for both an unreachable origin and a non-ff rejection | 6 | 3 | 0 | 0 | 0 | 196 | 44 | 88 | 17330 | 2082091 | 238687 | 2.61 | 1531 | unknown | unknown | unknown |
| build-develop-prompt.sh reconcile renders prompts/develop-reconcile.md with the remote sha, branch and literal --force-with-lease=<branch>:<sha>, no bare --force, and exits 2 on a missing argument | 6 | 3 | 0 | 0 | 0 | 220 | 43 | 84 | 18504 | 1973174 | 238742 | 2.76 | 1757 | unknown | unknown | unknown |
| classify-bail.sh reconcile-failed prints system and exits 0 | 6 | 3 | 0 | 0 | 0 | 132 | 28 | 56 | 6740 | 1274384 | 173617 | 2.13 | 1171 | unknown | unknown | unknown |
| SKILL.md at both push-branch.sh call sites launches develop-reconcile through supervise.sh on exit 1, bails on exit 2, requires re-running push-branch.sh and checking ledger ticks and refactor pending marks, bails with reconcile-failed otherwise, and no longer says exits 0 either way | 6 | 3 | 0 | 0 | 0 | 233 | 55 | 104 | 22057 | 2630441 | 253403 | 3.02 | 2498 | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 370 | 718 | 140825 | 17406659 | 2026597 | 23.84 |
