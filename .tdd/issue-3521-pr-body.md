Closes #3521. The ledger `.tdd/issue-3521.md` is committed. Every step was blind-verified, either as an R→G→R cycle or, for a test-only step, as a ⟦diff-checked⟧ diff.

- **Criterion 1: status.py only counts its own refresh.** `refresh_running()` in `skills/tdd/scripts/veri/status.py` used to treat any `report-cache.sh refresh` on the machine as its own. It now checks each `pgrep` hit with `ps` and counts only a refresh whose script path is exactly its own sibling `scripts/report-cache.sh` (resolved path, full-path match). The process cases in `test_status_refresh_scope_process.py` start an unrelated refresh themselves and check that the report still launches its own. One unrelated refresh lives at `<tmp>/other/scripts/report-cache.sh`, so a match on the directory's name alone goes red. The unit case's fake `ps` listing (`test_status_report_last_written.py`) now shows the script's own sibling path.
  - A `⟦suite-repair⟧` step fixed the full-suite red on the rebased tip: status.py now locates itself by `realpath` (#3501's audit), and the scope case copies veri.
  - The planned case "own sibling refresh alive → no second refresh" was **retired as unpinnable**. verify-pin found it also passes on the old unscoped `pgrep`, so it pins nothing the full-path cases don't already pin.
- **Criterion 2: EOF from the report closing stdout** (⟦diff-checked⟧). test_2750 reads stdout until EOF within a bound of its own, not `communicate(timeout=10)`.
- **Criterion 3: separate assertions** (⟦diff-checked⟧). "No EOF" and "stub never started" each fail with their own message.
- **Criterion 4: waits bounded below VERI_PYTEST_TIMEOUT** (⟦diff-checked⟧). 25 s at most in total.

The full suite (`make test`) was green on the branch before it was readied. CI is green.

## Review notes
- The EOF bound is 10 s, sized to fit the 30 s budget. The verdict now comes from EOF rather than from a `communicate` timeout, but a report that takes over 10 s to start under very heavy load still fails.

### 📊 Metrics — issue 3521

Wall time for the issue: 621 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3530.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $18.73 over 349 turns, in 6 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 78378 tokens, largest 222831 tokens
Conductor context: first turn 78379 tokens, largest 145303 tokens
Conductor context: first turn 78381 tokens, largest 108353 tokens
Conductor context: first turn 78379 tokens, largest 160249 tokens
Conductor context: first turn 78407 tokens, largest 152541 tokens
Conductor context: first turn 78404 tokens, largest 149118 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 78378 |
| 2 | $0.07 | 84390 |
| 3 | $0.04 | 86088 |
| 4 | $0.04 | 87683 |
| 5 | $0.03 | 87883 |
| 6 | $0.03 | 88572 |
| 7 | $0.03 | 88975 |
| 8 | $0.03 | 89306 |
| 9 | $0.03 | 89754 |
| 10 | $0.03 | 90093 |
| 11 | $0.03 | 90458 |
| 12 | $0.03 | 91076 |
| 13 | $0.03 | 91380 |
| 14 | $0.10 | 99816 |
| 15 | $0.05 | 102715 |
| 16 | $0.04 | 103838 |
| 17 | $0.04 | 104953 |
| 18 | $0.03 | 105385 |
| 19 | $0.04 | 106073 |
| 20 | $0.04 | 106647 |
| 21 | $0.03 | 107047 |
| 22 | $0.03 | 107565 |
| 23 | $0.14 | 120935 |
| 24 | $0.05 | 122126 |
| 25 | $0.04 | 122952 |
| 26 | $0.11 | 132819 |
| 27 | $0.05 | 134493 |
| 28 | $0.04 | 135295 |
| 29 | $0.04 | 136073 |
| 30 | $0.05 | 137568 |
| 31 | $0.05 | 138716 |
| 32 | $0.04 | 139128 |
| 33 | $0.05 | 140612 |
| 34 | $0.04 | 141545 |
| 35 | $0.05 | 143060 |
| 36 | $0.06 | 145428 |
| 37 | $0.04 | 147116 |
| 38 | $0.04 | 147540 |
| 39 | $0.06 | 150022 |
| 40 | $0.05 | 150648 |
| 41 | $0.04 | 151492 |
| 42 | $0.05 | 152248 |
| 43 | $0.04 | 152888 |
| 44 | $0.04 | 153654 |
| 45 | $0.05 | 154096 |
| 46 | $0.05 | 155055 |
| 47 | $0.05 | 156489 |
| 48 | $0.04 | 156811 |
| 49 | $0.05 | 157427 |
| 50 | $0.04 | 158202 |
| 51 | $0.05 | 158643 |
| 52 | $0.05 | 159239 |
| 53 | $0.04 | 159578 |
| 54 | $0.04 | 160072 |
| 55 | $0.05 | 160874 |
| 56 | $0.05 | 161065 |
| 57 | $0.04 | 161709 |
| 58 | $0.07 | 164556 |
| 59 | $0.05 | 165359 |
| 60 | $0.04 | 165960 |
| 61 | $0.05 | 166410 |
| 62 | $0.06 | 168166 |
| 63 | $0.04 | 168218 |
| 64 | $0.05 | 168656 |
| 65 | $0.04 | 169095 |
| 66 | $0.05 | 169777 |
| 67 | $0.05 | 170062 |
| 68 | $0.05 | 170822 |
| 69 | $0.05 | 171626 |
| 70 | $0.04 | 171815 |
| 71 | $0.05 | 172004 |
| 72 | $0.05 | 172493 |
| 73 | $0.05 | 173151 |
| 74 | $0.04 | 173336 |
| 75 | $0.05 | 174156 |
| 76 | $0.05 | 174869 |
| 77 | $0.05 | 175058 |
| 78 | $0.04 | 175247 |
| 79 | $0.05 | 175557 |
| 80 | $0.05 | 176320 |
| 81 | $0.05 | 177136 |
| 82 | $0.05 | 177325 |
| 83 | $0.05 | 177618 |
| 84 | $0.05 | 178335 |
| 85 | $0.05 | 179086 |
| 86 | $0.05 | 179763 |
| 87 | $0.06 | 182022 |
| 88 | $0.06 | 182708 |
| 89 | $0.05 | 183917 |
| 90 | $0.05 | 184369 |
| 91 | $0.05 | 184799 |
| 92 | $0.05 | 185018 |
| 93 | $0.05 | 185233 |
| 94 | $0.05 | 185507 |
| 95 | $0.05 | 186575 |
| 96 | $0.07 | 189653 |
| 97 | $0.06 | 190997 |
| 98 | $0.06 | 192128 |
| 99 | $0.05 | 192315 |
| 100 | $0.05 | 192648 |
| 101 | $0.05 | 193107 |
| 102 | $0.05 | 193295 |
| 103 | $0.05 | 193483 |
| 104 | $0.05 | 193671 |
| 105 | $0.05 | 193968 |
| 106 | $0.05 | 194431 |
| 107 | $0.06 | 195367 |
| 108 | $0.05 | 196067 |
| 109 | $0.05 | 196254 |
| 110 | $0.06 | 196904 |
| 111 | $0.05 | 197491 |
| 112 | $0.05 | 197679 |
| 113 | $0.05 | 198017 |
| 114 | $0.05 | 198505 |
| 115 | $0.06 | 199234 |
| 116 | $0.06 | 200168 |
| 117 | $0.17 | 215959 |
| 118 | $0.06 | 216162 |
| 119 | $0.05 | 216381 |
| 120 | $0.06 | 216751 |
| 121 | $0.05 | 216986 |
| 122 | $0.06 | 217248 |
| 123 | $0.05 | 217772 |
| 124 | $0.06 | 217988 |
| 125 | $0.05 | 218346 |
| 126 | $0.06 | 218636 |
| 127 | $0.06 | 218951 |
| 128 | $0.05 | 219350 |
| 129 | $0.06 | 219768 |
| 130 | $0.05 | 220045 |
| 131 | $0.06 | 221056 |
| 132 | $0.06 | 222443 |
| 133 | $0.06 | 222831 |
| 134 | $0.49 | 78379 |
| 135 | $0.08 | 84390 |
| 136 | $0.04 | 86120 |
| 137 | $0.04 | 88097 |
| 138 | $0.06 | 92486 |
| 139 | $0.03 | 93105 |
| 140 | $0.03 | 93599 |
| 141 | $0.03 | 93922 |
| 142 | $0.03 | 94438 |
| 143 | $0.05 | 97005 |
| 144 | $0.08 | 103488 |
| 145 | $0.05 | 105550 |
| 146 | $0.03 | 106046 |
| 147 | $0.04 | 107083 |
| 148 | $0.04 | 107894 |
| 149 | $0.03 | 108687 |
| 150 | $0.04 | 109346 |
| 151 | $0.03 | 109795 |
| 152 | $0.04 | 110520 |
| 153 | $0.04 | 111140 |
| 154 | $0.04 | 112850 |
| 155 | $0.04 | 113256 |
| 156 | $0.03 | 113686 |
| 157 | $0.04 | 114208 |
| 158 | $0.03 | 114611 |
| 159 | $0.04 | 115244 |
| 160 | $0.04 | 116623 |
| 161 | $0.04 | 117446 |
| 162 | $0.05 | 120290 |
| 163 | $0.04 | 121150 |
| 164 | $0.11 | 130216 |
| 165 | $0.04 | 130994 |
| 166 | $0.04 | 131752 |
| 167 | $0.05 | 133596 |
| 168 | $0.04 | 134445 |
| 169 | $0.05 | 135946 |
| 170 | $0.04 | 136604 |
| 171 | $0.05 | 137660 |
| 172 | $0.04 | 138663 |
| 173 | $0.04 | 139421 |
| 174 | $0.04 | 139899 |
| 175 | $0.04 | 140415 |
| 176 | $0.05 | 140980 |
| 177 | $0.03 | 141340 |
| 178 | $0.04 | 141676 |
| 179 | $0.06 | 144129 |
| 180 | $0.04 | 144682 |
| 181 | $0.05 | 145303 |
| 182 | $0.49 | 78381 |
| 183 | $0.08 | 84396 |
| 184 | $0.04 | 86062 |
| 185 | $0.04 | 87905 |
| 186 | $0.04 | 90466 |
| 187 | $0.06 | 94810 |
| 188 | $0.04 | 95408 |
| 189 | $0.03 | 96236 |
| 190 | $0.04 | 98289 |
| 191 | $0.04 | 99148 |
| 192 | $0.03 | 99621 |
| 193 | $0.07 | 104393 |
| 194 | $0.03 | 105111 |
| 195 | $0.03 | 105460 |
| 196 | $0.05 | 106912 |
| 197 | $0.04 | 108353 |
| 198 | $0.50 | 78379 |
| 199 | $0.07 | 84393 |
| 200 | $0.04 | 86085 |
| 201 | $0.04 | 87635 |
| 202 | $0.06 | 90748 |
| 203 | $0.03 | 91708 |
| 204 | $0.06 | 95262 |
| 205 | $0.05 | 97620 |
| 206 | $0.04 | 98190 |
| 207 | $0.03 | 98609 |
| 208 | $0.05 | 100912 |
| 209 | $0.03 | 101541 |
| 210 | $0.04 | 101873 |
| 211 | $0.04 | 102581 |
| 212 | $0.03 | 102939 |
| 213 | $0.04 | 103697 |
| 214 | $0.06 | 108120 |
| 215 | $0.04 | 109077 |
| 216 | $0.04 | 109675 |
| 217 | $0.04 | 110300 |
| 218 | $0.04 | 111495 |
| 219 | $0.04 | 112137 |
| 220 | $0.04 | 112449 |
| 221 | $0.04 | 113001 |
| 222 | $0.04 | 113867 |
| 223 | $0.08 | 120770 |
| 224 | $0.05 | 121776 |
| 225 | $0.04 | 122636 |
| 226 | $0.04 | 122998 |
| 227 | $0.04 | 123991 |
| 228 | $0.04 | 124452 |
| 229 | $0.04 | 125292 |
| 230 | $0.05 | 126182 |
| 231 | $0.04 | 126888 |
| 232 | $0.11 | 136384 |
| 233 | $0.05 | 137360 |
| 234 | $0.05 | 138695 |
| 235 | $0.04 | 139514 |
| 236 | $0.05 | 140604 |
| 237 | $0.05 | 141740 |
| 238 | $0.04 | 142436 |
| 239 | $0.05 | 143013 |
| 240 | $0.04 | 143327 |
| 241 | $0.04 | 143861 |
| 242 | $0.05 | 144992 |
| 243 | $0.05 | 146383 |
| 244 | $0.05 | 147914 |
| 245 | $0.06 | 150271 |
| 246 | $0.06 | 151503 |
| 247 | $0.09 | 157698 |
| 248 | $0.04 | 158507 |
| 249 | $0.06 | 160249 |
| 250 | $0.50 | 78407 |
| 251 | $0.07 | 84472 |
| 252 | $0.04 | 86136 |
| 253 | $0.03 | 86620 |
| 254 | $0.05 | 89435 |
| 255 | $0.03 | 90015 |
| 256 | $0.04 | 90793 |
| 257 | $0.03 | 91268 |
| 258 | $0.03 | 91594 |
| 259 | $0.03 | 92207 |
| 260 | $0.04 | 92820 |
| 261 | $0.03 | 93282 |
| 262 | $0.03 | 93892 |
| 263 | $0.07 | 98219 |
| 264 | $0.04 | 100065 |
| 265 | $0.04 | 101584 |
| 266 | $0.04 | 102400 |
| 267 | $0.04 | 102993 |
| 268 | $0.04 | 104400 |
| 269 | $0.03 | 104948 |
| 270 | $0.04 | 105460 |
| 271 | $0.05 | 107788 |
| 272 | $0.04 | 108565 |
| 273 | $0.10 | 117633 |
| 274 | $0.04 | 118263 |
| 275 | $0.04 | 118511 |
| 276 | $0.03 | 119129 |
| 277 | $0.06 | 121873 |
| 278 | $0.04 | 123166 |
| 279 | $0.05 | 124494 |
| 280 | $0.04 | 125376 |
| 281 | $0.04 | 125738 |
| 282 | $0.04 | 126451 |
| 283 | $0.04 | 127114 |
| 284 | $0.05 | 128176 |
| 285 | $0.11 | 137413 |
| 286 | $0.04 | 138526 |
| 287 | $0.04 | 139015 |
| 288 | $0.05 | 139885 |
| 289 | $0.04 | 140810 |
| 290 | $0.05 | 141776 |
| 291 | $0.04 | 142190 |
| 292 | $0.05 | 143149 |
| 293 | $0.04 | 143443 |
| 294 | $0.04 | 144226 |
| 295 | $0.05 | 144688 |
| 296 | $0.04 | 145727 |
| 297 | $0.05 | 146702 |
| 298 | $0.05 | 147449 |
| 299 | $0.04 | 148102 |
| 300 | $0.05 | 148689 |
| 301 | $0.06 | 151456 |
| 302 | $0.04 | 151851 |
| 303 | $0.05 | 152541 |
| 304 | $0.49 | 78404 |
| 305 | $0.06 | 84415 |
| 306 | $0.03 | 86101 |
| 307 | $0.03 | 87503 |
| 308 | $0.04 | 90841 |
| 309 | $0.03 | 91827 |
| 310 | $0.02 | 92341 |
| 311 | $0.02 | 92802 |
| 312 | $0.02 | 93355 |
| 313 | $0.02 | 93722 |
| 314 | $0.02 | 94262 |
| 315 | $0.02 | 94640 |
| 316 | $0.02 | 95306 |
| 317 | $0.06 | 99916 |
| 318 | $0.03 | 101348 |
| 319 | $0.03 | 102127 |
| 320 | $0.02 | 102567 |
| 321 | $0.02 | 102769 |
| 322 | $0.02 | 103021 |
| 323 | $0.03 | 103701 |
| 324 | $0.03 | 104382 |
| 325 | $0.10 | 114830 |
| 326 | $0.03 | 115567 |
| 327 | $0.03 | 116281 |
| 328 | $0.03 | 117122 |
| 329 | $0.03 | 117687 |
| 330 | $0.03 | 118117 |
| 331 | $0.03 | 118939 |
| 332 | $0.03 | 119824 |
| 333 | $0.05 | 123458 |
| 334 | $0.03 | 124037 |
| 335 | $0.03 | 124364 |
| 336 | $0.03 | 125086 |
| 337 | $0.03 | 125729 |
| 338 | $0.05 | 128583 |
| 339 | $0.03 | 129128 |
| 340 | $0.03 | 129731 |
| 341 | $0.04 | 130912 |
| 342 | $0.15 | 146504 |
| 343 | $0.03 | 146928 |
| 344 | $0.03 | 147248 |
| 345 | $0.03 | 147781 |
| 346 | $0.03 | 147994 |
| 347 | $0.03 | 148284 |
| 348 | $0.04 | 149118 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 10 | 4617 | $0.09 |
| 🟢 Green | 7 | 3241 | $0.06 |
| 🛠️ Refactor | 3 | 1003 | $0.02 |
| 🔎 verify-green | 4 | 1815 | $0.04 |
| 🔎 verify-refactor | 3 | 1003 | $0.02 |
| 🔎 verify-<phase> (revised) | 7 | 3305 | $0.07 |
| 🗺️ Plan | 2 | 942 | $0.02 |
| 🗺️ verify-plan | 6 | 2443 | $0.05 |
| ▶️ Resuming | 4 | 1495 | $0.03 |
| ⛔ Bailed | 2 | 969 | $0.02 |
| ⏹️ Stopped | 2 | 937 | $0.02 |
| Total | 36 | 15647 | $0.31 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 6 | 5 | 1 | 0 | 83 | 70 | 6 | 12 | 7720 | 5350 | 114950 | 0.37 |
| red | 18 | 6 | 2 | 0 | 1082 | 604 | 103 | 194 | 51490 | 1798001 | 424225 | 2.48 |
| green | 16 | 3 | 3 | 0 | 2292 | 468 | 96 | 184 | 36223 | 1604430 | 463564 | 2.26 |
| red-missing | 2 | 0 | 0 | 0 | 126 | 77 | 17 | 32 | 9346 | 350969 | 49533 | 0.25 |
| pin | 3 | 0 | 3 | 0 | 74 | 52 | 10 | 20 | 3687 | 145982 | 54818 | 0.19 |
| refactor | 3 | 0 | 0 | 0 | 20 | 12 | 6 | 12 | 882 | 61540 | 54216 | 0.15 |
| diff | 8 | 4 | 0 | 0 | 413 | 160 | 34 | 66 | 11175 | 484659 | 114410 | 0.45 |
| red-contradicted | 1 | 0 | 0 | 0 | 53 | 45 | 7 | 14 | 4905 | 159620 | 24293 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 27 | 18 | 9 | 0 | 2463 | 619 | 105 | 204 | 42612 | 1560405 | 506850 | 1.85 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 785 | 448 | 77 | 150 | 42878 | 1463154 | 388558 | 2.69 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 895 | 421 | 97 | 180 | 39938 | 1586992 | 404601 | 1.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 379 | 1.02 | 703 | 1.46 |
| green | 1152 | 2.01 | 1528 | 0.58 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 29 | 0.07 | 45 | 0.12 |
| refactor | 0 | 0.00 | 13 | 0.11 |
| diff | 0 | 0.00 | 96 | 0.14 |
| red-contradicted | 0 | 0.00 | 53 | 0.13 |
| preflight | 0 | 0.00 | 0 | 0.00 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 20 | 4 | 4 | 0 | 0 | 0 | 577 | 123 | 232 | 54316 | 2106133 | 603583 | 3.07 | 1824 | red 2/2, green 2/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 reads its EOF from the report closing its captured stdout within a bound of its own rather than a fixed 10 s wait, so a stand-in delay before status.py --report closes stdout, shorter than that bound, still passes; test-only, no production change, the case stays a process case ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 6 | 12 | 2232 | 79417 | 25607 | 0.09 | 155 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, test_2750 asserts its two conditions separately, so with status.py changed to hold stdout open until the refresh ends it goes red with a message naming no EOF, and a stub that never started fails with a message naming the stub not started; test-only, no production change ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 2676 | 136004 | 27023 | 0.11 | 217 | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_report_refresh_process.py, every wait inside test_2750 (the stdout wait, the stub-started wait and the cleanup wait together) is bounded below VERI_PYTEST_TIMEOUT (30 s default), so its failure paths are reachable before pytest-timeout fires; test-only, no production change ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 8 | 16 | 2548 | 115485 | 26438 | 0.10 | 11345 | n/a | n/a | n/a |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 223 | 32 | 64 | 14267 | 526072 | 162972 | 0.75 | unknown | 1/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, the scoping case's unrelated refresh lives at <tmp>/other/scripts/report-cache.sh (a directory also named scripts, not the old elsewhere), and the same case contrasts it with this script's own sibling report-cache.sh refresh being detected as already running (no second refresh launched): status.py --report with a stale snapshot still launches its own refresh while the unrelated <tmp>/other/scripts/report-cache.sh refresh is alive; production (skills/tdd/scripts/veri/status.py refresh_running, lines 468-476) compares the full resolved path of the matched script against this script's own scripts/report-cache.sh, not the basename of its directory, and the case must go red when that comparison is loosened back to the directory basename (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 6 | 1 | 1 | 0 | 0 | 0 | 198 | 36 | 68 | 17470 | 664739 | 124101 | 0.69 | unknown | 1/2 | unknown | unknown |  |  | full |
| test_2750 unit case's fake ps listing (skills/tdd/scripts/tests/py/test_status_report_last_written.py:119) shows this script's own sibling report-cache.sh, so it stays green under full-path comparison; test-only, no production change ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 11 | 20 | 3719 | 153753 | 35342 | 0.14 | unknown | n/a | n/a | n/a |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, the scoping case's unrelated refresh lives at <tmp>/other/scripts/report-cache.sh (a directory also named scripts, not the old elsewhere): status.py --report with a stale snapshot still launches its own refresh while that unrelated refresh is alive; production (skills/tdd/scripts/veri/status.py refresh_running) compares the full resolved path of the matched script against this script's own scripts/report-cache.sh, not the basename of its directory, so the case goes red when that comparison is loosened back to the directory basename (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 228 | 41 | 78 | 16566 | 706960 | 143824 | 0.80 | unknown | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, a separate case: with this script's own sibling report-cache.sh refresh alive (started by the case itself and stopped by it), status.py --report with a stale snapshot detects it as already running and launches no second refresh (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 32 | 7 | 14 | 3914 | 116638 | 36169 | 0.14 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, the scoping case's unrelated refresh lives at <tmp>/other/scripts/report-cache.sh (a directory also named scripts, not the old elsewhere): status.py --report with a stale snapshot still launches its own refresh while that unrelated refresh is alive; production (skills/tdd/scripts/veri/status.py refresh_running) compares the full resolved path of the matched script against this script's own scripts/report-cache.sh, not the basename of its directory, so the case goes red when that comparison is loosened back to the directory basename (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| status.py --report with a stale snapshot still launches its own sibling report-cache.sh refresh while an unrelated `report-cache.sh refresh` process at a different path is alive on the machine (only a refresh of its own sibling script counts as already running), pinned by a new process case in skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py that starts that unrelated process itself and stops it; the existing unit case test_2750_report_starts_no_refresh_when_a_report_cache_refresh_is_already_running stays green ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py — test_3521_report_with_a_stale_snapshot_launches_its_own_refresh_while_an_unrelated_refresh_is_alive: AssertionError: the stale report did not launch its own refresh while an unrelated refresh was alive; skills/tdd/scripts/tests/py/unit/test_file_location_resolves_symlinks.py — test_no_veri_module_locates_itself_through_abspath_of_file_3501: assert {'status.py': [471]} == {} ⟦suite-repair⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| In skills/tdd/scripts/tests/py/test_status_refresh_scope_process.py, the scoping case's unrelated refresh lives at <tmp>/other/scripts/report-cache.sh (a directory also named scripts, not the old elsewhere): status.py --report with a stale snapshot still launches its own refresh while that unrelated refresh is alive; production (skills/tdd/scripts/veri/status.py refresh_running) compares the full resolved path of the matched script against this script's own scripts/report-cache.sh, not the basename of its directory, so the case goes red when that comparison is loosened back to the directory basename (a process case, no network) ⟦added⟧ ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 4 | ? | ? | nothing-left 3, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 9 | 2 | 10 | 10 | 1 | 10 | 17 | 18 | 9 | 2 | 2 | 4 | 3 | 9 | 573 | 1 | 2 | 1 | 2 | 2 | 3 | 1 | 1 | 9 | 10 | 2 | 3 | 2 | 2 | 3 | 3 | 9 | 10 | 10 | 4 | 4 | 0 | 1 | 2 | 10 | 9 | 9 | 2 | 2 | 3 | 2 | 3 |
| fast | 21 | 21 | 22 | 31 | 456 | 32 | 23 | 22 | 22 | 22 | 21 | 22 | 47 | 23 | 21 | 26 | 32 | 32 | 30 | 21 | 0 | 23 | 22 | 21 | 21 | 22 | 27 | 22 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 3 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 279 | 534 | 125428 | 4610551 | 1300009 | 25.00 (estimate) |

## Refactor owed

### Test-only

These change only test files (tests/ directories, *.test.*, JS/TS *.spec.*, Go *_test.go, Python test_*.py and *_test.py); the structural pass does not work them.

- extract the scratch-scripts, stale-cache and repo setup shared by the two `test_3521_*` cases in test_status_refresh_scope_process.py into a helper

## Owed by a human
- `pin-recheck.sh` flagged earlier mutation pins on `skills/tdd/scripts/veri/status.py` as needing a look: "old text occurs more than once" ×1 and "old text gone" ×8. The step's code rewrote `refresh_running()`, so their recorded mutations no longer apply as written. Re-check that those pins still guard what they claim.
