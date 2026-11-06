### 📊 Metrics — issue 3007

Wall time for the issue: 9748 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3015.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $13.34 over 248 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89710 tokens, largest 214908 tokens
Conductor context: first turn 89727 tokens, largest 136690 tokens
Conductor context: first turn 89892 tokens, largest 236948 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89710 |
| 2 | $0.08 | 96690 |
| 3 | $0.06 | 99327 |
| 4 | $0.04 | 100960 |
| 5 | $0.04 | 101625 |
| 6 | $0.03 | 102022 |
| 7 | $0.04 | 102320 |
| 8 | $0.03 | 102614 |
| 9 | $0.03 | 102871 |
| 10 | $0.04 | 103511 |
| 11 | $0.03 | 103805 |
| 12 | $0.07 | 108345 |
| 13 | $0.07 | 113063 |
| 14 | $0.07 | 116530 |
| 15 | $0.04 | 118197 |
| 16 | $0.05 | 119751 |
| 17 | $0.05 | 121012 |
| 18 | $0.05 | 123951 |
| 19 | $0.05 | 125140 |
| 20 | $0.06 | 128640 |
| 21 | $0.06 | 130382 |
| 22 | $0.04 | 130704 |
| 23 | $0.04 | 131613 |
| 24 | $0.04 | 132044 |
| 25 | $0.08 | 137770 |
| 26 | $0.05 | 138308 |
| 27 | $0.04 | 138828 |
| 28 | $0.15 | 153148 |
| 29 | $0.05 | 153527 |
| 30 | $0.05 | 154262 |
| 31 | $0.04 | 154857 |
| 32 | $0.06 | 156106 |
| 33 | $0.05 | 157159 |
| 34 | $0.05 | 158322 |
| 35 | $0.05 | 159323 |
| 36 | $0.05 | 159641 |
| 37 | $0.05 | 160467 |
| 38 | $0.07 | 163680 |
| 39 | $0.04 | 164077 |
| 40 | $0.05 | 164375 |
| 41 | $0.05 | 165595 |
| 42 | $0.07 | 168289 |
| 43 | $0.05 | 168615 |
| 44 | $0.04 | 169010 |
| 45 | $0.05 | 169202 |
| 46 | $0.05 | 169542 |
| 47 | $0.05 | 169697 |
| 48 | $0.05 | 170367 |
| 49 | $0.05 | 171106 |
| 50 | $0.05 | 172541 |
| 51 | $0.06 | 173341 |
| 52 | $0.05 | 174058 |
| 53 | $0.05 | 174354 |
| 54 | $0.04 | 174533 |
| 55 | $0.06 | 175454 |
| 56 | $0.05 | 176579 |
| 57 | $0.06 | 177445 |
| 58 | $0.05 | 178309 |
| 59 | $0.06 | 179871 |
| 60 | $0.06 | 181210 |
| 61 | $0.05 | 182011 |
| 62 | $0.06 | 183120 |
| 63 | $0.05 | 184031 |
| 64 | $0.06 | 184700 |
| 65 | $0.06 | 186150 |
| 66 | $0.06 | 188069 |
| 67 | $0.06 | 188963 |
| 68 | $0.05 | 189872 |
| 69 | $0.06 | 191079 |
| 70 | $0.09 | 196025 |
| 71 | $0.06 | 197201 |
| 72 | $0.06 | 198390 |
| 73 | $0.06 | 199468 |
| 74 | $0.06 | 199970 |
| 75 | $0.06 | 201851 |
| 76 | $0.07 | 203411 |
| 77 | $0.06 | 204591 |
| 78 | $0.05 | 205115 |
| 79 | $0.06 | 205860 |
| 80 | $0.06 | 206556 |
| 81 | $0.07 | 208282 |
| 82 | $0.09 | 212884 |
| 83 | $0.06 | 213651 |
| 84 | $0.06 | 214908 |
| 85 | $0.59 | 89727 |
| 86 | $0.08 | 96712 |
| 87 | $0.05 | 99383 |
| 88 | $0.04 | 101290 |
| 89 | $0.04 | 103219 |
| 90 | $0.04 | 104279 |
| 91 | $0.03 | 104816 |
| 92 | $0.04 | 105198 |
| 93 | $0.03 | 105981 |
| 94 | $0.03 | 106433 |
| 95 | $0.03 | 106717 |
| 96 | $0.04 | 107055 |
| 97 | $0.03 | 107338 |
| 98 | $0.03 | 107579 |
| 99 | $0.03 | 108035 |
| 100 | $0.04 | 108341 |
| 101 | $0.03 | 108687 |
| 102 | $0.03 | 109372 |
| 103 | $0.07 | 113447 |
| 104 | $0.05 | 116623 |
| 105 | $0.04 | 117521 |
| 106 | $0.04 | 118093 |
| 107 | $0.03 | 118760 |
| 108 | $0.05 | 120070 |
| 109 | $0.03 | 120520 |
| 110 | $0.04 | 121872 |
| 111 | $0.04 | 122234 |
| 112 | $0.04 | 122882 |
| 113 | $0.04 | 123595 |
| 114 | $0.03 | 123912 |
| 115 | $0.04 | 124596 |
| 116 | $0.04 | 125225 |
| 117 | $0.05 | 127322 |
| 118 | $0.04 | 128543 |
| 119 | $0.04 | 129305 |
| 120 | $0.07 | 134189 |
| 121 | $0.05 | 135383 |
| 122 | $0.04 | 136690 |
| 123 | $0.58 | 89892 |
| 124 | $0.07 | 96866 |
| 125 | $0.04 | 99972 |
| 126 | $0.04 | 102895 |
| 127 | $0.04 | 105764 |
| 128 | $0.07 | 112064 |
| 129 | $0.03 | 112816 |
| 130 | $0.03 | 113495 |
| 131 | $0.02 | 113770 |
| 132 | $0.03 | 114470 |
| 133 | $0.03 | 114947 |
| 134 | $0.03 | 115662 |
| 135 | $0.04 | 117548 |
| 136 | $0.04 | 119841 |
| 137 | $0.04 | 121970 |
| 138 | $0.03 | 122547 |
| 139 | $0.03 | 123140 |
| 140 | $0.03 | 123908 |
| 141 | $0.03 | 124094 |
| 142 | $0.04 | 125597 |
| 143 | $0.03 | 126189 |
| 144 | $0.03 | 126704 |
| 145 | $0.05 | 129947 |
| 146 | $0.03 | 130613 |
| 147 | $0.03 | 130951 |
| 148 | $0.04 | 132834 |
| 149 | $0.04 | 134000 |
| 150 | $0.03 | 134539 |
| 151 | $0.03 | 135456 |
| 152 | $0.03 | 136067 |
| 153 | $0.03 | 136402 |
| 154 | $0.03 | 137360 |
| 155 | $0.03 | 138256 |
| 156 | $0.04 | 139327 |
| 157 | $0.03 | 139732 |
| 158 | $0.03 | 140305 |
| 159 | $0.04 | 141331 |
| 160 | $0.03 | 142049 |
| 161 | $0.04 | 142942 |
| 162 | $0.03 | 143339 |
| 163 | $0.03 | 144046 |
| 164 | $0.03 | 144644 |
| 165 | $0.03 | 145017 |
| 166 | $0.03 | 145709 |
| 167 | $0.03 | 146339 |
| 168 | $0.04 | 147121 |
| 169 | $0.04 | 148073 |
| 170 | $0.04 | 149066 |
| 171 | $0.03 | 149610 |
| 172 | $0.04 | 150245 |
| 173 | $0.03 | 150534 |
| 174 | $0.04 | 151525 |
| 175 | $0.10 | 160824 |
| 176 | $0.04 | 161432 |
| 177 | $0.07 | 165644 |
| 178 | $0.05 | 167462 |
| 179 | $0.09 | 174618 |
| 180 | $0.05 | 176595 |
| 181 | $0.05 | 178514 |
| 182 | $0.04 | 179477 |
| 183 | $0.05 | 180753 |
| 184 | $0.04 | 181453 |
| 185 | $0.05 | 182668 |
| 186 | $0.04 | 183721 |
| 187 | $0.05 | 184943 |
| 188 | $0.06 | 187646 |
| 189 | $0.04 | 188356 |
| 190 | $0.05 | 190074 |
| 191 | $0.05 | 191287 |
| 192 | $0.04 | 191622 |
| 193 | $0.05 | 192512 |
| 194 | $0.04 | 193181 |
| 195 | $0.05 | 194316 |
| 196 | $0.04 | 195074 |
| 197 | $0.05 | 195958 |
| 198 | $0.05 | 197445 |
| 199 | $0.05 | 198321 |
| 200 | $0.05 | 199483 |
| 201 | $0.05 | 200516 |
| 202 | $0.05 | 201371 |
| 203 | $0.05 | 202587 |
| 204 | $0.05 | 203308 |
| 205 | $0.05 | 204275 |
| 206 | $0.05 | 205036 |
| 207 | $0.05 | 205814 |
| 208 | $0.05 | 206600 |
| 209 | $0.05 | 207358 |
| 210 | $0.05 | 208254 |
| 211 | $0.05 | 208859 |
| 212 | $0.04 | 209160 |
| 213 | $0.05 | 210593 |
| 214 | $0.05 | 211408 |
| 215 | $0.05 | 212587 |
| 216 | $0.06 | 214281 |
| 217 | $0.04 | 214494 |
| 218 | $0.05 | 215307 |
| 219 | $0.05 | 216191 |
| 220 | $0.05 | 216808 |
| 221 | $0.06 | 218574 |
| 222 | $0.05 | 219499 |
| 223 | $0.05 | 219852 |
| 224 | $0.05 | 220170 |
| 225 | $0.05 | 220611 |
| 226 | $0.05 | 221270 |
| 227 | $0.05 | 221930 |
| 228 | $0.09 | 227252 |
| 229 | $0.05 | 227951 |
| 230 | $0.05 | 228524 |
| 231 | $0.05 | 229234 |
| 232 | $0.05 | 229785 |
| 233 | $0.05 | 230300 |
| 234 | $0.05 | 230505 |
| 235 | $0.05 | 230786 |
| 236 | $0.05 | 231085 |
| 237 | $0.05 | 231403 |
| 238 | $0.05 | 231850 |
| 239 | $0.05 | 232572 |
| 240 | $0.05 | 233138 |
| 241 | $0.06 | 234188 |
| 242 | $0.06 | 235232 |
| 243 | $0.05 | 235943 |
| 244 | $0.05 | 236183 |
| 245 | $0.05 | 236499 |
| 246 | $0.05 | 236948 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 15 | 1 | 2 | 1804 | 0 | 33943 | 0.10 |
| red | 18 | 5 | 1 | 0 | 1035 | 400 | 95 | 188 | 35467 | 2961621 | 561112 | 2.46 |
| green | 8 | 3 | 0 | 0 | 1295 | 212 | 43 | 82 | 19076 | 1349495 | 173698 | 0.76 |
| refactor | 5 | 1 | 0 | 0 | 165 | 56 | 16 | 32 | 4232 | 442786 | 126176 | 0.56 |
| diff | 11 | 5 | 1 | 0 | 1344 | 349 | 77 | 150 | 33786 | 2582360 | 477832 | 2.08 |
| pin | 4 | 3 | 1 | 0 | 174 | 54 | 13 | 26 | 4559 | 340999 | 83748 | 0.29 |
| prose | 14 | 0 | 0 | 0 | 258 | 222 | 14 | 28 | 36186 | 36363 | 264562 | 1.03 |
| skill-edit | 2 | 0 | 0 | 0 | 24 | 18 | 7 | 14 | 1901 | 161925 | 41539 | 0.14 |
| rebase | 2 | 1 | 0 | 0 | 1471 | 38 | 15 | 30 | 3940 | 414998 | 106149 | 0.35 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 22 | 19 | 3 | 0 | 2969 | 367 | 89 | 176 | 29252 | 2380311 | 644980 | 2.14 |
| developer | claude-sonnet-5-5 | 21 | 0 | 0 | 0 | 1960 | 577 | 131 | 254 | 56183 | 4309429 | 702129 | 2.94 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 574 | 180 | 40 | 80 | 17429 | 1402519 | 215549 | 1.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 585 | 1.22 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 582 | 0.78 | 0 | 0.00 |
| pin | 127 | 0.16 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `wrong-test-route.sh` prints `red <case>` for a green report carrying a `CONTRADICTS: <case>` line that names an existing test case other than the step's own, beside a `WRONG_TEST:` line whose prose names no case ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 87 | 19 | 36 | 5553 | 519312 | 109864 | 0.38 | 2016 | unknown | 0/5 | nothing-left |  |  | full |
| every existing case in `skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py`, `unit/test_wrong_test_route_prose.py` and `test_wrong_test_route_process.py` whose expected output relies on a case named on a `WRONG_TEST:` line being taken as the contradicted case also carries a `CONTRADICTS:` line naming that case in the same spelling and quoting; test files only, no production change, every suite stays green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 109 | 17 | 34 | 10210 | 649362 | 100447 | 0.42 | 947 | n/a | n/a | n/a |  |  | full |
| `wrong-test-route.sh` prints `repair <the step's own case>`, and never `red`, for a green report whose `WRONG_TEST:` line names an existing test case other than the step's own and which carries no `CONTRADICTS:` line ⟦criterion 1⟧ | 20 | 6 | 2 | 0 | 0 | 0 | 509 | 110 | 216 | 45662 | 3509096 | 628722 | 3.08 | 1262 | diff 1/2, red 2/2, refactor 1/2 | 0/5 | nothing-left |  |  | full |
| every existing case in `skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py` of families 1957, 2172, 2227, 2807 and 2878 that limiting `route()` to `CONTRADICTS:` lines would supersede carries a `CONTRADICTS:` line naming the case its expected output relies on, in the same spelling and quoting, the 2172 and 2807 cases still expecting `revise`; test files only, no production change, every suite stays green ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 20 | 38 | 8497 | 704775 | 106356 | 0.42 | 942 | n/a | n/a | n/a |  |  | full |
| every existing case in `skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py` of families 1621, 1957, 2172, 2227, 2807 and 2878 that expects `red <case>` from a case named on a `WRONG_TEST:` line carries a `CONTRADICTS:` line naming that case, its expectation unchanged, landed in test-only commits before the `route()` change; test files only, no production change ⟦diff-checked⟧ ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 9 | 18 | 3007 | 232084 | 77704 | 0.25 | 392 | n/a | n/a | n/a |  |  | full |
| `wrong-test-route.sh` routes a report naming one case on both its `WRONG_TEST:` line and a `CONTRADICTS:` line by the `CONTRADICTS:` line only: it prints `red <that case>`, and a different existing case cited in the `WRONG_TEST:` prose is not listed in the output ⟦criterion 3⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 77 | 18 | 36 | 7359 | 510200 | 129760 | 0.59 | unknown | 1/2 | unknown | unknown |  |  | pin |
| `wrong-test-route.sh` prints `red <case>` for a `CONTRADICTS:` line naming an existing case in each spelling a `WRONG_TEST:` line accepts today — a bare `test_*` or `Test*` name, backticked, double-quoted, curly-quoted, a backticked path followed by a quoted title, and the `›` form — and for a JS/TS case named as `` `foo.test.ts` "rejects an empty name" `` prints `red` over the title ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 10 | 20 | 3342 | 312262 | 60525 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| `wrong-test-route.sh` does not print `red` for a `CONTRADICTS:` line naming a case that resolves to no defined test: it falls to the existing no-answer path, with the existing stderr diagnostic ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 10 | 20 | 4812 | 336878 | 42572 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| `wrong-test-route.sh` prints `repair <the step's own case>` for a report whose `CONTRADICTS:` line names the step's own case ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 23 | 46 | 6263 | 734276 | 95824 | 0.38 | 734 | unknown | 0/5 | nothing-left |  |  | full |
| the existing `test_main_1957_*`, `test_main_2172_*` and `test_main_2807_*` cases in `skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py` that expect `revise` keep that expectation unchanged on the branch, so a `WRONG_TEST:` line whose names resolve to no defined case other than the step's own (the step's own case, a helper outside a test file, a name defined nowhere) keeps today's route, `revise` or `fixture` ⟦diff-checked⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 14 | 2415 | 169016 | 70792 | 0.22 | 499 | n/a | n/a | n/a |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/develop-green.md`: the report section's `WRONG_TEST:` alternative asks, only when the step's criterion contradicts an existing test case other than the step's own, for a `CONTRADICTS: <case>` line naming that case by its own name as its test file spells it, with no describe, class or file prefix, a case cited only as evidence being named in the `WRONG_TEST:` text and never on a `CONTRADICTS:` line, in the same words as `_develop-wrong-test-report.md`; the `green-wrong-test` REPORT-FORMAT keys include `CONTRADICTS:`; row GN18 stands in the unit's requirements list as the issue states it ⟦skill-edit⟧ ⟦criterion 6⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 41 | 8 | 16 | 5533 | 105037 | 64009 | 0.23 | 81 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/scripts/prompts/_develop-wrong-test-report.md`: the sentences after the `WRONG_TEST:` line tell the leaf to add, only when the step's criterion contradicts an existing test case other than the step's own, a `CONTRADICTS: <case>` line naming it by its own name as its test file spells it, with no describe, class or file prefix, and to name a case cited only as evidence in the `WRONG_TEST:` text, never on that line, in the same words as `develop-green.md`; row WT2 stands in the unit's requirements list as the issue states it ⟦skill-edit⟧ ⟦criterion 6⟧ | 7 | 1 | 0 | 0 | 0 | 0 | 63 | 22 | 44 | 7346 | 500020 | 139486 | 0.47 | 60 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `wrong-test-route.sh` prints `red <case>` for a green report carrying a `CONTRADICTS: <case>` line that names an existing test case other than the step's own, beside a `WRONG_TEST:` line whose prose names no case ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |
| `wrong-test-route.sh` prints `repair <the step's own case>`, and never `red`, for a green report whose `WRONG_TEST:` line names an existing test case other than the step's own and which carries no `CONTRADICTS:` line ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 1 | 148 | 0.46 |
| `wrong-test-route.sh` prints `repair <the step's own case>` for a report whose `CONTRADICTS:` line names the step's own case ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s | run 146 s | run 147 s | run 148 s | run 149 s | run 150 s | run 151 s | run 152 s | run 153 s | run 154 s | run 155 s | run 156 s | run 157 s | run 158 s | run 159 s | run 160 s | run 161 s | run 162 s | run 163 s | run 164 s | run 165 s | run 166 s | run 167 s | run 168 s | run 169 s | run 170 s | run 171 s | run 172 s | run 173 s | run 174 s | run 175 s | run 176 s | run 177 s | run 178 s | run 179 s | run 180 s | run 181 s | run 182 s | run 183 s | run 184 s | run 185 s | run 186 s | run 187 s | run 188 s | run 189 s | run 190 s | run 191 s | run 192 s | run 193 s | run 194 s | run 195 s | run 196 s | run 197 s | run 198 s | run 199 s | run 200 s | run 201 s | run 202 s | run 203 s | run 204 s | run 205 s | run 206 s | run 207 s | run 208 s | run 209 s | run 210 s | run 211 s | run 212 s | run 213 s | run 214 s | run 215 s | run 216 s | run 217 s | run 218 s | run 219 s | run 220 s | run 221 s | run 222 s | run 223 s | run 224 s | run 225 s | run 226 s | run 227 s | run 228 s | run 229 s | run 230 s | run 231 s | run 232 s | run 233 s | run 234 s | run 235 s | run 236 s | run 237 s | run 238 s | run 239 s | run 240 s | run 241 s | run 242 s | run 243 s | run 244 s | run 245 s | run 246 s | run 247 s | run 248 s | run 249 s | run 250 s | run 251 s | run 252 s | run 253 s | run 254 s | run 255 s | run 256 s | run 257 s | run 258 s | run 259 s | run 260 s | run 261 s | run 262 s | run 263 s | run 264 s | run 265 s | run 266 s | run 267 s | run 268 s | run 269 s | run 270 s | run 271 s | run 272 s | run 273 s | run 274 s | run 275 s | run 276 s | run 277 s | run 278 s | run 279 s | run 280 s | run 281 s | run 282 s | run 283 s | run 284 s | run 285 s | run 286 s | run 287 s | run 288 s | run 289 s | run 290 s | run 291 s | run 292 s | run 293 s | run 294 s | run 295 s | run 296 s | run 297 s | run 298 s | run 299 s | run 300 s | run 301 s | run 302 s | run 303 s | run 304 s | run 305 s | run 306 s | run 307 s | run 308 s | run 309 s | run 310 s | run 311 s | run 312 s | run 313 s | run 314 s | run 315 s | run 316 s | run 317 s | run 318 s | run 319 s | run 320 s | run 321 s | run 322 s | run 323 s | run 324 s | run 325 s | run 326 s | run 327 s | run 328 s | run 329 s | run 330 s | run 331 s | run 332 s | run 333 s | run 334 s | run 335 s | run 336 s | run 337 s | run 338 s | run 339 s | run 340 s | run 341 s | run 342 s | run 343 s | run 344 s | run 345 s | run 346 s | run 347 s | run 348 s | run 349 s | run 350 s | run 351 s | run 352 s | run 353 s | run 354 s | run 355 s | run 356 s | run 357 s | run 358 s | run 359 s | run 360 s | run 361 s | run 362 s | run 363 s | run 364 s | run 365 s | run 366 s | run 367 s | run 368 s | run 369 s | run 370 s | run 371 s | run 372 s | run 373 s | run 374 s | run 375 s | run 376 s | run 377 s | run 378 s | run 379 s | run 380 s | run 381 s | run 382 s | run 383 s | run 384 s | run 385 s | run 386 s | run 387 s | run 388 s | run 389 s | run 390 s | run 391 s | run 392 s | run 393 s | run 394 s | run 395 s | run 396 s | run 397 s | run 398 s | run 399 s | run 400 s | run 401 s | run 402 s | run 403 s | run 404 s | run 405 s | run 406 s | run 407 s | run 408 s | run 409 s | run 410 s | run 411 s | run 412 s | run 413 s | run 414 s | run 415 s | run 416 s | run 417 s | run 418 s | run 419 s | run 420 s | run 421 s | run 422 s | run 423 s | run 424 s | run 425 s | run 426 s | run 427 s | run 428 s | run 429 s | run 430 s | run 431 s | run 432 s | run 433 s | run 434 s | run 435 s | run 436 s | run 437 s | run 438 s | run 439 s | run 440 s | run 441 s | run 442 s | run 443 s | run 444 s | run 445 s | run 446 s | run 447 s | run 448 s | run 449 s | run 450 s | run 451 s | run 452 s | run 453 s | run 454 s | run 455 s | run 456 s | run 457 s | run 458 s | run 459 s | run 460 s | run 461 s | run 462 s | run 463 s | run 464 s | run 465 s | run 466 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 11 | 12 | 19 | 15 | 11 | 11 | 11 | 44 | 18 | 23 | 16 | 10 | 12 | 3 | 7 | 4 | 4 | 4 | 0 | 5 | 6 | 5 | 3 | 7 | 7 | 7 | 4 | 5 | 5 | 7 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 89 | 96 | 70 | 64 | 86 | 86 | 31 | 52 | 30 | 38 | 35 | 36 | 31 | 44 | 39 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 7 | 7 | 6 | 6 | 7 | 5 | 6 | 7 | 7 | 7 | 7 | 7 | 6 | 6 | 6 | 6 | 6 | 8 | 9 | 9 | 10 | 10 | 9 | 8 | 9 | 9 | 10 | 11 | 8 | 8 | 8 | 12 | 9 | 8 | 10 | 7 | 8 | 12 | 11 | 11 | 10 | 8 | 11 | 10 | 8 | 9 | 9 | 12 | 18 | 14 | 14 | 11 | 9 | 9 | 9 | 8 | 7 | 10 | 7 | 9 | 9 | 7 | 7 | 10 | 7 | 9 | 8 | 8 | 11 | 9 | 10 | 7 | 6 | 7 | 8 | 8 | 7 | 7 | 6 | 6 | 7 | 7 | 6 | 8 | 8 | 7 | 8 | 8 | 7 | 7 | 8 | 7 | 6 | 7 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 6 | 7 | 13 | 8 | 9 | 7 | 8 | 7 | 8 | 8 | 9 | 6 | 7 | 7 | 7 | 8 | 8 | 10 | 7 | 8 | 7 | 10 | 9 | 8 | 9 | 8 | 10 | 11 | 8 | 7 | 9 | 18 | 13 | 12 | 7 | 7 | 8 | 8 | 7 | 10 | 5 | 5 | 5 | 5 | 4 | 6 | 9 | 6 | 5 | 7 | 5 | 5 | 4 | 4 | 5 | 6 | 8 | 5 | 5 | 4 | 4 | 4 | 5 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 3 | 3 | 4 | 4 | 6 | 5 | 6 | 2 | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 4 | 3 | 5 | 6 | 11 | 6 | 7 | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 5 | 5 | 5 | 4 | 5 | 3 | 5 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 5 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 5 | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 6 | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 6 | 4 | 4 | 4 | 3 | 5 | 5 | 6 | 4 | 3 | 3 | 4 | 7 | 4 | 4 | 2 | 2 | 2 | 2 | 2 | 4 | 4 | 3 | 3 | 4 | 3 | 4 | 4 | 3 | 3 | 3 | 3 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 3 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 5 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 5 | 5 | 44 | 39 | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 6 | 6 | 6 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 8 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 33 | 3 | 3 | 3 | 5 | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 3 | 4 | 6 | 4 | 5 | 4 | 4 | 4 | 4 | 3 | 4 | 5 | 35 | 4 | 3 | 3 |
| all | 52 | 51 | 1301 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 281 | 552 | 140951 | 8290547 | 1868759 | 21.10 (estimate) |
