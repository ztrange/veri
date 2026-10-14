### 📊 Metrics — issue 1558

Wall time for the issue: 2384 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1562.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 30 | 22 | 3 | 6 | 2592 | 74940 | 89101 | 0.39 |
| red | 5 | 2 | 0 | 0 | 140 | 104 | 29 | 58 | 11980 | 1484743 | 242876 | 1.24 |
| green | 4 | 2 | 0 | 0 | 578 | 72 | 27 | 52 | 7599 | 1288413 | 183836 | 0.94 |
| refactor | 4 | 2 | 0 | 0 | 172 | 45 | 19 | 36 | 4294 | 826498 | 182783 | 0.86 |
| pin | 1 | 1 | 0 | 0 | 25 | 16 | 4 | 8 | 1956 | 179657 | 46716 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 420 | 131 | 40 | 80 | 14328 | 1830240 | 407951 | 1.96 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 525 | 128 | 42 | 80 | 14093 | 2024011 | 337361 | 1.69 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| replaces-case-survivors.sh "<step text>" on a plain step text carrying no ⟦replaces-case⟧ mark exits 3 with nothing on stdout and no Python traceback on stderr (today: AttributeError 'NoneType' object has no attribute 'end', exit 2); pinned by a small pytest case in tests/py/test_replaces_case_survivors.py driving the module through run_cli ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 37 | 70 | 9300 | 1705656 | 276508 | 1.37 | 373 | unknown | 0/5 | nothing-left |  |  | full |
| SKILL.md's Green Verify sub-step line that runs replaces-case-survivors.sh "<step text>" before the verify-green launch says it runs only on a ⟦replaces-case⟧ step, as the pin-path paragraph already does, so a conductor reading it on an ordinary step runs nothing; pinned by a prose case in skill-green-split.test.sh that goes red when that line carries no ⟦replaces-case⟧ qualifier ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 91 | 31 | 62 | 9399 | 1507857 | 278425 | 1.36 | 604 | unknown | 0/5 | nothing-left |  |  | full |
| Test-only pin, no production and no SKILL.md change (SKILL.md already orders every survivors run correctly, so this case passes against the unmodified tree and takes the pin path): for every place SKILL.md runs replaces-case-survivors.sh "<step text>" (the Green path's and the pin path's alike, not only the first occurrence as #1406's case at skill-green-split.test.sh:360 reads), a prose case in skill-green-split.test.sh checks it comes before the verify-green launch it gates within the same path, and goes red naming that SKILL.md line when any one of them is moved after its launch ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 11 | 22 | 7130 | 565798 | 101278 | 0.53 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| replaces-case-survivors.sh "<step text>" on a plain step text carrying no ⟦replaces-case⟧ mark exits 3 with nothing on stdout and no Python traceback on stderr (today: AttributeError 'NoneType' object has no attribute 'end', exit 2); pinned by a small pytest case in tests/py/test_replaces_case_survivors.py driving the module through run_cli ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 87 | 0.43 |
| SKILL.md's Green Verify sub-step line that runs replaces-case-survivors.sh "<step text>" before the verify-green launch says it runs only on a ⟦replaces-case⟧ step, as the pin-path paragraph already does, so a conductor reading it on an ordinary step runs nothing; pinned by a prose case in skill-green-split.test.sh that goes red when that line carries no ⟦replaces-case⟧ qualifier ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 85 | 0.43 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 | 0 | 1 | 8 |
| fast | 58 | 58 | 58 | 57 | 59 | 52 |  |
| target | 1 | 1 | 1 | 2 | 1 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 82 | 160 | 28421 | 3854251 | 745312 | 3.65 |
