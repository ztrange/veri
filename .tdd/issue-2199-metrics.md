### 📊 Metrics — issue 2199

Wall time for the issue: 2530 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 10 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2256.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $15.64 over 323 turns, in 4 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89183 |
| 2 | $0.04 | 90296 |
| 3 | $0.04 | 92198 |
| 4 | $0.04 | 92468 |
| 5 | $0.03 | 92836 |
| 6 | $0.04 | 93401 |
| 7 | $0.04 | 93959 |
| 8 | $0.03 | 94526 |
| 9 | $0.05 | 95561 |
| 10 | $0.06 | 99665 |
| 11 | $0.12 | 110338 |
| 12 | $0.05 | 112644 |
| 13 | $0.09 | 118371 |
| 14 | $0.07 | 123433 |
| 15 | $0.06 | 125999 |
| 16 | $0.05 | 126868 |
| 17 | $0.05 | 128172 |
| 18 | $0.06 | 130465 |
| 19 | $0.06 | 133724 |
| 20 | $0.05 | 134144 |
| 21 | $0.04 | 134835 |
| 22 | $0.05 | 135630 |
| 23 | $0.04 | 135872 |
| 24 | $0.05 | 136826 |
| 25 | $0.05 | 138067 |
| 26 | $0.04 | 138375 |
| 27 | $0.05 | 139099 |
| 28 | $0.05 | 140151 |
| 29 | $0.05 | 141433 |
| 30 | $0.05 | 142287 |
| 31 | $0.05 | 143207 |
| 32 | $0.05 | 143952 |
| 33 | $0.05 | 144884 |
| 34 | $0.05 | 145483 |
| 35 | $0.05 | 146444 |
| 36 | $0.04 | 147034 |
| 37 | $0.05 | 147944 |
| 38 | $0.06 | 149242 |
| 39 | $0.05 | 150352 |
| 40 | $0.06 | 151947 |
| 41 | $0.06 | 153908 |
| 42 | $0.06 | 155601 |
| 43 | $0.05 | 156768 |
| 44 | $0.05 | 157897 |
| 45 | $0.06 | 159118 |
| 46 | $0.05 | 160196 |
| 47 | $0.06 | 162307 |
| 48 | $0.06 | 163389 |
| 49 | $0.06 | 165166 |
| 50 | $0.05 | 166081 |
| 51 | $0.06 | 167248 |
| 52 | $0.06 | 168472 |
| 53 | $0.05 | 169574 |
| 54 | $0.07 | 171467 |
| 55 | $0.05 | 172367 |
| 56 | $0.06 | 173992 |
| 57 | $0.06 | 174915 |
| 58 | $0.06 | 177123 |
| 59 | $0.07 | 179555 |
| 60 | $0.06 | 180560 |
| 61 | $0.05 | 180870 |
| 62 | $0.06 | 181640 |
| 63 | $0.05 | 182147 |
| 64 | $0.06 | 182473 |
| 65 | $0.05 | 183242 |
| 66 | $0.06 | 183788 |
| 67 | $0.05 | 184791 |
| 68 | $0.06 | 185041 |
| 69 | $0.05 | 185392 |
| 70 | $0.05 | 185779 |
| 71 | $0.06 | 186784 |
| 72 | $0.06 | 187191 |
| 73 | $0.05 | 187725 |
| 74 | $0.06 | 188648 |
| 75 | $0.06 | 189591 |
| 76 | $0.06 | 190090 |
| 77 | $0.05 | 190824 |
| 78 | $0.06 | 191401 |
| 79 | $0.06 | 192013 |
| 80 | $0.06 | 193278 |
| 81 | $0.06 | 194049 |
| 82 | $0.06 | 195024 |
| 83 | $0.06 | 195650 |
| 84 | $0.05 | 196245 |
| 85 | $0.06 | 196980 |
| 86 | $0.06 | 197853 |
| 87 | $0.06 | 198549 |
| 88 | $0.06 | 199526 |
| 89 | $0.06 | 200373 |
| 90 | $0.59 | 89186 |
| 91 | $0.04 | 90820 |
| 92 | $0.03 | 91446 |
| 93 | $0.04 | 92811 |
| 94 | $0.11 | 102547 |
| 95 | $0.04 | 102998 |
| 96 | $0.03 | 103413 |
| 97 | $0.04 | 103762 |
| 98 | $0.03 | 104039 |
| 99 | $0.04 | 104715 |
| 100 | $0.04 | 105414 |
| 101 | $0.04 | 105787 |
| 102 | $0.04 | 106878 |
| 103 | $0.04 | 108485 |
| 104 | $0.06 | 110791 |
| 105 | $0.06 | 114245 |
| 106 | $0.04 | 114823 |
| 107 | $0.06 | 118557 |
| 108 | $0.05 | 120061 |
| 109 | $0.04 | 120510 |
| 110 | $0.04 | 121406 |
| 111 | $0.04 | 122143 |
| 112 | $0.05 | 123529 |
| 113 | $0.05 | 124549 |
| 114 | $0.04 | 124943 |
| 115 | $0.04 | 125463 |
| 116 | $0.05 | 127187 |
| 117 | $0.04 | 128419 |
| 118 | $0.05 | 128850 |
| 119 | $0.04 | 129475 |
| 120 | $0.10 | 137230 |
| 121 | $0.06 | 139434 |
| 122 | $0.04 | 140247 |
| 123 | $0.05 | 141840 |
| 124 | $0.06 | 143454 |
| 125 | $0.04 | 143897 |
| 126 | $0.04 | 144164 |
| 127 | $0.06 | 146630 |
| 128 | $0.05 | 147724 |
| 129 | $0.06 | 148959 |
| 130 | $0.05 | 151024 |
| 131 | $0.05 | 151806 |
| 132 | $0.05 | 151984 |
| 133 | $0.04 | 152237 |
| 134 | $0.04 | 152584 |
| 135 | $0.06 | 153862 |
| 136 | $0.08 | 159291 |
| 137 | $0.06 | 161221 |
| 138 | $0.06 | 162741 |
| 139 | $0.06 | 164483 |
| 140 | $0.05 | 165528 |
| 141 | $0.05 | 166454 |
| 142 | $0.06 | 168116 |
| 143 | $0.05 | 168617 |
| 144 | $0.05 | 169602 |
| 145 | $0.06 | 170778 |
| 146 | $0.05 | 171763 |
| 147 | $0.06 | 173161 |
| 148 | $0.07 | 175658 |
| 149 | $0.05 | 176307 |
| 150 | $0.05 | 177404 |
| 151 | $0.08 | 181456 |
| 152 | $0.12 | 190406 |
| 153 | $0.07 | 191849 |
| 154 | $0.59 | 89487 |
| 155 | $0.03 | 89823 |
| 156 | $0.04 | 91231 |
| 157 | $0.03 | 91875 |
| 158 | $0.04 | 93252 |
| 159 | $0.04 | 95560 |
| 160 | $0.04 | 95894 |
| 161 | $0.03 | 96354 |
| 162 | $0.03 | 96754 |
| 163 | $0.03 | 97113 |
| 164 | $0.03 | 97483 |
| 165 | $0.04 | 98114 |
| 166 | $0.06 | 101574 |
| 167 | $0.04 | 102899 |
| 168 | $0.04 | 104947 |
| 169 | $0.04 | 105700 |
| 170 | $0.04 | 106377 |
| 171 | $0.03 | 106605 |
| 172 | $0.04 | 108002 |
| 173 | $0.04 | 108626 |
| 174 | $0.03 | 109025 |
| 175 | $0.04 | 109587 |
| 176 | $0.03 | 110061 |
| 177 | $0.04 | 111075 |
| 178 | $0.05 | 112199 |
| 179 | $0.03 | 112924 |
| 180 | $0.04 | 113260 |
| 181 | $0.04 | 114187 |
| 182 | $0.04 | 114790 |
| 183 | $0.03 | 115521 |
| 184 | $0.04 | 116175 |
| 185 | $0.04 | 116746 |
| 186 | $0.04 | 117132 |
| 187 | $0.04 | 117874 |
| 188 | $0.04 | 118745 |
| 189 | $0.04 | 119533 |
| 190 | $0.04 | 120367 |
| 191 | $0.04 | 121182 |
| 192 | $0.04 | 122133 |
| 193 | $0.04 | 123121 |
| 194 | $0.05 | 124670 |
| 195 | $0.03 | 125127 |
| 196 | $0.06 | 127344 |
| 197 | $0.04 | 128000 |
| 198 | $0.04 | 128962 |
| 199 | $0.04 | 129216 |
| 200 | $0.04 | 129876 |
| 201 | $0.04 | 130822 |
| 202 | $0.05 | 131932 |
| 203 | $0.05 | 133489 |
| 204 | $0.09 | 140668 |
| 205 | $0.05 | 141796 |
| 206 | $0.05 | 143080 |
| 207 | $0.04 | 143464 |
| 208 | $0.04 | 144234 |
| 209 | $0.04 | 144847 |
| 210 | $0.05 | 145765 |
| 211 | $0.05 | 146628 |
| 212 | $0.04 | 146953 |
| 213 | $0.05 | 148766 |
| 214 | $0.05 | 149738 |
| 215 | $0.04 | 150263 |
| 216 | $0.05 | 151287 |
| 217 | $0.05 | 152365 |
| 218 | $0.05 | 153069 |
| 219 | $0.07 | 157855 |
| 220 | $0.05 | 158641 |
| 221 | $0.05 | 159696 |
| 222 | $0.05 | 160819 |
| 223 | $0.58 | 90203 |
| 224 | $0.02 | 90826 |
| 225 | $0.02 | 91311 |
| 226 | $0.03 | 92799 |
| 227 | $0.04 | 95235 |
| 228 | $0.04 | 97953 |
| 229 | $0.05 | 101271 |
| 230 | $0.03 | 101898 |
| 231 | $0.02 | 102273 |
| 232 | $0.02 | 102596 |
| 233 | $0.02 | 102911 |
| 234 | $0.03 | 103644 |
| 235 | $0.03 | 104859 |
| 236 | $0.03 | 105652 |
| 237 | $0.03 | 106343 |
| 238 | $0.03 | 106995 |
| 239 | $0.03 | 108391 |
| 240 | $0.03 | 109294 |
| 241 | $0.04 | 111029 |
| 242 | $0.03 | 111442 |
| 243 | $0.03 | 112046 |
| 244 | $0.03 | 112496 |
| 245 | $0.03 | 113593 |
| 246 | $0.03 | 114421 |
| 247 | $0.03 | 115126 |
| 248 | $0.03 | 116384 |
| 249 | $0.08 | 123834 |
| 250 | $0.03 | 125041 |
| 251 | $0.04 | 126520 |
| 252 | $0.03 | 127189 |
| 253 | $0.03 | 127773 |
| 254 | $0.03 | 128527 |
| 255 | $0.03 | 129129 |
| 256 | $0.03 | 129996 |
| 257 | $0.03 | 130656 |
| 258 | $0.03 | 131441 |
| 259 | $0.03 | 131951 |
| 260 | $0.03 | 132844 |
| 261 | $0.03 | 133687 |
| 262 | $0.05 | 136148 |
| 263 | $0.03 | 136928 |
| 264 | $0.03 | 137217 |
| 265 | $0.04 | 138582 |
| 266 | $0.04 | 139958 |
| 267 | $0.04 | 141053 |
| 268 | $0.03 | 141562 |
| 269 | $0.04 | 142483 |
| 270 | $0.04 | 143564 |
| 271 | $0.03 | 144052 |
| 272 | $0.03 | 144700 |
| 273 | $0.04 | 145741 |
| 274 | $0.04 | 147317 |
| 275 | $0.04 | 148009 |
| 276 | $0.04 | 148735 |
| 277 | $0.05 | 150777 |
| 278 | $0.04 | 152293 |
| 279 | $0.04 | 153368 |
| 280 | $0.04 | 154260 |
| 281 | $0.04 | 155064 |
| 282 | $0.04 | 156373 |
| 283 | $0.03 | 156744 |
| 284 | $0.04 | 157230 |
| 285 | $0.04 | 157951 |
| 286 | $0.04 | 158569 |
| 287 | $0.04 | 159313 |
| 288 | $0.04 | 159838 |
| 289 | $0.03 | 160158 |
| 290 | $0.04 | 160668 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 1 | 2 | 1482 | 0 | 31085 | 0.09 |
| red | 25 | 11 | 1 | 0 | 929 | 493 | 123 | 242 | 57163 | 3612695 | 649127 | 2.72 |
| green | 25 | 6 | 4 | 0 | 1838 | 478 | 133 | 266 | 46430 | 4012712 | 432317 | 2.39 |
| refactor | 12 | 6 | 0 | 0 | 378 | 113 | 40 | 78 | 9690 | 1033201 | 167555 | 0.62 |
| pin | 5 | 3 | 2 | 0 | 149 | 68 | 20 | 40 | 7137 | 546584 | 80477 | 0.33 |
| cover | 3 | 0 | 0 | 0 | 115 | 48 | 15 | 30 | 5210 | 403971 | 65007 | 0.26 |
| predicate | 2 | 0 | 0 | 0 | 26 | 19 | 7 | 14 | 1711 | 179065 | 24141 | 0.10 |
| structural | 2 | 0 | 0 | 0 | 73 | 23 | 10 | 20 | 2459 | 270627 | 26203 | 0.12 |
| transform | 2 | 2 | 0 | 0 | 54 | 17 | 7 | 14 | 1454 | 158875 | 41929 | 0.14 |
| red-supersede | 1 | 0 | 0 | 0 | 56 | 30 | 9 | 18 | 3812 | 313707 | 23649 | 0.13 |
| exhausted | 2 | 0 | 0 | 0 | 66 | 52 | 9 | 18 | 3827 | 250921 | 32705 | 0.29 |
| diff | 6 | 2 | 1 | 0 | 313 | 113 | 36 | 70 | 12569 | 1041523 | 128076 | 0.73 |
| rebase | 2 | 1 | 0 | 0 | 424 | 22 | 11 | 20 | 2308 | 252277 | 70268 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 40 | 32 | 8 | 0 | 1927 | 482 | 148 | 290 | 48694 | 3836377 | 684336 | 2.58 |
| developer | claude-sonnet-5-5 | 37 | 0 | 0 | 0 | 1871 | 736 | 211 | 418 | 82683 | 6338658 | 854791 | 3.90 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 639 | 270 | 62 | 124 | 23875 | 1901123 | 233412 | 1.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 314 | 0.94 | 0 | 0.00 |
| green | 2417 | 3.17 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 116 | 0.27 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |
| diff | 231 | 0.58 | 82 | 0.14 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh record --step <s> <test-file>` run again for a step whose record already holds a `body:` entry for a case, when that case is committed at HEAD unchanged, keeps that case's `body:` entry with its digest at the current content, instead of writing a file-only record with no case (a git repo in tmp_path: a medium case marked process) ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 91 | 29 | 56 | 8770 | 822960 | 121831 | 0.47 | 495 | unknown | 1/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-earlier <ledger> --step <s>`, for a step `<s>` marked `⟦diff-checked⟧`, rewrites each earlier step's record entry whose case's content changed at the case's current content and exits 0, so that a later step's `tests-frozen.sh check-earlier` exits 0 and names nothing for that case (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 90 | 25 | 50 | 9075 | 727920 | 100755 | 0.42 | 350 | unknown | 0/5 | structural-owed |  |  | full |
| `tick-ledger.sh` ticking a step marked `⟦diff-checked⟧` re-records, as `rerecord-earlier` does, every earlier step's frozen case that step changed, so after the ⟦diff-checked⟧ step's tick a later step's `tests-frozen.sh check-earlier` exits 0 for the edited case, with no extra conductor command (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 27 | 54 | 8372 | 771354 | 98426 | 0.41 | 371 | unknown | 0/5 | structural-owed |  |  | full |
| A frozen case changed by a step not marked `⟦diff-checked⟧` still trips `check-earlier`: `tick-ledger.sh` ticking such a step, and `tests-frozen.sh rerecord-earlier` given such a step (exit 3, nothing to do), leave every earlier record unchanged, and a later step's `check-earlier` exits 1 naming the case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 23 | 46 | 8117 | 641060 | 94790 | 0.38 | 392 | unknown | 0/5 | structural-owed |  |  | full |
| The fresh record the ⟦diff-checked⟧ tick writes is computed by the `tests_frozen` beside the `tick-ledger.sh` that ran (the run's pinned skill snapshot), never by a `tests_frozen` in the working tree: with two copies of the scripts directory whose `tests_frozen` digest a case differently, the tick and `check-earlier` run from the snapshot copy pass for the re-recorded case though the checkout copy would digest it otherwise (a medium case marked process) ⟦criterion 4⟧ | 11 | 3 | 0 | 0 | 0 | 0 | 166 | 51 | 102 | 17946 | 1426290 | 205429 | 0.84 | unknown | unknown | unknown | unknown |  |  | pin |
| `tick-ledger.sh` re-records earlier frozen cases only when the ticked line's kind, as `ledger.KIND_RE` parses it from the line's trailing markers, is `⟦diff-checked⟧`: ticking an ordinary step whose text merely mentions `⟦diff-checked⟧` in its prose leaves every earlier frozen record unchanged, `tests-frozen.sh rerecord-earlier` given that step exits 3, and a later step's `check-earlier` exits 1 naming the edited case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 5⟧ | 21 | 6 | 5 | 0 | 0 | 0 | 399 | 106 | 210 | 40802 | 3090002 | 451517 | 2.14 | 425 | 2/2 | 1/5 | nothing-left |  |  | full |
| `tests-frozen.sh rerecord-earlier` (and so the `⟦diff-checked⟧` tick) re-records only the earlier frozen cases that the step's own diff changed, from the step base (the last commit that changed the ledger, `git log -1 --format=%H -- <ledger>`) to HEAD, reading each case's content at HEAD and never from the working tree: an earlier frozen case edited in a commit before the step base, or edited only in the working tree and left uncommitted, keeps its old record entry, and a later step's `check-earlier` still exits 1 naming it (a git repo in tmp_path: medium cases marked process) ⟦criterion 6⟧ | 19 | 5 | 2 | 0 | 0 | 0 | 351 | 89 | 176 | 36088 | 2569553 | 384649 | 2.04 | 621 | red 1/2, green 3/2 | 1/5 | nothing-left |  |  | full |
| `rerecord_earlier` never rewrites the ticked step's own frozen record: when the `⟦diff-checked⟧` step being ticked has a record of its own holding a case its diff changed, that record file is byte-for-byte unchanged after `tick-ledger.sh` ticks the step, while an earlier step's record of the same case is re-recorded (a git repo in tmp_path: a medium case marked process) ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 4517 | 326109 | 44490 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| After `tick-ledger.sh` ticks a `⟦diff-checked⟧` step that re-records an earlier step's frozen case, committing with `git add .tdd/issue-<n>.md && git commit` leaves `git status --porcelain` empty: every record the tick rewrote is either in that commit or ignored run state, and the tick changes no tracked file besides the ledger; no SKILL.md text is changed (a git repo in tmp_path: a medium case marked process) ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 13 | 26 | 5206 | 407110 | 41223 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests_frozen.rerecord_earlier` and `tests_frozen._check_earlier` read the ledger's steps and their frozen records through one shared reader in `veri/tests_frozen.py`, neither keeping a ledger-reading loop of its own, with no behaviour changed and every suite green ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 8⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 10 | 20 | 3727 | 281537 | 31009 | 0.14 | unknown | n/a | n/a | n/a |  |  | full |
| The documentation names the new behaviour: `tests-frozen.sh`'s header and its `USAGE` line in `veri/tests_frozen.py` name `rerecord-earlier <ledger> --step <step-text>` and its exits; `tick-ledger.sh`'s header states that exit 2 can follow a write of the ledger (a `⟦diff-checked⟧` tick whose re-record failed); and `SCRIPTS.md`'s `tests-frozen.sh` and `tick-ledger.sh` entries describe `rerecord-earlier` and the `⟦diff-checked⟧` tick's re-record ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 8⟧ | 6 | 2 | 1 | 0 | 0 | 0 | 108 | 37 | 70 | 11150 | 1012263 | 167335 | 0.81 | 378 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh record --step <s> <test-file>` run again for a step whose record already holds a `body:` entry for a case, when that case is committed at HEAD unchanged, keeps that case's `body:` entry with its digest at the current content, instead of writing a file-only record with no case (a git repo in tmp_path: a medium case marked process) ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 85 | 0.11 |
| `tests-frozen.sh rerecord-earlier <ledger> --step <s>`, for a step `<s>` marked `⟦diff-checked⟧`, rewrites each earlier step's record entry whose case's content changed at the case's current content and exits 0, so that a later step's `tests-frozen.sh check-earlier` exits 0 and names nothing for that case (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 53 | 0.10 |
| `tick-ledger.sh` ticking a step marked `⟦diff-checked⟧` re-records, as `rerecord-earlier` does, every earlier step's frozen case that step changed, so after the ⟦diff-checked⟧ step's tick a later step's `tests-frozen.sh check-earlier` exits 0 for the edited case, with no extra conductor command (a git repo in tmp_path: a medium case marked process) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 50 | 0.09 |
| A frozen case changed by a step not marked `⟦diff-checked⟧` still trips `check-earlier`: `tick-ledger.sh` ticking such a step, and `tests-frozen.sh rerecord-earlier` given such a step (exit 3, nothing to do), leave every earlier record unchanged, and a later step's `check-earlier` exits 1 naming the case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 48 | 0.09 |
| `tick-ledger.sh` re-records earlier frozen cases only when the ticked line's kind, as `ledger.KIND_RE` parses it from the line's trailing markers, is `⟦diff-checked⟧`: ticking an ordinary step whose text merely mentions `⟦diff-checked⟧` in its prose leaves every earlier frozen record unchanged, `tests-frozen.sh rerecord-earlier` given that step exits 3, and a later step's `check-earlier` exits 1 naming the edited case and its owning step (a git repo in tmp_path: a medium case marked process) ⟦criterion 5⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 78 | 0.12 |
| `tests-frozen.sh rerecord-earlier` (and so the `⟦diff-checked⟧` tick) re-records only the earlier frozen cases that the step's own diff changed, from the step base (the last commit that changed the ledger, `git log -1 --format=%H -- <ledger>`) to HEAD, reading each case's content at HEAD and never from the working tree: an earlier frozen case edited in a commit before the step base, or edited only in the working tree and left uncommitted, keeps its old record entry, and a later step's `check-earlier` still exits 1 naming it (a git repo in tmp_path: medium cases marked process) ⟦criterion 6⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 64 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 12 | 14 | 14 | 30 | 20 | 18 | 13 | 13 | 14 | 15 | 13 | 9 | 9 | 10 | 24 | 10 | 19 | 16 | 13 | 16 | 12 | 10 | 11 | 13 | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 7 | 5 | 11 | 6 | 10 | 16 | 37 | 38 | 0 | 0 | 30 | 40 | 6 | 4 | 0 | 4 | 22 | 21 | 7 | 17 | 34 | 16 | 7 | 6 | 7 | 7 | 6 | 29 | 16 | 24 | 16 | 17 | 7 | 7 | 4 | 7 | 3 | 3 | 7 | 7 | 19 | 7 | 7 |
| fast | 15 | 25 | 17 | 16 | 18 | 14 | 14 | 15 | 15 | 15 | 20 | 14 | 23 | 24 | 33 | 25 | 29 | 55 | 19 | 19 | 20 | 53 | 20 | 20 | 19 | 18 | 17 | 18 | 18 | 19 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 9 | 9 | 8 | 10 | 11 | 11 | 11 | 12 | 8 | 0 | 4 | 3 | 1 | 1 | 4 | 4 | 5 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 195 | 190 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 421 | 832 | 155252 | 12076158 | 1772539 | 8.12 |
