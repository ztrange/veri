### 📊 Metrics — issue 2900

Wall time for the issue: 5860 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 22 of 23 planned.
Outcome: the run bailed — suite-red, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $13.96 over 266 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87232 tokens, largest 173563 tokens
Conductor context: first turn 87226 tokens, largest 177813 tokens
Conductor context: first turn 87262 tokens, largest 238686 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87232 |
| 2 | $0.08 | 94109 |
| 3 | $0.06 | 97760 |
| 4 | $0.05 | 99377 |
| 5 | $0.03 | 100053 |
| 6 | $0.04 | 100584 |
| 7 | $0.03 | 100827 |
| 8 | $0.04 | 101313 |
| 9 | $0.04 | 101963 |
| 10 | $0.03 | 102299 |
| 11 | $0.05 | 104327 |
| 12 | $0.05 | 107150 |
| 13 | $0.06 | 110351 |
| 14 | $0.04 | 110821 |
| 15 | $0.06 | 113905 |
| 16 | $0.11 | 123296 |
| 17 | $0.05 | 125902 |
| 18 | $0.06 | 128504 |
| 19 | $0.05 | 130162 |
| 20 | $0.05 | 131477 |
| 21 | $0.06 | 134601 |
| 22 | $0.05 | 135311 |
| 23 | $0.04 | 135844 |
| 24 | $0.04 | 136479 |
| 25 | $0.06 | 138034 |
| 26 | $0.04 | 138781 |
| 27 | $0.07 | 142355 |
| 28 | $0.05 | 143235 |
| 29 | $0.05 | 145232 |
| 30 | $0.04 | 145455 |
| 31 | $0.05 | 146211 |
| 32 | $0.05 | 147056 |
| 33 | $0.05 | 147969 |
| 34 | $0.05 | 149797 |
| 35 | $0.05 | 150671 |
| 36 | $0.08 | 155249 |
| 37 | $0.05 | 156406 |
| 38 | $0.06 | 158094 |
| 39 | $0.04 | 158433 |
| 40 | $0.06 | 159771 |
| 41 | $0.05 | 160456 |
| 42 | $0.05 | 161579 |
| 43 | $0.05 | 162079 |
| 44 | $0.05 | 162578 |
| 45 | $0.05 | 163585 |
| 46 | $0.04 | 163999 |
| 47 | $0.06 | 165778 |
| 48 | $0.05 | 166100 |
| 49 | $0.05 | 166949 |
| 50 | $0.09 | 171883 |
| 51 | $0.05 | 172768 |
| 52 | $0.05 | 173563 |
| 53 | $0.57 | 87226 |
| 54 | $0.08 | 93924 |
| 55 | $0.06 | 97586 |
| 56 | $0.04 | 99158 |
| 57 | $0.07 | 103408 |
| 58 | $0.06 | 107303 |
| 59 | $0.04 | 107803 |
| 60 | $0.03 | 108332 |
| 61 | $0.04 | 108666 |
| 62 | $0.03 | 109160 |
| 63 | $0.04 | 109940 |
| 64 | $0.04 | 110763 |
| 65 | $0.05 | 112064 |
| 66 | $0.04 | 113209 |
| 67 | $0.04 | 113907 |
| 68 | $0.03 | 114132 |
| 69 | $0.05 | 115520 |
| 70 | $0.04 | 116435 |
| 71 | $0.04 | 117237 |
| 72 | $0.04 | 118361 |
| 73 | $0.05 | 119934 |
| 74 | $0.04 | 120521 |
| 75 | $0.05 | 122139 |
| 76 | $0.04 | 122803 |
| 77 | $0.05 | 124232 |
| 78 | $0.03 | 124669 |
| 79 | $0.05 | 125423 |
| 80 | $0.10 | 133446 |
| 81 | $0.04 | 134562 |
| 82 | $0.05 | 135655 |
| 83 | $0.05 | 136559 |
| 84 | $0.04 | 137078 |
| 85 | $0.04 | 137913 |
| 86 | $0.05 | 138614 |
| 87 | $0.06 | 141110 |
| 88 | $0.04 | 141971 |
| 89 | $0.05 | 142997 |
| 90 | $0.05 | 144289 |
| 91 | $0.04 | 144817 |
| 92 | $0.05 | 145535 |
| 93 | $0.04 | 145860 |
| 94 | $0.04 | 146253 |
| 95 | $0.06 | 147673 |
| 96 | $0.04 | 148442 |
| 97 | $0.05 | 148829 |
| 98 | $0.04 | 149726 |
| 99 | $0.05 | 150510 |
| 100 | $0.05 | 150979 |
| 101 | $0.04 | 151710 |
| 102 | $0.05 | 152673 |
| 103 | $0.05 | 153996 |
| 104 | $0.05 | 154620 |
| 105 | $0.05 | 155186 |
| 106 | $0.05 | 156726 |
| 107 | $0.05 | 157043 |
| 108 | $0.04 | 157716 |
| 109 | $0.05 | 158231 |
| 110 | $0.05 | 158787 |
| 111 | $0.05 | 159927 |
| 112 | $0.04 | 160196 |
| 113 | $0.06 | 161715 |
| 114 | $0.06 | 163737 |
| 115 | $0.04 | 164174 |
| 116 | $0.05 | 164499 |
| 117 | $0.05 | 165443 |
| 118 | $0.05 | 165688 |
| 119 | $0.05 | 166031 |
| 120 | $0.04 | 166345 |
| 121 | $0.06 | 167604 |
| 122 | $0.05 | 169278 |
| 123 | $0.06 | 171062 |
| 124 | $0.09 | 175817 |
| 125 | $0.05 | 176793 |
| 126 | $0.05 | 177813 |
| 127 | $0.56 | 87262 |
| 128 | $0.07 | 93949 |
| 129 | $0.05 | 97564 |
| 130 | $0.03 | 99085 |
| 131 | $0.07 | 105438 |
| 132 | $0.06 | 110141 |
| 133 | $0.03 | 110715 |
| 134 | $0.03 | 111303 |
| 135 | $0.02 | 111638 |
| 136 | $0.03 | 112145 |
| 137 | $0.03 | 112846 |
| 138 | $0.05 | 116515 |
| 139 | $0.03 | 117800 |
| 140 | $0.05 | 121665 |
| 141 | $0.03 | 122549 |
| 142 | $0.03 | 123426 |
| 143 | $0.10 | 132989 |
| 144 | $0.03 | 133901 |
| 145 | $0.03 | 134699 |
| 146 | $0.04 | 135714 |
| 147 | $0.03 | 136479 |
| 148 | $0.04 | 137550 |
| 149 | $0.05 | 140034 |
| 150 | $0.03 | 140754 |
| 151 | $0.03 | 141085 |
| 152 | $0.03 | 141854 |
| 153 | $0.05 | 144050 |
| 154 | $0.03 | 144542 |
| 155 | $0.03 | 145223 |
| 156 | $0.04 | 146258 |
| 157 | $0.03 | 146641 |
| 158 | $0.04 | 147699 |
| 159 | $0.03 | 148133 |
| 160 | $0.04 | 148897 |
| 161 | $0.04 | 149876 |
| 162 | $0.03 | 150288 |
| 163 | $0.04 | 151001 |
| 164 | $0.03 | 151462 |
| 165 | $0.03 | 151882 |
| 166 | $0.05 | 154004 |
| 167 | $0.04 | 154861 |
| 168 | $0.04 | 155413 |
| 169 | $0.05 | 157831 |
| 170 | $0.04 | 158283 |
| 171 | $0.03 | 158526 |
| 172 | $0.03 | 158856 |
| 173 | $0.04 | 159392 |
| 174 | $0.04 | 160259 |
| 175 | $0.04 | 160754 |
| 176 | $0.04 | 161154 |
| 177 | $0.04 | 161693 |
| 178 | $0.04 | 162065 |
| 179 | $0.04 | 162518 |
| 180 | $0.04 | 163443 |
| 181 | $0.04 | 163887 |
| 182 | $0.03 | 164123 |
| 183 | $0.04 | 164452 |
| 184 | $0.04 | 165317 |
| 185 | $0.04 | 166279 |
| 186 | $0.04 | 166735 |
| 187 | $0.03 | 166940 |
| 188 | $0.04 | 167275 |
| 189 | $0.04 | 167766 |
| 190 | $0.04 | 168779 |
| 191 | $0.04 | 169190 |
| 192 | $0.04 | 169480 |
| 193 | $0.04 | 170294 |
| 194 | $0.04 | 171070 |
| 195 | $0.04 | 171940 |
| 196 | $0.04 | 172377 |
| 197 | $0.04 | 172582 |
| 198 | $0.04 | 173347 |
| 199 | $0.04 | 174173 |
| 200 | $0.04 | 174638 |
| 201 | $0.04 | 174917 |
| 202 | $0.04 | 175489 |
| 203 | $0.04 | 176486 |
| 204 | $0.04 | 177102 |
| 205 | $0.04 | 177509 |
| 206 | $0.04 | 178636 |
| 207 | $0.04 | 179728 |
| 208 | $0.04 | 180158 |
| 209 | $0.04 | 180962 |
| 210 | $0.04 | 181454 |
| 211 | $0.05 | 182869 |
| 212 | $0.04 | 183567 |
| 213 | $0.04 | 184184 |
| 214 | $0.04 | 185065 |
| 215 | $0.04 | 185658 |
| 216 | $0.10 | 193922 |
| 217 | $0.05 | 195486 |
| 218 | $0.04 | 196206 |
| 219 | $0.05 | 198088 |
| 220 | $0.05 | 198881 |
| 221 | $0.04 | 199248 |
| 222 | $0.04 | 199837 |
| 223 | $0.05 | 201230 |
| 224 | $0.05 | 202418 |
| 225 | $0.05 | 203066 |
| 226 | $0.05 | 204016 |
| 227 | $0.04 | 204412 |
| 228 | $0.04 | 204619 |
| 229 | $0.05 | 205862 |
| 230 | $0.04 | 206232 |
| 231 | $0.04 | 206610 |
| 232 | $0.05 | 207269 |
| 233 | $0.05 | 208822 |
| 234 | $0.05 | 209534 |
| 235 | $0.05 | 210566 |
| 236 | $0.04 | 210780 |
| 237 | $0.05 | 211444 |
| 238 | $0.05 | 212484 |
| 239 | $0.05 | 213123 |
| 240 | $0.05 | 214011 |
| 241 | $0.05 | 215259 |
| 242 | $0.05 | 215740 |
| 243 | $0.05 | 217138 |
| 244 | $0.05 | 217415 |
| 245 | $0.05 | 217847 |
| 246 | $0.05 | 218905 |
| 247 | $0.05 | 219336 |
| 248 | $0.05 | 219798 |
| 249 | $0.05 | 220355 |
| 250 | $0.05 | 221187 |
| 251 | $0.05 | 221468 |
| 252 | $0.06 | 223749 |
| 253 | $0.06 | 226227 |
| 254 | $0.05 | 227323 |
| 255 | $0.05 | 228500 |
| 256 | $0.05 | 229518 |
| 257 | $0.05 | 230059 |
| 258 | $0.05 | 230519 |
| 259 | $0.06 | 231715 |
| 260 | $0.05 | 232214 |
| 261 | $0.05 | 232692 |
| 262 | $0.05 | 232987 |
| 263 | $0.05 | 233359 |
| 264 | $0.05 | 233835 |
| 265 | $0.09 | 238686 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 29 | 2 | 4 | 3385 | 33346 | 38641 | 0.13 |
| red | 47 | 20 | 1 | 0 | 1888 | 1148 | 235 | 454 | 97938 | 7485524 | 1157196 | 5.15 |
| green | 62 | 14 | 16 | 0 | 3906 | 1213 | 315 | 600 | 101962 | 9800370 | 1166305 | 5.82 |
| red-missing | 6 | 0 | 0 | 0 | 277 | 212 | 36 | 70 | 22372 | 1239389 | 143820 | 0.71 |
| pin | 13 | 12 | 1 | 0 | 353 | 256 | 61 | 122 | 20070 | 1865810 | 273220 | 1.07 |
| exhausted | 2 | 0 | 0 | 0 | 94 | 62 | 10 | 20 | 4525 | 315108 | 40887 | 0.36 |
| refactor | 18 | 2 | 0 | 0 | 300 | 186 | 49 | 96 | 12933 | 1330160 | 369468 | 1.36 |
| prose | 4 | 0 | 0 | 0 | 41 | 33 | 4 | 8 | 4505 | 14118 | 30337 | 0.12 |
| skill-edit | 1 | 0 | 0 | 0 | 12 | 9 | 3 | 6 | 1301 | 76764 | 13295 | 0.05 |
| red-supersede | 1 | 0 | 0 | 0 | 52 | 48 | 7 | 14 | 4947 | 267848 | 33140 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 68 | 49 | 19 | 0 | 3531 | 1263 | 290 | 570 | 103115 | 8876570 | 1221774 | 4.97 |
| developer | claude-sonnet-5-5 | 63 | 0 | 0 | 0 | 2179 | 1359 | 311 | 586 | 118312 | 9705907 | 1430165 | 6.16 |
| developer | claude-opus-5-5 | 20 | 0 | 0 | 0 | 1192 | 532 | 114 | 224 | 46705 | 3755078 | 570738 | 3.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 312 | 0.81 | 212 | 0.71 |
| green | 2391 | 3.28 | 1154 | 2.00 |
| red-missing | 0 | 0.00 | 202 | 0.52 |
| pin | 0 | 0.00 | 115 | 0.35 |
| exhausted | 0 | 0.00 | 94 | 0.36 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails ⟦criterion 1⟧ | 13 | 2 | 4 | 0 | 0 | 0 | 247 | 57 | 112 | 24420 | 1779058 | 251197 | 1.34 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails; every guard the step adds is pinned by a case only it decides ⟦criterion 1⟧ | 23 | 4 | 7 | 0 | 0 | 0 | 610 | 116 | 226 | 57313 | 3778205 | 468683 | 2.60 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails. Minimal: its green adds only what this step's own case decides — no argument-shape check, no unknown-commit check, no signal handler; each lands in the later step that pins it ⟦criterion 1⟧ | 13 | 3 | 3 | 0 | 0 | 0 | 263 | 52 | 102 | 20501 | 1564736 | 262378 | 1.25 | 873 | 2/2 | 0/5 | nothing-left |  |  | already-satisfied |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` exits 1 when the command passes on the restored before-state ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 8 | 16 | 3418 | 244595 | 38848 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before` leaves `<test-path>` exactly as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 11 | 22 | 3932 | 354999 | 41516 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before` leaves every file under `.tdd/` as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 83 | 19 | 36 | 5585 | 541747 | 96833 | 0.35 | 263 | unknown | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before` removes a file added since `<sha>` (tracked or untracked) while the command runs ⟦criterion 1⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 125 | 23 | 46 | 10321 | 675363 | 158684 | 0.74 | 724 | 1/2 | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before` keeps a `<test-path>` that is itself new since `<sha>` present with its working-tree bytes while the command runs, so a command that reads the kept file passes where one that finds it removed or blanked fails ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 82 | 12 | 24 | 4241 | 382959 | 58849 | 0.23 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before` brings back a file deleted since `<sha>`, with its `<sha>` content, while the command runs ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 152 | 39 | 70 | 13389 | 1072970 | 175402 | 0.68 | 454 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| `mutation-probe.sh --before` restores a file renamed since `<sha>` as a deletion of the new name and a return of the old name (the diff runs with `--no-renames`), so the old name comes back with its `<sha>` content ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 86 | 23 | 42 | 5374 | 653334 | 97555 | 0.36 | 248 | unknown | 0/5 | nothing-left |  |  | full |
| after the command, `mutation-probe.sh --before` puts every tracked file it restored back to its working-tree bytes ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 12 | 20 | 3930 | 323391 | 42422 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| after the command, `mutation-probe.sh --before` removes again a file it brought back from `<sha>` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 14 | 24 | 4574 | 401043 | 44341 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| after the command, `mutation-probe.sh --before` puts back every untracked file it removed, byte for byte ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 12 | 24 | 4933 | 404904 | 43482 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` does not resolve to a commit ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 73 | 19 | 36 | 4930 | 545003 | 96823 | 0.35 | 217 | unknown | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before` exits 2 with the usage message without running the command when `--keep <test-path> --` is missing or out of place (fewer than 6 arguments, `argv[2]` not `--keep`, or `argv[4]` not `--`), one case per condition, each asserting the stderr usage line (exit code alone cannot tell a short argv from an IndexError mapped to 2) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 76 | 21 | 38 | 6260 | 581245 | 98183 | 0.37 | 201 | unknown | 0/5 | nothing-left |  |  | full |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` is not 7-40 lowercase hex (`^[0-9a-f]{7,40}$`) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 80 | 24 | 44 | 6035 | 694665 | 97428 | 0.37 | 232 | unknown | 0/5 | structural-owed |  |  | full |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when no file other than `<test-path>` and `.tdd/` differs between `<sha>` and the working tree ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 61 | 20 | 38 | 5099 | 581610 | 96785 | 0.35 | 195 | unknown | 0/5 | nothing-left |  |  | full |
| when the before-state probe exits 0, it appends a record to `VERI_MUTATION_RECORD` carrying `before <sha>`, `keep <test-path>` and `command` ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 24 | 46 | 7399 | 718195 | 124361 | 0.46 | 286 | unknown | 1/5 | nothing-left |  |  | full |
| a process case (`@pytest.mark.process`, in `test_mutation_probe_process.py`) on a scratch git repo in the shape of the issue's Steps to reproduce (`view.py`, `quote.py` changed on the branch, a test stubbing `{"deps": 10}`) shows `mutation-probe.sh --before <base> --keep <test>` exits 1 and the working tree is unchanged afterwards ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 10 | 20 | 4410 | 331333 | 42585 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/scripts/prompts/verify-pin.md`: check 2 first runs the before-state probe `{{MUTATION_PROBE}} --before {{BRANCH_BASE}} --keep '{{TEST_PATH}}' -- <command>`, REJECTs naming "the real before-state stays green" on its exit 1, and allows a hand mutation only when it exits 2 because no file differs (VP5, VP8) ⟦skill-edit⟧ ⟦criterion 2⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 42 | 7 | 14 | 5806 | 90882 | 43632 | 0.18 | 83 | unknown | unknown | unknown |  |  | full |
| `build-verify-prompt.sh pin` fills a `{{BRANCH_BASE}}` slot in the pin template with the run's branch point, `git merge-base HEAD origin/<default>`, carrying only that commit name ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 230 | 47 | 94 | 19401 | 1675912 | 191704 | 1.06 | 544 | 1/2 | 0/5 | nothing-left |  |  | full |
| a pin verify (`verify.sh pin`) renders its prompt with `{{BRANCH_BASE}}` filled by the run's branch point, `git merge-base HEAD origin/<default>`, so the before-state probe line never reaches the verifier with an empty sha ⟦added⟧ ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 155 | 41 | 82 | 11880 | 1406374 | 157784 | 0.78 | 508 | 1/2 | 0/5 | nothing-left |  |  | full |
| `build-verify-prompt.sh pin` refuses with exit 2 when the branch base it would fill into `{{BRANCH_BASE}}` is not 7-40 lowercase hex ⟦criterion 2⟧ | 13 | 6 | 0 | 0 | 0 | 0 | 317 | 69 | 136 | 24619 | 2283541 | 279862 | 1.33 | 788 | 1/2 | 1/5 | nothing-left |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_verify_process.py — FAILED test_verify_sh_pin_whose_verifier_writes_only_its_mutation_record_takes_the_pass_and_keeps_the_record_2741 - AssertionError: build-verify-prompt: pin needs --branch-base; skills/tdd/scripts/tests/py/test_verify.py — FAILED test_main_reads_the_verdict_from_supervises_stdout_and_prints_the_whole_reason_with_one_newline[…-pin] (a pin verify in a repo with no origin gets no branch base); skills/tdd/scripts/tests/py/test_skill_leaf_env.py — 3 FAILED; skills/tdd/scripts/tests/py/test_prompt_test_tiers.py — FAILED test_verify_red_green_refactor_and_pin_run_their_test_commands_through_timed_test_run_each_naming_its_tier; skills/tdd/scripts/tests/py/test_ignored_signals_process.py — FAILED test_a_signal_case_passes_in_a_pytest_run_started_with_int_term_and_hup_ignored_2294 - the signal case did not finish ⟦suite-repair⟧ ⟦criterion 2⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 140 | 40 | 78 | 12783 | 1309027 | 218331 | 0.93 | 952 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `mutation-probe.sh --before <sha> --keep <test-path> -- <command…>` runs the command with every tracked file that differs between `<sha>` and the working tree restored to its `<sha>` content, and exits 0 when the command fails. Minimal: its green adds only what this step's own case decides — no argument-shape check, no unknown-commit check, no signal handler; each lands in the later step that pins it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.06 |
| `mutation-probe.sh --before` leaves every file under `.tdd/` as it is in the working tree while the command runs, not restored to `<sha>` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 15 | 0.05 |
| `mutation-probe.sh --before` removes a file added since `<sha>` (tracked or untracked) while the command runs ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 1 | 76 | 0.45 |
| `mutation-probe.sh --before` brings back a file deleted since `<sha>`, with its `<sha>` content, while the command runs ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| `mutation-probe.sh --before` restores a file renamed since `<sha>` as a deletion of the new name and a return of the old name (the diff runs with `--no-renames`), so the old name comes back with its `<sha>` content ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` does not resolve to a commit ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.05 |
| `mutation-probe.sh --before` exits 2 with the usage message without running the command when `--keep <test-path> --` is missing or out of place (fewer than 6 arguments, `argv[2]` not `--keep`, or `argv[4]` not `--`), one case per condition, each asserting the stderr usage line (exit code alone cannot tell a short argv from an IndexError mapped to 2) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when `<sha>` is not 7-40 lowercase hex (`^[0-9a-f]{7,40}$`) ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | skipped | 0 | 11 | 0.05 |
| `mutation-probe.sh --before <sha>` exits 2 without running the command when no file other than `<test-path>` and `.tdd/` differs between `<sha>` and the working tree ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |
| when the before-state probe exits 0, it appends a record to `VERI_MUTATION_RECORD` carrying `before <sha>`, `keep <test-path>` and `command` ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 52 | 0.13 |
| `build-verify-prompt.sh pin` fills a `{{BRANCH_BASE}}` slot in the pin template with the run's branch point, `git merge-base HEAD origin/<default>`, carrying only that commit name ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.05 |
| a pin verify (`verify.sh pin`) renders its prompt with `{{BRANCH_BASE}}` filled by the run's branch point, `git merge-base HEAD origin/<default>`, so the before-state probe line never reaches the verifier with an empty sha ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.06 |
| `build-verify-prompt.sh pin` refuses with exit 2 when the branch base it would fill into `{{BRANCH_BASE}}` is not 7-40 lowercase hex ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 73 | 0.14 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_verify_process.py — FAILED test_verify_sh_pin_whose_verifier_writes_only_its_mutation_record_takes_the_pass_and_keeps_the_record_2741 - AssertionError: build-verify-prompt: pin needs --branch-base; skills/tdd/scripts/tests/py/test_verify.py — FAILED test_main_reads_the_verdict_from_supervises_stdout_and_prints_the_whole_reason_with_one_newline[…-pin] (a pin verify in a repo with no origin gets no branch base); skills/tdd/scripts/tests/py/test_skill_leaf_env.py — 3 FAILED; skills/tdd/scripts/tests/py/test_prompt_test_tiers.py — FAILED test_verify_red_green_refactor_and_pin_run_their_test_commands_through_timed_test_run_each_naming_its_tier; skills/tdd/scripts/tests/py/test_ignored_signals_process.py — FAILED test_a_signal_case_passes_in_a_pytest_run_started_with_int_term_and_hup_ignored_2294 - the signal case did not finish ⟦suite-repair⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s | run 82 s | run 83 s | run 84 s | run 85 s | run 86 s | run 87 s | run 88 s | run 89 s | run 90 s | run 91 s | run 92 s | run 93 s | run 94 s | run 95 s | run 96 s | run 97 s | run 98 s | run 99 s | run 100 s | run 101 s | run 102 s | run 103 s | run 104 s | run 105 s | run 106 s | run 107 s | run 108 s | run 109 s | run 110 s | run 111 s | run 112 s | run 113 s | run 114 s | run 115 s | run 116 s | run 117 s | run 118 s | run 119 s | run 120 s | run 121 s | run 122 s | run 123 s | run 124 s | run 125 s | run 126 s | run 127 s | run 128 s | run 129 s | run 130 s | run 131 s | run 132 s | run 133 s | run 134 s | run 135 s | run 136 s | run 137 s | run 138 s | run 139 s | run 140 s | run 141 s | run 142 s | run 143 s | run 144 s | run 145 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 2 | 3 | 0 | 3 | 4 | 3 | 3 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 4 | 4 | 4 | 2 | 4 | 2 | 2 | 2 | 2 | 2 | 2 | 4 | 4 | 1 | 1 | 2 | 2 | 2 | 4 | 5 | 2 | 2 | 3 | 3 | 2 | 2 | 3 | 6 | 6 | 4 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 6 | 2 | 23 | 26 | 6 | 1 | 6 | 3 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 6 | 5 | 3 | 2 | 1 | 24 | 27 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 19 | 20 | 18 | 19 | 21 | 22 | 19 | 21 | 19 | 18 | 19 | 19 | 19 | 19 | 20 | 21 | 21 | 21 | 19 | 19 | 20 | 19 | 30 | 20 | 36 | 19 | 24 | 19 | 19 | 19 | 19 | 21 | 19 | 22 | 21 | 21 | 18 | 18 | 21 | 27 | 19 | 18 | 29 | 19 | 19 | 19 | 20 | 34 | 20 | 18 | 21 | 18 | 26 | 18 | 19 | 19 | 20 | 20 | 19 | 31 | 19 | 20 | 19 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 3 | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 1 | 2 | 1 | 2 | 3 | 1 | 2 | 2 | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 722 | 1394 | 273938 | 22428437 | 3266309 | 28.89 (estimate) |
