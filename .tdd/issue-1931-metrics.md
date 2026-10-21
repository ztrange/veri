### 📊 Metrics — issue 1931

Wall time for the issue: 2027 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1990.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 2 | 4 | 1470 | 47898 | 15433 | 0.06 |
| red | 5 | 2 | 0 | 0 | 87 | 70 | 22 | 44 | 7141 | 630760 | 81060 | 0.34 |
| green | 8 | 2 | 2 | 0 | 630 | 173 | 51 | 98 | 16446 | 1513670 | 110844 | 0.77 |
| refactor | 4 | 2 | 0 | 0 | 48 | 26 | 12 | 22 | 1963 | 277768 | 51810 | 0.18 |
| pin | 1 | 1 | 0 | 0 | 16 | 12 | 5 | 10 | 1409 | 135696 | 14362 | 0.06 |
| diff | 2 | 1 | 0 | 0 | 46 | 28 | 10 | 20 | 2991 | 273430 | 26822 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 9 | 2 | 0 | 521 | 139 | 44 | 88 | 13814 | 1201821 | 134481 | 0.59 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 114 | 80 | 31 | 58 | 8787 | 822357 | 107290 | 0.44 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 206 | 102 | 27 | 52 | 8819 | 855044 | 58560 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1136 | 1.09 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A requirements list written as a GFM table without leading or trailing pipes (`ID | Requirement | Why`, `---|---|---`, `A1 | … | …`) is read by `requirements.claims` as the same rows as its piped form, so `prose-owed.sh` run on a tree whose only list is that pipe-less table prints the unsigned unit owed and exits 1, never 0; pinned by a small in-process case in tests/py/unit/test_prose_owed_gate.py ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 191 | 57 | 112 | 17373 | 1704905 | 143617 | 0.88 | 781 | 2/2 | 0/5 | nothing-left |  |  | full |
| A requirements list written as a GFM table indented by one to three spaces is read by `requirements.claims` as the same rows as its unindented form, so `prose-owed.sh` run on a tree whose only list is that indented table prints the unsigned unit owed and exits 1, never 0; pinned by a small in-process case in tests/py/unit/test_prose_owed_gate.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 12 | 24 | 3644 | 356553 | 32439 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| The gate and `grade-prose.sh` read lists through one reader: `prose_owed.listed_units`' copy of the loop in `requirements.units` is removed, and the gate takes a file's listed units from one function of `veri/requirements.py` that skips only a unit with no table and raises every other refusal, with no behaviour change to `requirements.sh units` or `requirements.sh claims` ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 10 | 20 | 2991 | 273430 | 26822 | 0.12 | 76 | n/a | n/a | n/a |  |  | full |
| A `REQUIREMENTS.md` beside a unit at any depth under `skills/<skill>/` (e.g. `skills/demo/prompts/REQUIREMENTS.md` listing `skills/demo/prompts/P.md`) is read by `prose-owed.sh`, so that unit, with no `GRADED` line, is printed owed and the exit is 1; pinned by a small in-process case in tests/py/unit/test_prose_owed_gate.py ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 58 | 21 | 38 | 5942 | 496436 | 82020 | 0.31 | 169 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A requirements list written as a GFM table without leading or trailing pipes (`ID | Requirement | Why`, `---|---|---`, `A1 | … | …`) is read by `requirements.claims` as the same rows as its piped form, so `prose-owed.sh` run on a tree whose only list is that pipe-less table prints the unsigned unit owed and exits 1, never 0; pinned by a small in-process case in tests/py/unit/test_prose_owed_gate.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 26 | 0.09 |
| A `REQUIREMENTS.md` beside a unit at any depth under `skills/<skill>/` (e.g. `skills/demo/prompts/REQUIREMENTS.md` listing `skills/demo/prompts/P.md`) is read by `prose-owed.sh`, so that unit, with no `GRADED` line, is printed owed and the exit is 1; pinned by a small in-process case in tests/py/unit/test_prose_owed_gate.py ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 22 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 56 | 3 | 0 | 0 | 97 | 0 | 0 | 95 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 2 | 0 |
| fast | 6 | 7 | 6 | 6 | 7 | 6 | 5 | 6 | 6 | 7 | 6 | 5 | 6 |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 102 | 198 | 31420 | 2879222 | 300331 | 1.53 |
