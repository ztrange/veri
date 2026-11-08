### 📊 Metrics — issue 3261

Wall time for the issue: 1413 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 19 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $16.65 over 314 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92835 tokens, largest 185166 tokens
Conductor context: first turn 92838 tokens, largest 198525 tokens
Conductor context: first turn 92849 tokens, largest 178979 tokens
Conductor context: first turn 92884 tokens, largest 182572 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 92835 |
| 2 | $0.08 | 98630 |
| 3 | $0.03 | 99699 |
| 4 | $0.05 | 101645 |
| 5 | $0.03 | 101938 |
| 6 | $0.03 | 102382 |
| 7 | $0.04 | 102776 |
| 8 | $0.03 | 103085 |
| 9 | $0.03 | 103472 |
| 10 | $0.04 | 104126 |
| 11 | $0.04 | 105138 |
| 12 | $0.04 | 106860 |
| 13 | $0.06 | 110042 |
| 14 | $0.05 | 112587 |
| 15 | $0.07 | 117586 |
| 16 | $0.04 | 118247 |
| 17 | $0.04 | 118800 |
| 18 | $0.05 | 120847 |
| 19 | $0.06 | 124060 |
| 20 | $0.04 | 125140 |
| 21 | $0.05 | 127036 |
| 22 | $0.04 | 127962 |
| 23 | $0.05 | 129472 |
| 24 | $0.04 | 130097 |
| 25 | $0.04 | 130386 |
| 26 | $0.04 | 130978 |
| 27 | $0.04 | 131625 |
| 28 | $0.04 | 132704 |
| 29 | $0.04 | 133366 |
| 30 | $0.05 | 134610 |
| 31 | $0.04 | 135037 |
| 32 | $0.04 | 136179 |
| 33 | $0.05 | 136927 |
| 34 | $0.04 | 137608 |
| 35 | $0.04 | 137953 |
| 36 | $0.04 | 138715 |
| 37 | $0.04 | 139327 |
| 38 | $0.05 | 139951 |
| 39 | $0.04 | 140394 |
| 40 | $0.04 | 140780 |
| 41 | $0.04 | 141447 |
| 42 | $0.04 | 141852 |
| 43 | $0.04 | 142102 |
| 44 | $0.05 | 143116 |
| 45 | $0.05 | 144542 |
| 46 | $0.04 | 145234 |
| 47 | $0.05 | 146752 |
| 48 | $0.04 | 147102 |
| 49 | $0.05 | 147802 |
| 50 | $0.05 | 148875 |
| 51 | $0.10 | 157149 |
| 52 | $0.05 | 158771 |
| 53 | $0.05 | 159369 |
| 54 | $0.05 | 160163 |
| 55 | $0.04 | 160707 |
| 56 | $0.05 | 161288 |
| 57 | $0.05 | 162056 |
| 58 | $0.04 | 162719 |
| 59 | $0.05 | 163533 |
| 60 | $0.05 | 164437 |
| 61 | $0.05 | 165031 |
| 62 | $0.05 | 165851 |
| 63 | $0.05 | 166614 |
| 64 | $0.05 | 168135 |
| 65 | $0.05 | 168857 |
| 66 | $0.05 | 169372 |
| 67 | $0.05 | 169959 |
| 68 | $0.04 | 170296 |
| 69 | $0.05 | 170765 |
| 70 | $0.05 | 171680 |
| 71 | $0.05 | 172495 |
| 72 | $0.05 | 172772 |
| 73 | $0.05 | 173324 |
| 74 | $0.05 | 174572 |
| 75 | $0.05 | 175751 |
| 76 | $0.05 | 176132 |
| 77 | $0.05 | 177110 |
| 78 | $0.05 | 177582 |
| 79 | $0.05 | 178445 |
| 80 | $0.09 | 183025 |
| 81 | $0.05 | 183981 |
| 82 | $0.05 | 184764 |
| 83 | $0.05 | 184909 |
| 84 | $0.05 | 185166 |
| 85 | $0.61 | 92838 |
| 86 | $0.08 | 98635 |
| 87 | $0.04 | 99694 |
| 88 | $0.04 | 101235 |
| 89 | $0.06 | 105293 |
| 90 | $0.04 | 105806 |
| 91 | $0.03 | 106268 |
| 92 | $0.04 | 106595 |
| 93 | $0.03 | 107030 |
| 94 | $0.04 | 107375 |
| 95 | $0.04 | 108228 |
| 96 | $0.06 | 112547 |
| 97 | $0.05 | 113524 |
| 98 | $0.03 | 114093 |
| 99 | $0.04 | 114667 |
| 100 | $0.04 | 114888 |
| 101 | $0.04 | 115657 |
| 102 | $0.04 | 116951 |
| 103 | $0.04 | 117969 |
| 104 | $0.05 | 119149 |
| 105 | $0.03 | 119476 |
| 106 | $0.04 | 120195 |
| 107 | $0.04 | 120935 |
| 108 | $0.04 | 121549 |
| 109 | $0.04 | 122200 |
| 110 | $0.05 | 123547 |
| 111 | $0.04 | 124354 |
| 112 | $0.11 | 132872 |
| 113 | $0.04 | 134402 |
| 114 | $0.05 | 135172 |
| 115 | $0.04 | 135585 |
| 116 | $0.04 | 136187 |
| 117 | $0.05 | 136949 |
| 118 | $0.04 | 137326 |
| 119 | $0.04 | 138002 |
| 120 | $0.04 | 138508 |
| 121 | $0.05 | 139091 |
| 122 | $0.04 | 139866 |
| 123 | $0.05 | 141917 |
| 124 | $0.05 | 142388 |
| 125 | $0.04 | 143158 |
| 126 | $0.05 | 143612 |
| 127 | $0.04 | 143916 |
| 128 | $0.04 | 144932 |
| 129 | $0.05 | 145362 |
| 130 | $0.06 | 148679 |
| 131 | $0.05 | 149342 |
| 132 | $0.05 | 150031 |
| 133 | $0.04 | 150442 |
| 134 | $0.04 | 150735 |
| 135 | $0.05 | 151485 |
| 136 | $0.04 | 151898 |
| 137 | $0.05 | 152263 |
| 138 | $0.05 | 153156 |
| 139 | $0.04 | 153682 |
| 140 | $0.05 | 154616 |
| 141 | $0.05 | 155864 |
| 142 | $0.05 | 156197 |
| 143 | $0.04 | 156905 |
| 144 | $0.05 | 157544 |
| 145 | $0.05 | 158197 |
| 146 | $0.06 | 160892 |
| 147 | $0.05 | 161251 |
| 148 | $0.05 | 162493 |
| 149 | $0.05 | 162830 |
| 150 | $0.04 | 163576 |
| 151 | $0.06 | 164615 |
| 152 | $0.05 | 166127 |
| 153 | $0.06 | 168100 |
| 154 | $0.05 | 168962 |
| 155 | $0.06 | 170499 |
| 156 | $0.07 | 173999 |
| 157 | $0.05 | 174570 |
| 158 | $0.06 | 175870 |
| 159 | $0.05 | 176135 |
| 160 | $0.04 | 176437 |
| 161 | $0.07 | 178560 |
| 162 | $0.06 | 180169 |
| 163 | $0.05 | 180644 |
| 164 | $0.05 | 181258 |
| 165 | $0.05 | 181607 |
| 166 | $0.05 | 182045 |
| 167 | $0.05 | 182368 |
| 168 | $0.05 | 182606 |
| 169 | $0.05 | 184003 |
| 170 | $0.06 | 184512 |
| 171 | $0.06 | 186705 |
| 172 | $0.07 | 189203 |
| 173 | $0.05 | 189837 |
| 174 | $0.07 | 191927 |
| 175 | $0.08 | 196693 |
| 176 | $0.06 | 197798 |
| 177 | $0.06 | 198525 |
| 178 | $0.61 | 92849 |
| 179 | $0.08 | 98605 |
| 180 | $0.04 | 99628 |
| 181 | $0.04 | 101459 |
| 182 | $0.08 | 107548 |
| 183 | $0.07 | 111791 |
| 184 | $0.04 | 112164 |
| 185 | $0.03 | 112559 |
| 186 | $0.04 | 112860 |
| 187 | $0.03 | 113208 |
| 188 | $0.04 | 113824 |
| 189 | $0.04 | 114146 |
| 190 | $0.04 | 114822 |
| 191 | $0.04 | 115482 |
| 192 | $0.04 | 116172 |
| 193 | $0.03 | 116656 |
| 194 | $0.04 | 116845 |
| 195 | $0.04 | 117592 |
| 196 | $0.05 | 118991 |
| 197 | $0.03 | 119504 |
| 198 | $0.04 | 119831 |
| 199 | $0.04 | 120498 |
| 200 | $0.05 | 122259 |
| 201 | $0.04 | 122996 |
| 202 | $0.04 | 123721 |
| 203 | $0.05 | 124908 |
| 204 | $0.04 | 125498 |
| 205 | $0.04 | 126332 |
| 206 | $0.04 | 127155 |
| 207 | $0.05 | 128006 |
| 208 | $0.07 | 131838 |
| 209 | $0.05 | 133575 |
| 210 | $0.05 | 135654 |
| 211 | $0.05 | 136642 |
| 212 | $0.10 | 144826 |
| 213 | $0.05 | 145669 |
| 214 | $0.05 | 147077 |
| 215 | $0.05 | 148033 |
| 216 | $0.04 | 148920 |
| 217 | $0.05 | 149492 |
| 218 | $0.05 | 150983 |
| 219 | $0.05 | 151781 |
| 220 | $0.04 | 152313 |
| 221 | $0.06 | 153808 |
| 222 | $0.05 | 154540 |
| 223 | $0.04 | 155312 |
| 224 | $0.05 | 156086 |
| 225 | $0.05 | 156760 |
| 226 | $0.05 | 157886 |
| 227 | $0.05 | 158949 |
| 228 | $0.05 | 159276 |
| 229 | $0.05 | 160158 |
| 230 | $0.05 | 161548 |
| 231 | $0.05 | 162302 |
| 232 | $0.06 | 164159 |
| 233 | $0.05 | 164811 |
| 234 | $0.04 | 165375 |
| 235 | $0.06 | 167356 |
| 236 | $0.05 | 167815 |
| 237 | $0.05 | 168359 |
| 238 | $0.06 | 169714 |
| 239 | $0.05 | 170760 |
| 240 | $0.09 | 176021 |
| 241 | $0.06 | 178053 |
| 242 | $0.05 | 178979 |
| 243 | $0.60 | 92884 |
| 244 | $0.06 | 98681 |
| 245 | $0.03 | 99740 |
| 246 | $0.02 | 100327 |
| 247 | $0.05 | 104154 |
| 248 | $0.05 | 108421 |
| 249 | $0.03 | 108887 |
| 250 | $0.03 | 109364 |
| 251 | $0.02 | 109671 |
| 252 | $0.02 | 109917 |
| 253 | $0.02 | 110207 |
| 254 | $0.03 | 111170 |
| 255 | $0.03 | 112182 |
| 256 | $0.03 | 112736 |
| 257 | $0.03 | 113472 |
| 258 | $0.03 | 114140 |
| 259 | $0.03 | 115141 |
| 260 | $0.02 | 115325 |
| 261 | $0.03 | 115795 |
| 262 | $0.03 | 116471 |
| 263 | $0.04 | 118100 |
| 264 | $0.03 | 118746 |
| 265 | $0.03 | 119664 |
| 266 | $0.03 | 120184 |
| 267 | $0.03 | 121108 |
| 268 | $0.03 | 121650 |
| 269 | $0.03 | 121971 |
| 270 | $0.03 | 122623 |
| 271 | $0.03 | 123546 |
| 272 | $0.03 | 124244 |
| 273 | $0.03 | 124958 |
| 274 | $0.09 | 133279 |
| 275 | $0.03 | 133633 |
| 276 | $0.03 | 133962 |
| 277 | $0.03 | 134729 |
| 278 | $0.03 | 135209 |
| 279 | $0.04 | 136203 |
| 280 | $0.03 | 136686 |
| 281 | $0.03 | 137524 |
| 282 | $0.03 | 138121 |
| 283 | $0.05 | 141481 |
| 284 | $0.04 | 142357 |
| 285 | $0.03 | 142872 |
| 286 | $0.04 | 143832 |
| 287 | $0.03 | 144493 |
| 288 | $0.04 | 145340 |
| 289 | $0.04 | 146190 |
| 290 | $0.03 | 146536 |
| 291 | $0.05 | 148730 |
| 292 | $0.04 | 149794 |
| 293 | $0.04 | 150523 |
| 294 | $0.04 | 151250 |
| 295 | $0.04 | 152517 |
| 296 | $0.12 | 163281 |
| 297 | $0.04 | 164197 |
| 298 | $0.04 | 164750 |
| 299 | $0.05 | 166355 |
| 300 | $0.04 | 167340 |
| 301 | $0.04 | 167996 |
| 302 | $0.04 | 168877 |
| 303 | $0.04 | 170051 |
| 304 | $0.04 | 171004 |
| 305 | $0.04 | 172138 |
| 306 | $0.04 | 172950 |
| 307 | $0.04 | 173893 |
| 308 | $0.04 | 174234 |
| 309 | $0.05 | 175697 |
| 310 | $0.04 | 176150 |
| 311 | $0.04 | 176703 |
| 312 | $0.04 | 177360 |
| 313 | $0.08 | 182572 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 5 | 4 | 1 | 0 | 71 | 60 | 7 | 14 | 7699 | 45780 | 94629 | 0.32 |
| red | 41 | 16 | 4 | 0 | 1543 | 885 | 227 | 448 | 96236 | 4117622 | 763769 | 4.18 |
| green | 51 | 10 | 11 | 0 | 3290 | 821 | 269 | 526 | 86776 | 4515622 | 778651 | 3.99 |
| refactor | 16 | 5 | 0 | 0 | 278 | 111 | 50 | 100 | 11288 | 682335 | 220688 | 0.73 |
| exhausted | 3 | 0 | 0 | 0 | 168 | 66 | 13 | 26 | 4647 | 197157 | 44061 | 0.35 |
| red-missing | 5 | 0 | 0 | 0 | 149 | 116 | 26 | 52 | 15981 | 469540 | 91175 | 0.43 |
| pin | 5 | 3 | 2 | 0 | 126 | 89 | 26 | 52 | 9789 | 432973 | 83202 | 0.35 |
| red-supersede | 1 | 0 | 0 | 0 | 34 | 31 | 5 | 10 | 3880 | 225078 | 55482 | 0.20 |
| diff | 3 | 1 | 1 | 0 | 111 | 35 | 13 | 26 | 3741 | 251626 | 40822 | 0.26 |
| red-contradicted | 1 | 0 | 0 | 0 | 38 | 28 | 6 | 12 | 3134 | 122456 | 22982 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 58 | 39 | 19 | 0 | 3173 | 727 | 227 | 448 | 79282 | 3454785 | 769095 | 3.06 |
| developer | claude-sonnet-5-5 | 42 | 0 | 0 | 0 | 1229 | 705 | 213 | 420 | 84247 | 3837613 | 805550 | 3.54 |
| developer | claude-opus-5-5 | 31 | 0 | 0 | 0 | 1406 | 810 | 202 | 398 | 79642 | 3767791 | 620816 | 4.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 310 | 0.73 | 545 | 1.62 |
| green | 4938 | 5.35 | 366 | 0.79 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 101 | 0.20 |
| red-missing | 0 | 0.00 | 31 | 0.08 |
| pin | 20 | 0.07 | 28 | 0.08 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| diff | 111 | 0.26 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 38 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `report.sh` run with no argument prints its usage line on stderr and exits 2; the step adds `report.sh` (a `/bin/sh` shim over `veri/prd_report.py`) and its declared caller (a `report` recipe in the `Makefile` running `report.sh --report`, so `unreachable.sh` reaches it; `SCRIPTS.md` is a graded unit and is not edited) | 5 | 2 | 0 | 0 | 0 | 0 | 64 | 24 | 46 | 7566 | 371814 | 81831 | 0.32 | 341 | unknown | 0/5 | nothing-left |  |  | full |
| `report.sh --report` with a snapshot `.tdd/report-cache.json` present states the snapshot's age on its first line ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 60 | 22 | 44 | 6563 | 352576 | 74711 | 0.29 | 191 | unknown | 0/5 | nothing-left |  |  | full |
| `report.sh --report` with no `.tdd/report-cache.json` says there is no snapshot and exits 2 ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 88 | 32 | 64 | 8930 | 503839 | 107004 | 0.49 | 294 | 1/2 | 1/5 | nothing-left |  |  | full |
| `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 88 | 28 | 56 | 9080 | 434844 | 98462 | 0.47 | 355 | 1/2 | 0/5 | structural-owed |  |  | full |
| Each PRD block's solved line counts the PRD's closed children (cached issues whose title starts with its `PRD <nnn>`, plus the issues in its `links`, minus the PRD itself and links to other PRDs) and how many of them closed in the last 7 days ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 116 | 39 | 76 | 13834 | 629818 | 119035 | 0.56 | 473 | 1/2 | 1/5 | nothing-left |  |  | full |
| Each PRD block's left line counts as solvable now the open children that `VERI_LABEL=<their opt-in label> solvable-issues.sh` lists ⟦criterion 1⟧ | 6 | 1 | 0 | 0 | 0 | 0 | 138 | 33 | 62 | 12493 | 544002 | 104983 | 0.63 | unknown | 2/2 | unknown | unknown |  |  | full |
| Each PRD block's left line counts as solvable now the open children that `VERI_LABEL=<their opt-in label> solvable-issues.sh` lists; the red case's fixture keeps a second open PRD (#99 "PRD 015: other prd child") so blocks are shown not to bleed into each other, and it asserts the `left` line inside the PRD 014 block only, never the count of `left` lines in the whole report ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 138 | 45 | 88 | 14740 | 793464 | 137634 | 0.64 | 566 | 1/2 | 1/5 | nothing-structural |  |  | full |
| Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧ | 16 | 5 | 3 | 0 | 0 | 0 | 203 | 71 | 142 | 22608 | 1174427 | 233528 | 1.00 | 932 | 1/2 | 1/5 | structural-owed |  |  | already-satisfied |
| Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧ | 13 | 4 | 2 | 0 | 0 | 0 | 212 | 68 | 134 | 24043 | 1376634 | 243346 | 1.18 | 673 | red 1/2, diff 1/2 | 0/5 | nothing-left |  |  | full |
| Each PRD block's ETA is a range: its left count ÷ the rate of the lanes holding its open children, the rate per lane taken from the cache's `lane` field over the issues closed in the last 7 days (issues per day, fastest and slowest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane ⟦criterion 1⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 269 | 55 | 110 | 30360 | 1054359 | 186129 | 1.19 | unknown | 2/2 | unknown | unknown |  |  | full |
| A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧ | 21 | 4 | 4 | 0 | 0 | 0 | 391 | 110 | 216 | 41562 | 1850592 | 366282 | 1.98 | 3267 | red 1/2, green 3/2 | 0/5 | nothing-left |  |  | full |
| A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's lower bound as its left count ÷ the fastest rate, the rate per lane taken from the cache's `lane` field over those closed issues (issues per day at the fastest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 177 | 50 | 98 | 20257 | 833200 | 178683 | 0.81 | 769 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's upper bound as its left count ÷ the slowest rate (issues per day at the slowest quartile of `wallSeconds`), after the lower bound as a range; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧ | 10 | 2 | 1 | 0 | 0 | 0 | 238 | 58 | 116 | 23436 | 1094840 | 169204 | 1.06 | unknown | red 1/2, green 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `report.sh` run with no argument prints its usage line on stderr and exits 2; the step adds `report.sh` (a `/bin/sh` shim over `veri/prd_report.py`) and its declared caller (a `report` recipe in the `Makefile` running `report.sh --report`, so `unreachable.sh` reaches it; `SCRIPTS.md` is a graded unit and is not edited) | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |
| `report.sh --report` with a snapshot `.tdd/report-cache.json` present states the snapshot's age on its first line ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.03 |
| `report.sh --report` with no `.tdd/report-cache.json` says there is no snapshot and exits 2 ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 39 | 0.09 |
| `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 5 | 0.04 |
| Each PRD block's solved line counts the PRD's closed children (cached issues whose title starts with its `PRD <nnn>`, plus the issues in its `links`, minus the PRD itself and links to other PRDs) and how many of them closed in the last 7 days ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 57 | 0.10 |
| Each PRD block's left line counts as solvable now the open children that `VERI_LABEL=<their opt-in label> solvable-issues.sh` lists; the red case's fixture keeps a second open PRD (#99 "PRD 015: other prd child") so blocks are shown not to bleed into each other, and it asserts the `left` line inside the PRD 014 block only, never the count of `left` lines in the whole report ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 48 | 0.10 |
| Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 46 | 0.10 |
| Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 46 | 0.09 |
| A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 20 | 0.12 |
| A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's lower bound as its left count ÷ the fastest rate, the rate per lane taken from the cache's `lane` field over those closed issues (issues per day at the fastest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `report.sh` run with no argument prints its usage line on stderr and exits 2; the step adds `report.sh` (a `/bin/sh` shim over `veri/prd_report.py`) and its declared caller (a `report` recipe in the `Makefile` running `report.sh --report`, so `unreachable.sh` reaches it; `SCRIPTS.md` is a graded unit and is not edited) | 1 | 0 | 1 | nothing-left 1 |
| `report.sh --report` with a snapshot `.tdd/report-cache.json` present states the snapshot's age on its first line ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| `report.sh --report` with no `.tdd/report-cache.json` says there is no snapshot and exits 2 ⟦criterion 2⟧ | 1 | 1 | 0 | nothing-left 1 |
| `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧ | 1 | 0 | 1 | structural-owed 1 |
| Each PRD block's solved line counts the PRD's closed children (cached issues whose title starts with its `PRD <nnn>`, plus the issues in its `links`, minus the PRD itself and links to other PRDs) and how many of them closed in the last 7 days ⟦criterion 1⟧ | 1 | 1 | 0 | nothing-left 1 |
| Each PRD block's left line counts as solvable now the open children that `VERI_LABEL=<their opt-in label> solvable-issues.sh` lists; the red case's fixture keeps a second open PRD (#99 "PRD 015: other prd child") so blocks are shown not to bleed into each other, and it asserts the `left` line inside the PRD 014 block only, never the count of `left` lines in the whole report ⟦criterion 1⟧ | 1 | 1 | 0 | nothing-structural 1 |
| Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧ | 1 | 1 | 0 | structural-owed 1 |
| Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's lower bound as its left count ÷ the fastest rate, the rate per lane taken from the cache's `lane` field over those closed issues (issues per day at the fastest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 10 | 4 | 6 | nothing-left 7, nothing-structural 1, structural-owed 2 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 2 | 2 | 3 | 1 | 1 | 0 | 1 | 1 | 0 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 3 | 1 | 1 | 0 | 2 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 2 | 1 | 3 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 |
| fast | 31 | 25 | 19 | 19 | 26 | 19 | 19 | 20 | 28 | 0 | 19 | 19 | 19 | 20 | 19 | 30 | 28 | 29 | 20 | 20 | 21 | 24 | 31 | 20 | 19 | 20 | 19 | 20 | 22 | 21 | 25 | 21 | 20 | 21 | 21 | 22 | 20 | 23 | 21 | 20 | 22 | 20 | 21 | 22 | 20 | 22 | 21 | 21 | 20 | 20 | 33 | 34 | 22 | 20 | 26 | 21 | 25 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 642 | 1266 | 243171 | 11060189 | 2195461 | 27.57 (estimate) |
