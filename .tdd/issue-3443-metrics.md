### 📊 Metrics — issue 3443

Wall time for the issue: 2043 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3462.
Lane: ready-for-agent:mu
Suite flakes: skills/tdd/scripts/tests/py/test_run_conductor_process.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $10.43 over 212 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 77571 tokens, largest 152579 tokens
Conductor context: first turn 77587 tokens, largest 135941 tokens
Conductor context: first turn 77922 tokens, largest 160646 tokens
Conductor context: first turn 77916 tokens, largest 147764 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.49 | 77571 |
| 2 | $0.07 | 83578 |
| 3 | $0.04 | 85022 |
| 4 | $0.04 | 86905 |
| 5 | $0.03 | 87206 |
| 6 | $0.03 | 87526 |
| 7 | $0.03 | 87816 |
| 8 | $0.03 | 88253 |
| 9 | $0.03 | 88558 |
| 10 | $0.03 | 89248 |
| 11 | $0.03 | 89848 |
| 12 | $0.04 | 91179 |
| 13 | $0.03 | 92143 |
| 14 | $0.03 | 92383 |
| 15 | $0.03 | 93023 |
| 16 | $0.04 | 93533 |
| 17 | $0.03 | 94057 |
| 18 | $0.03 | 94454 |
| 19 | $0.04 | 95824 |
| 20 | $0.03 | 96375 |
| 21 | $0.04 | 97858 |
| 22 | $0.03 | 98549 |
| 23 | $0.04 | 99285 |
| 24 | $0.03 | 99506 |
| 25 | $0.03 | 100161 |
| 26 | $0.04 | 100450 |
| 27 | $0.03 | 101139 |
| 28 | $0.04 | 102381 |
| 29 | $0.04 | 103209 |
| 30 | $0.10 | 112709 |
| 31 | $0.04 | 113543 |
| 32 | $0.04 | 114768 |
| 33 | $0.04 | 115719 |
| 34 | $0.04 | 116236 |
| 35 | $0.04 | 117298 |
| 36 | $0.04 | 119179 |
| 37 | $0.04 | 120069 |
| 38 | $0.05 | 121805 |
| 39 | $0.05 | 123199 |
| 40 | $0.04 | 124044 |
| 41 | $0.04 | 124989 |
| 42 | $0.04 | 125814 |
| 43 | $0.04 | 126677 |
| 44 | $0.04 | 127489 |
| 45 | $0.04 | 128293 |
| 46 | $0.04 | 128790 |
| 47 | $0.04 | 129423 |
| 48 | $0.04 | 130230 |
| 49 | $0.04 | 130828 |
| 50 | $0.05 | 132029 |
| 51 | $0.16 | 147535 |
| 52 | $0.04 | 147843 |
| 53 | $0.04 | 148132 |
| 54 | $0.04 | 148601 |
| 55 | $0.04 | 148840 |
| 56 | $0.04 | 149096 |
| 57 | $0.04 | 149520 |
| 58 | $0.04 | 149803 |
| 59 | $0.05 | 150169 |
| 60 | $0.04 | 150484 |
| 61 | $0.05 | 151484 |
| 62 | $0.04 | 152414 |
| 63 | $0.04 | 152579 |
| 64 | $0.49 | 77587 |
| 65 | $0.07 | 83562 |
| 66 | $0.04 | 84962 |
| 67 | $0.04 | 86892 |
| 68 | $0.03 | 88077 |
| 69 | $0.06 | 92385 |
| 70 | $0.03 | 92832 |
| 71 | $0.03 | 93166 |
| 72 | $0.03 | 93473 |
| 73 | $0.04 | 94074 |
| 74 | $0.03 | 95003 |
| 75 | $0.04 | 96040 |
| 76 | $0.03 | 96791 |
| 77 | $0.03 | 97298 |
| 78 | $0.04 | 98045 |
| 79 | $0.03 | 98670 |
| 80 | $0.04 | 100652 |
| 81 | $0.04 | 101610 |
| 82 | $0.03 | 102138 |
| 83 | $0.04 | 102781 |
| 84 | $0.03 | 103553 |
| 85 | $0.04 | 104200 |
| 86 | $0.03 | 104760 |
| 87 | $0.04 | 105913 |
| 88 | $0.04 | 106754 |
| 89 | $0.03 | 107457 |
| 90 | $0.04 | 108039 |
| 91 | $0.03 | 108538 |
| 92 | $0.04 | 109232 |
| 93 | $0.03 | 109697 |
| 94 | $0.04 | 110322 |
| 95 | $0.03 | 111135 |
| 96 | $0.04 | 111590 |
| 97 | $0.04 | 112816 |
| 98 | $0.16 | 128524 |
| 99 | $0.03 | 128832 |
| 100 | $0.04 | 129189 |
| 101 | $0.04 | 129769 |
| 102 | $0.04 | 130421 |
| 103 | $0.04 | 130944 |
| 104 | $0.03 | 131312 |
| 105 | $0.04 | 131854 |
| 106 | $0.04 | 132399 |
| 107 | $0.04 | 132771 |
| 108 | $0.04 | 133093 |
| 109 | $0.05 | 134495 |
| 110 | $0.04 | 135628 |
| 111 | $0.04 | 135941 |
| 112 | $0.49 | 77922 |
| 113 | $0.07 | 83931 |
| 114 | $0.05 | 86539 |
| 115 | $0.04 | 88579 |
| 116 | $0.03 | 89223 |
| 117 | $0.04 | 90650 |
| 118 | $0.03 | 91173 |
| 119 | $0.03 | 91658 |
| 120 | $0.03 | 91975 |
| 121 | $0.03 | 92472 |
| 122 | $0.03 | 92791 |
| 123 | $0.02 | 93078 |
| 124 | $0.04 | 93859 |
| 125 | $0.03 | 94341 |
| 126 | $0.06 | 98632 |
| 127 | $0.03 | 99086 |
| 128 | $0.03 | 99644 |
| 129 | $0.04 | 100293 |
| 130 | $0.03 | 101685 |
| 131 | $0.04 | 102278 |
| 132 | $0.03 | 102856 |
| 133 | $0.03 | 103235 |
| 134 | $0.04 | 103816 |
| 135 | $0.14 | 118595 |
| 136 | $0.06 | 122081 |
| 137 | $0.04 | 122808 |
| 138 | $0.04 | 123469 |
| 139 | $0.04 | 124949 |
| 140 | $0.05 | 126373 |
| 141 | $0.04 | 127642 |
| 142 | $0.04 | 128860 |
| 143 | $0.05 | 130343 |
| 144 | $0.04 | 131037 |
| 145 | $0.04 | 131850 |
| 146 | $0.04 | 133052 |
| 147 | $0.04 | 133418 |
| 148 | $0.04 | 134495 |
| 149 | $0.16 | 150117 |
| 150 | $0.04 | 150456 |
| 151 | $0.05 | 150916 |
| 152 | $0.04 | 151632 |
| 153 | $0.05 | 152787 |
| 154 | $0.04 | 153918 |
| 155 | $0.05 | 154892 |
| 156 | $0.05 | 155617 |
| 157 | $0.04 | 155955 |
| 158 | $0.04 | 156251 |
| 159 | $0.04 | 156589 |
| 160 | $0.04 | 156880 |
| 161 | $0.05 | 157259 |
| 162 | $0.04 | 157581 |
| 163 | $0.05 | 159080 |
| 164 | $0.05 | 160390 |
| 165 | $0.04 | 160646 |
| 166 | $0.48 | 77916 |
| 167 | $0.06 | 83920 |
| 168 | $0.04 | 86457 |
| 169 | $0.03 | 88515 |
| 170 | $0.03 | 90435 |
| 171 | $0.02 | 91124 |
| 172 | $0.02 | 91609 |
| 173 | $0.02 | 91922 |
| 174 | $0.02 | 92318 |
| 175 | $0.02 | 93091 |
| 176 | $0.06 | 97670 |
| 177 | $0.03 | 98417 |
| 178 | $0.03 | 99220 |
| 179 | $0.02 | 99654 |
| 180 | $0.02 | 100028 |
| 181 | $0.04 | 102021 |
| 182 | $0.03 | 102780 |
| 183 | $0.02 | 103252 |
| 184 | $0.02 | 103653 |
| 185 | $0.09 | 112809 |
| 186 | $0.05 | 116334 |
| 187 | $0.03 | 116969 |
| 188 | $0.03 | 117209 |
| 189 | $0.03 | 117910 |
| 190 | $0.03 | 118557 |
| 191 | $0.03 | 119606 |
| 192 | $0.03 | 120357 |
| 193 | $0.03 | 121347 |
| 194 | $0.03 | 122185 |
| 195 | $0.03 | 122469 |
| 196 | $0.03 | 123278 |
| 197 | $0.03 | 124216 |
| 198 | $0.15 | 139712 |
| 199 | $0.03 | 140048 |
| 200 | $0.03 | 140529 |
| 201 | $0.03 | 141257 |
| 202 | $0.04 | 142675 |
| 203 | $0.04 | 143590 |
| 204 | $0.04 | 144396 |
| 205 | $0.03 | 144716 |
| 206 | $0.03 | 145010 |
| 207 | $0.03 | 145364 |
| 208 | $0.03 | 145797 |
| 209 | $0.03 | 146454 |
| 210 | $0.03 | 147015 |
| 211 | $0.03 | 147367 |
| 212 | $0.03 | 147764 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 4 | 1777 | $0.04 |
| 🟢 Green | 3 | 1327 | $0.03 |
| 🛠️ Refactor | 2 | 877 | $0.02 |
| 🔎 verify-green | 3 | 1327 | $0.03 |
| 🔎 verify-refactor | 2 | 877 | $0.02 |
| 🔎 verify-<phase> (revised) | 2 | 900 | $0.02 |
| 🗺️ Plan | 1 | 450 | $0.01 |
| 🗺️ verify-plan | 6 | 1701 | $0.03 |
| ▶️ Resuming | 3 | 827 | $0.02 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 20 | 7409 | $0.15 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 6 | 4 | 2 | 0 | 67 | 50 | 6 | 12 | 5485 | 10462 | 107492 | 0.32 |
| red | 10 | 3 | 1 | 0 | 522 | 264 | 63 | 114 | 27318 | 1122081 | 240536 | 1.10 |
| green | 8 | 2 | 2 | 0 | 1460 | 186 | 53 | 94 | 15132 | 850493 | 136270 | 0.66 |
| red-missing | 1 | 0 | 0 | 0 | 25 | 19 | 3 | 6 | 2527 | 39523 | 23252 | 0.09 |
| refactor | 3 | 1 | 0 | 0 | 158 | 38 | 14 | 28 | 2561 | 219910 | 48754 | 0.17 |
| pin | 3 | 1 | 2 | 0 | 72 | 52 | 14 | 28 | 6034 | 229919 | 49118 | 0.21 |
| prose | 7 | 0 | 0 | 0 | 240 | 227 | 7 | 14 | 34631 | 51084 | 383805 | 1.31 |
| skill-edit | 1 | 0 | 0 | 0 | 17 | 16 | 4 | 8 | 853 | 227374 | 68623 | 0.20 |
| rebase | 4 | 2 | 0 | 0 | 573 | 65 | 22 | 40 | 4790 | 308925 | 84909 | 0.29 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 20 | 13 | 7 | 0 | 1705 | 287 | 69 | 134 | 28221 | 987545 | 342856 | 1.24 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 128 | 71 | 15 | 26 | 6112 | 259380 | 57170 | 0.34 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 1044 | 316 | 91 | 162 | 29514 | 1534388 | 290305 | 1.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 303 | 0.51 | 76 | 0.23 |
| green | 1940 | 1.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 49 | 0.14 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 268 | 0.13 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After `tests-frozen.sh record --step` records a step whose text carries `⟦guard-subject: <file>⟧`, a Red case in another file and a changed non-Red case in that guard-subject file, a later step changing the non-Red case passes `tests-frozen.sh check-earlier` (exit 0), while a later step changing the earlier step's own Red case still exits 1 naming it — one test with the contrast, a medium case driving real git in a temporary repository ⟦criterion 1⟧ | 14 | 4 | 3 | 0 | 0 | 0 | 316 | 79 | 144 | 25990 | 1257472 | 250984 | 1.20 | 1856 | green 1/2, red 1/2 | 1/5 | nothing-structural |  |  | full |
| record --step on a guard-subject file freezes the step's own Red case and none of the file's other cases; one test, with the other case left unfrozen as the contrast, and a second guard-subject path sharing a prefix with the first so a substring or prefix match in _guard_subjects is caught ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 107 | 29 | 56 | 10737 | 499571 | 110313 | 0.43 | 1055 | unknown | 0/5 | nothing-left |  |  | full |
| record --step freezes a changed non-Red case in a file that shares a name prefix with a guard subject but is not one; one test, with guard subject `tests/test_guard.py` and the non-subject file `tests/test_guard_more.py`, asserting the non-subject file's changed non-Red case is frozen ⟦added⟧ ⟦criterion 1⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 45 | 12 | 22 | 5007 | 209842 | 45129 | 0.18 | unknown | unknown | unknown | unknown |  |  | full |
| `skills/tdd/SCRIPTS.md`: the tests-frozen.sh entry says `record --step` freezes, in the file a `⟦guard-subject: <path>⟧` marker names, only the step's own Red cases and none of that file's other changed cases, beside the existing `check --step` exemption ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 1⟧ | 7 | 1 | 0 | 0 | 0 | 0 | 146 | 19 | 36 | 17628 | 427287 | 293036 | 0.95 | unknown | unknown | unknown | unknown |  |  | full |
| record --step keeps frozen a changed non-Red case in a file that is not a guard subject but whose path ends with one: guard subject `tests/test_guard.py`, non-subject `projects/x/tests/test_guard.py`; a later step changing that non-Red case makes `tests-frozen.sh check-earlier` exit 1 naming it (catches a `s in name` match in place of exact membership in `_guard_subjects` in skills/tdd/scripts/veri/tests_frozen.py); one new pin case, a medium case driving real git in a temporary repository, no production change ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 16 | 26 | 5918 | 278733 | 50111 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| record --step keeps frozen a changed non-Red case in a file that is not a guard subject but whose path is a suffix of one: guard subject `projects/x/tests/test_guard.py`, non-subject `tests/test_guard.py`; a later step changing that non-Red case makes `tests-frozen.sh check-earlier` exit 1 naming it (catches a `name in s` match in place of exact membership in `_guard_subjects` in skills/tdd/scripts/veri/tests_frozen.py); one new pin case, a medium case driving real git in a temporary repository, no production change ⟦added⟧ ⟦criterion 1⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 47 | 11 | 22 | 5920 | 216308 | 41393 | 0.18 | unknown | unknown | unknown | unknown |  |  | full |
| record --step keeps frozen a changed non-Red case in a file that is not a guard subject but whose path is a suffix of one: guard subject `projects/x/tests/test_guard.py`, non-subject `tests/test_guard.py`; a later step changing that non-Red case makes `tests-frozen.sh check-earlier` exit 1 naming it (catches a `name in s` match in place of exact membership in `_guard_subjects` in skills/tdd/scripts/veri/tests_frozen.py); one new pin case, a medium case driving real git in a temporary repository, no production change ⟦added⟧ ⟦criterion 1⟧ ⟂ retired unpinnable | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 11 | 20 | 2257 | 156415 | 37826 | 0.13 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| After `tests-frozen.sh record --step` records a step whose text carries `⟦guard-subject: <file>⟧`, a Red case in another file and a changed non-Red case in that guard-subject file, a later step changing the non-Red case passes `tests-frozen.sh check-earlier` (exit 0), while a later step changing the earlier step's own Red case still exits 1 naming it — one test with the contrast, a medium case driving real git in a temporary repository ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 144 | 0.11 |
| record --step on a guard-subject file freezes the step's own Red case and none of the file's other cases; one test, with the other case left unfrozen as the contrast, and a second guard-subject path sharing a prefix with the first so a substring or prefix match in _guard_subjects is caught ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| After `tests-frozen.sh record --step` records a step whose text carries `⟦guard-subject: <file>⟧`, a Red case in another file and a changed non-Red case in that guard-subject file, a later step changing the non-Red case passes `tests-frozen.sh check-earlier` (exit 0), while a later step changing the earlier step's own Red case still exits 1 naming it — one test with the contrast, a medium case driving real git in a temporary repository ⟦criterion 1⟧ | 1 | 1 | 0 | nothing-structural 1 |
| record --step on a guard-subject file freezes the step's own Red case and none of the file's other cases; one test, with the other case left unfrozen as the contrast, and a second guard-subject path sharing a prefix with the first so a substring or prefix match in _guard_subjects is caught ⟦added⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 3 | ? | ? | nothing-left 1, nothing-structural 2 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 48 | 2 | 93 | 49 | 15 | 60 | 3 | 54 | 1 | 2 | 72 | 48 | 47 | 42 | 1 | 1 | 53 | 73 | 1 | 13 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 23 | 23 | 23 | 41 | 22 | 27 | 22 | 39 | 21 | 42 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 3 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 4 | 3 | 2 | 1 | 1 | 1 | 1 | 3 | 2 | 2 | 2 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 2 |
| all | 30 | 28 | 208 | 21 | 21 | 190 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 186 | 344 | 99331 | 3059771 | 1142759 | 14.78 (estimate) |
