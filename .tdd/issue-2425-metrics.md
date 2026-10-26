### 📊 Metrics — issue 2425

Wall time for the issue: 2512 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2452.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.33 over 73 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88505 tokens, largest 184965 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88505 |
| 2 | $0.03 | 89884 |
| 3 | $0.03 | 91527 |
| 4 | $0.02 | 92171 |
| 5 | $0.02 | 92983 |
| 6 | $0.02 | 93271 |
| 7 | $0.02 | 93606 |
| 8 | $0.02 | 94172 |
| 9 | $0.02 | 94843 |
| 10 | $0.04 | 97993 |
| 11 | $0.04 | 100091 |
| 12 | $0.04 | 103147 |
| 13 | $0.04 | 105225 |
| 14 | $0.03 | 106039 |
| 15 | $0.03 | 106576 |
| 16 | $0.03 | 107495 |
| 17 | $0.03 | 108864 |
| 18 | $0.03 | 109644 |
| 19 | $0.03 | 110461 |
| 20 | $0.03 | 111177 |
| 21 | $0.03 | 112205 |
| 22 | $0.04 | 113948 |
| 23 | $0.03 | 114652 |
| 24 | $0.03 | 115578 |
| 25 | $0.03 | 116289 |
| 26 | $0.03 | 116718 |
| 27 | $0.03 | 117705 |
| 28 | $0.03 | 118144 |
| 29 | $0.04 | 119990 |
| 30 | $0.03 | 120443 |
| 31 | $0.03 | 121151 |
| 32 | $0.04 | 123324 |
| 33 | $0.03 | 124098 |
| 34 | $0.09 | 131969 |
| 35 | $0.04 | 133907 |
| 36 | $0.03 | 134741 |
| 37 | $0.03 | 135694 |
| 38 | $0.04 | 136930 |
| 39 | $0.04 | 138062 |
| 40 | $0.04 | 139797 |
| 41 | $0.03 | 140555 |
| 42 | $0.04 | 142178 |
| 43 | $0.03 | 142949 |
| 44 | $0.04 | 144347 |
| 45 | $0.04 | 145323 |
| 46 | $0.05 | 148066 |
| 47 | $0.04 | 148801 |
| 48 | $0.04 | 150515 |
| 49 | $0.04 | 151224 |
| 50 | $0.04 | 152748 |
| 51 | $0.11 | 162974 |
| 52 | $0.04 | 163447 |
| 53 | $0.04 | 164417 |
| 54 | $0.04 | 165293 |
| 55 | $0.05 | 167254 |
| 56 | $0.04 | 168259 |
| 57 | $0.03 | 168413 |
| 58 | $0.05 | 170442 |
| 59 | $0.06 | 173168 |
| 60 | $0.05 | 175111 |
| 61 | $0.04 | 176113 |
| 62 | $0.05 | 177522 |
| 63 | $0.04 | 178489 |
| 64 | $0.04 | 179252 |
| 65 | $0.05 | 181574 |
| 66 | $0.04 | 182262 |
| 67 | $0.04 | 182960 |
| 68 | $0.04 | 183213 |
| 69 | $0.04 | 183504 |
| 70 | $0.04 | 184049 |
| 71 | $0.04 | 184326 |
| 72 | $0.04 | 184657 |
| 73 | $0.04 | 184965 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 27 | 25 | 5 | 10 | 2142 | 133003 | 36594 | 0.13 |
| red | 8 | 4 | 0 | 0 | 150 | 125 | 30 | 60 | 10239 | 834509 | 162890 | 0.59 |
| green | 14 | 4 | 3 | 0 | 706 | 292 | 76 | 150 | 27484 | 2329222 | 253273 | 1.63 |
| refactor | 5 | 1 | 0 | 0 | 70 | 41 | 17 | 30 | 2939 | 383338 | 89732 | 0.29 |
| diff | 2 | 1 | 0 | 0 | 122 | 29 | 10 | 20 | 2764 | 283837 | 30553 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 11 | 3 | 0 | 499 | 209 | 59 | 118 | 17897 | 1652187 | 199103 | 0.84 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 259 | 148 | 44 | 84 | 13229 | 1168979 | 223986 | 0.81 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 317 | 155 | 35 | 68 | 14442 | 1142743 | 149953 | 1.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 761 | 1.83 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `queued-merge.sh` given a `<pr>` argument that is not a GitHub PR URL (e.g. the bare number `2415`) exits 2 with a usage line naming `<pr-url>` (the module's USAGE and the shim's header comment both say `<pr-url>`), before taking the merge lock, fetching, rebasing or pushing; pinned by an in-process case in `tests/py/unit/test_queued_merge.py` (process boundaries faked) asserting no `merge-lock.sh take` ran and no git command ran ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 74 | 18 | 36 | 5445 | 479752 | 99114 | 0.35 | 218 | unknown | 0/5 | nothing-left |  |  | full |
| On a successful queued merge the PR's local branch is deleted from the main clone (the checkout owning the worktree's common git dir) after the worktree is removed, so no `<branch>` ref is left behind; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 97 | 28 | 54 | 8677 | 762846 | 121252 | 0.57 | 306 | 1/2 | 0/5 | nothing-left |  |  | full |
| On a successful queued merge the main clone's `main` is fast-forwarded to `origin/main` with `--ff-only`, after the tag and the lock release; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 29 | 54 | 7731 | 769047 | 97409 | 0.40 | 241 | unknown | 1/5 | nothing-left |  |  | full |
| When the main clone's `main` cannot be fast-forwarded to `origin/main` (the `--ff-only` refuses), queued-merge reports it on stderr and exits non-zero, after the tag and the lock release have run, never silently skipping it; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 201 | 48 | 96 | 18809 | 1535424 | 188120 | 1.19 | 575 | 2/2 | 0/5 | nothing-left |  |  | full |
| `skills/tdd/SCRIPTS.md`'s `queued-merge.sh` entry names its first argument `<pr-url>`, the exit-2 refusal of a non-URL argument before the lock, and the local branch delete and `main` fast-forward on success (with its non-zero exit when the fast-forward cannot be done), and no longer says it does not fast-forward the main checkout ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 2764 | 283837 | 30553 | 0.13 | 148 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `queued-merge.sh` given a `<pr>` argument that is not a GitHub PR URL (e.g. the bare number `2415`) exits 2 with a usage line naming `<pr-url>` (the module's USAGE and the shim's header comment both say `<pr-url>`), before taking the merge lock, fetching, rebasing or pushing; pinned by an in-process case in `tests/py/unit/test_queued_merge.py` (process boundaries faked) asserting no `merge-lock.sh take` ran and no git command ran ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| On a successful queued merge the PR's local branch is deleted from the main clone (the checkout owning the worktree's common git dir) after the worktree is removed, so no `<branch>` ref is left behind; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| On a successful queued merge the main clone's `main` is fast-forwarded to `origin/main` with `--ff-only`, after the tag and the lock release; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 50 | 0.12 |
| When the main clone's `main` cannot be fast-forwarded to `origin/main` (the `--ff-only` refuses), queued-merge reports it on stderr and exits non-zero, after the tag and the lock release have run, never silently skipping it; pinned by an in-process case in `tests/py/unit/test_queued_merge.py`, process boundaries faked ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 13 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 8 | 1 | 1 | 1 | 1 | 2 | 9 | 9 | 1 | 9 | 1 | 25 | 26 |
| fast | 17 | 19 | 17 | 17 | 18 | 18 | 19 | 17 | 19 | 19 | 20 | 19 | 19 | 18 | 19 | 19 | 18 |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 138 | 270 | 45568 | 3963909 | 573042 | 2.77 |
