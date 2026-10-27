### 📊 Metrics — issue 2483

Wall time for the issue: 3761 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 9 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $12.72 over 243 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88981 tokens, largest 213118 tokens
Conductor context: first turn 88968 tokens, largest 161295 tokens
Conductor context: first turn 88968 tokens, largest 182967 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 88981 |
| 2 | $0.03 | 89316 |
| 3 | $0.05 | 91423 |
| 4 | $0.05 | 92993 |
| 5 | $0.04 | 93625 |
| 6 | $0.04 | 94180 |
| 7 | $0.03 | 94708 |
| 8 | $0.04 | 95014 |
| 9 | $0.04 | 95283 |
| 10 | $0.04 | 95888 |
| 11 | $0.03 | 96219 |
| 12 | $0.14 | 109419 |
| 13 | $0.05 | 111045 |
| 14 | $0.07 | 115076 |
| 15 | $0.06 | 117865 |
| 16 | $0.05 | 118334 |
| 17 | $0.04 | 119540 |
| 18 | $0.08 | 123797 |
| 19 | $0.05 | 125095 |
| 20 | $0.08 | 130601 |
| 21 | $0.06 | 132935 |
| 22 | $0.06 | 134719 |
| 23 | $0.06 | 136896 |
| 24 | $0.04 | 137357 |
| 25 | $0.05 | 138296 |
| 26 | $0.05 | 138800 |
| 27 | $0.05 | 139566 |
| 28 | $0.05 | 140010 |
| 29 | $0.12 | 150489 |
| 30 | $0.05 | 150904 |
| 31 | $0.05 | 151609 |
| 32 | $0.06 | 152408 |
| 33 | $0.04 | 152827 |
| 34 | $0.06 | 154398 |
| 35 | $0.05 | 154929 |
| 36 | $0.06 | 156064 |
| 37 | $0.11 | 164027 |
| 38 | $0.05 | 164815 |
| 39 | $0.06 | 166119 |
| 40 | $0.06 | 167714 |
| 41 | $0.06 | 168849 |
| 42 | $0.06 | 169808 |
| 43 | $0.05 | 170247 |
| 44 | $0.06 | 172230 |
| 45 | $0.06 | 173203 |
| 46 | $0.06 | 173781 |
| 47 | $0.05 | 174476 |
| 48 | $0.06 | 174856 |
| 49 | $0.05 | 175767 |
| 50 | $0.06 | 176361 |
| 51 | $0.06 | 177543 |
| 52 | $0.06 | 178404 |
| 53 | $0.06 | 180098 |
| 54 | $0.06 | 180999 |
| 55 | $0.06 | 182137 |
| 56 | $0.05 | 182523 |
| 57 | $0.06 | 183725 |
| 58 | $0.07 | 184811 |
| 59 | $0.05 | 185676 |
| 60 | $0.08 | 188020 |
| 61 | $0.05 | 188907 |
| 62 | $0.06 | 190480 |
| 63 | $0.08 | 193228 |
| 64 | $0.06 | 193724 |
| 65 | $0.06 | 195273 |
| 66 | $0.08 | 197454 |
| 67 | $0.06 | 198277 |
| 68 | $0.06 | 199968 |
| 69 | $0.07 | 201201 |
| 70 | $0.06 | 202179 |
| 71 | $0.07 | 204085 |
| 72 | $0.07 | 204816 |
| 73 | $0.06 | 205928 |
| 74 | $0.06 | 206719 |
| 75 | $0.10 | 211405 |
| 76 | $0.06 | 212266 |
| 77 | $0.07 | 213118 |
| 78 | $0.58 | 88968 |
| 79 | $0.04 | 89482 |
| 80 | $0.03 | 89843 |
| 81 | $0.07 | 95079 |
| 82 | $0.07 | 98982 |
| 83 | $0.03 | 99310 |
| 84 | $0.04 | 99800 |
| 85 | $0.03 | 100096 |
| 86 | $0.03 | 100388 |
| 87 | $0.04 | 101159 |
| 88 | $0.05 | 102571 |
| 89 | $0.03 | 103288 |
| 90 | $0.04 | 104018 |
| 91 | $0.04 | 104243 |
| 92 | $0.04 | 105623 |
| 93 | $0.04 | 106275 |
| 94 | $0.04 | 106602 |
| 95 | $0.03 | 107157 |
| 96 | $0.05 | 108979 |
| 97 | $0.04 | 109747 |
| 98 | $0.05 | 110988 |
| 99 | $0.04 | 111970 |
| 100 | $0.04 | 112879 |
| 101 | $0.04 | 113698 |
| 102 | $0.04 | 114146 |
| 103 | $0.10 | 121820 |
| 104 | $0.04 | 123113 |
| 105 | $0.05 | 124490 |
| 106 | $0.04 | 125420 |
| 107 | $0.05 | 126019 |
| 108 | $0.04 | 127035 |
| 109 | $0.05 | 127970 |
| 110 | $0.04 | 128917 |
| 111 | $0.05 | 129897 |
| 112 | $0.04 | 130612 |
| 113 | $0.04 | 131139 |
| 114 | $0.06 | 133436 |
| 115 | $0.05 | 134689 |
| 116 | $0.05 | 135526 |
| 117 | $0.04 | 136229 |
| 118 | $0.05 | 137324 |
| 119 | $0.04 | 138182 |
| 120 | $0.05 | 139242 |
| 121 | $0.05 | 140399 |
| 122 | $0.05 | 141246 |
| 123 | $0.05 | 142570 |
| 124 | $0.05 | 143916 |
| 125 | $0.05 | 144264 |
| 126 | $0.05 | 145431 |
| 127 | $0.04 | 146410 |
| 128 | $0.06 | 147689 |
| 129 | $0.05 | 148764 |
| 130 | $0.04 | 149605 |
| 131 | $0.05 | 150506 |
| 132 | $0.06 | 151659 |
| 133 | $0.04 | 152523 |
| 134 | $0.05 | 153385 |
| 135 | $0.06 | 154825 |
| 136 | $0.08 | 159478 |
| 137 | $0.05 | 160419 |
| 138 | $0.05 | 161295 |
| 139 | $0.57 | 88968 |
| 140 | $0.04 | 91219 |
| 141 | $0.05 | 94874 |
| 142 | $0.06 | 99443 |
| 143 | $0.02 | 99943 |
| 144 | $0.02 | 100366 |
| 145 | $0.02 | 100692 |
| 146 | $0.02 | 101063 |
| 147 | $0.03 | 101685 |
| 148 | $0.03 | 102640 |
| 149 | $0.03 | 103370 |
| 150 | $0.03 | 104066 |
| 151 | $0.02 | 104291 |
| 152 | $0.04 | 106312 |
| 153 | $0.03 | 107310 |
| 154 | $0.03 | 108370 |
| 155 | $0.02 | 108726 |
| 156 | $0.03 | 109303 |
| 157 | $0.03 | 109921 |
| 158 | $0.03 | 110503 |
| 159 | $0.04 | 112128 |
| 160 | $0.03 | 112779 |
| 161 | $0.03 | 113568 |
| 162 | $0.03 | 113984 |
| 163 | $0.03 | 114526 |
| 164 | $0.03 | 114970 |
| 165 | $0.08 | 122638 |
| 166 | $0.03 | 123792 |
| 167 | $0.03 | 124833 |
| 168 | $0.03 | 125413 |
| 169 | $0.03 | 126014 |
| 170 | $0.03 | 127101 |
| 171 | $0.04 | 128896 |
| 172 | $0.03 | 129452 |
| 173 | $0.03 | 130136 |
| 174 | $0.03 | 130862 |
| 175 | $0.03 | 131591 |
| 176 | $0.04 | 133747 |
| 177 | $0.03 | 134392 |
| 178 | $0.03 | 135015 |
| 179 | $0.03 | 135350 |
| 180 | $0.04 | 136413 |
| 181 | $0.03 | 137160 |
| 182 | $0.03 | 137746 |
| 183 | $0.03 | 138084 |
| 184 | $0.03 | 138770 |
| 185 | $0.03 | 139357 |
| 186 | $0.03 | 140104 |
| 187 | $0.03 | 140506 |
| 188 | $0.03 | 141050 |
| 189 | $0.03 | 141380 |
| 190 | $0.03 | 142086 |
| 191 | $0.04 | 142981 |
| 192 | $0.04 | 143788 |
| 193 | $0.04 | 144596 |
| 194 | $0.04 | 145409 |
| 195 | $0.03 | 145868 |
| 196 | $0.04 | 146675 |
| 197 | $0.03 | 147132 |
| 198 | $0.04 | 147941 |
| 199 | $0.04 | 148940 |
| 200 | $0.04 | 149816 |
| 201 | $0.04 | 150550 |
| 202 | $0.03 | 151052 |
| 203 | $0.04 | 151725 |
| 204 | $0.04 | 152658 |
| 205 | $0.04 | 153298 |
| 206 | $0.03 | 153713 |
| 207 | $0.04 | 154489 |
| 208 | $0.03 | 154917 |
| 209 | $0.03 | 155229 |
| 210 | $0.03 | 155688 |
| 211 | $0.04 | 156481 |
| 212 | $0.04 | 158048 |
| 213 | $0.04 | 158854 |
| 214 | $0.04 | 159425 |
| 215 | $0.04 | 160371 |
| 216 | $0.03 | 160632 |
| 217 | $0.04 | 161242 |
| 218 | $0.04 | 162132 |
| 219 | $0.04 | 162774 |
| 220 | $0.04 | 163793 |
| 221 | $0.04 | 164136 |
| 222 | $0.04 | 165050 |
| 223 | $0.04 | 166185 |
| 224 | $0.04 | 166897 |
| 225 | $0.04 | 167244 |
| 226 | $0.04 | 168493 |
| 227 | $0.04 | 168842 |
| 228 | $0.04 | 169317 |
| 229 | $0.04 | 170106 |
| 230 | $0.04 | 170867 |
| 231 | $0.04 | 171663 |
| 232 | $0.04 | 172611 |
| 233 | $0.04 | 173619 |
| 234 | $0.04 | 174022 |
| 235 | $0.04 | 174585 |
| 236 | $0.04 | 174930 |
| 237 | $0.04 | 175264 |
| 238 | $0.04 | 175438 |
| 239 | $0.04 | 176242 |
| 240 | $0.05 | 177499 |
| 241 | $0.07 | 182262 |
| 242 | $0.04 | 182967 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 12 | 1 | 2 | 1185 | 0 | 34534 | 0.10 |
| red | 15 | 7 | 0 | 0 | 788 | 445 | 84 | 168 | 41291 | 2890463 | 497406 | 1.95 |
| green | 37 | 5 | 12 | 0 | 3427 | 802 | 189 | 378 | 66224 | 6085049 | 723813 | 4.27 |
| refactor | 6 | 1 | 0 | 0 | 134 | 62 | 18 | 36 | 3294 | 457884 | 154043 | 0.46 |
| red-missing | 3 | 0 | 0 | 0 | 149 | 93 | 14 | 28 | 10161 | 578532 | 152831 | 0.54 |
| pin | 4 | 4 | 0 | 0 | 106 | 71 | 14 | 28 | 4626 | 381804 | 91012 | 0.31 |
| exhausted | 2 | 0 | 0 | 0 | 54 | 33 | 6 | 12 | 2386 | 144604 | 48849 | 0.32 |
| prose | 6 | 0 | 0 | 0 | 345 | 329 | 6 | 12 | 50381 | 7478 | 354773 | 1.39 |
| skill-edit | 2 | 0 | 0 | 0 | 40 | 35 | 8 | 16 | 2840 | 601278 | 124313 | 0.40 |
| rebase | 2 | 1 | 0 | 0 | 249 | 58 | 14 | 26 | 2962 | 390572 | 53528 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 31 | 19 | 12 | 0 | 2470 | 510 | 113 | 226 | 42144 | 3300799 | 553737 | 2.14 |
| developer | claude-sonnet-5-5 | 28 | 0 | 0 | 0 | 1804 | 798 | 170 | 338 | 69910 | 5828705 | 912092 | 4.00 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 648 | 268 | 57 | 114 | 20075 | 1799404 | 290187 | 2.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 191 | 0.45 |
| green | 3034 | 3.49 | 1253 | 1.69 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 120 | 0.36 |
| pin | 0 | 0.00 | 57 | 0.13 |
| exhausted | 0 | 0.00 | 54 | 0.32 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `grade-prose.sh <requirements-file> <unit>`, run at the root of a tree that carries its own `skills/tdd/scripts/veri/grade_prose.py` whose `signature` formula differs from the running grader's, signs a PASS under the tree's own formula (the signature and GRADED line the tree's own grade_prose writes), so a tree whose own `skills/tdd/scripts/prose-owed.sh <root>` exits 0 before the grade still has it exit 0 after; a tree carrying no such module, or one whose formula agrees, is signed exactly as today. Pinned by a process case (stub claude, real git tree in tmp_path) that grades a unit on such a tree and reads the tree's prose-owed.sh exit; red on today's code ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 225 | 48 | 96 | 19525 | 1591602 | 227885 | 1.19 | 910 | 2/2 | 0/5 | nothing-left |  |  | full |
| When the tree at the grading root carries its own `skills/tdd/scripts/veri/grade_prose.py` but its signature for the unit cannot be obtained (the module fails to import, or its `signature` raises), a passing `grade-prose.sh <requirements-file> <unit>` writes no GRADED line and exits 2, its stderr naming the cause `signature-formula-disagreement`, the unit, and the running grader's signature beside what the tree's formula gave (or that it gave none); the usage line is unchanged ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 71 | 21 | 42 | 7191 | 648410 | 95413 | 0.38 | 280 | unknown | 0/5 | nothing-left |  |  | full |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's, leaves every other GRADED line byte-identical, and exits 0 (2 when the tree's formula cannot be obtained, naming the unit); a process case builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and after `--convert` the tree's own prose-owed.sh exits 0; the usage line is unchanged ⟦criterion 3⟧ | 12 | 2 | 3 | 0 | 0 | 0 | 275 | 56 | 112 | 27102 | 1882996 | 307135 | 1.56 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's, leaves every other GRADED line byte-identical, and exits 0 (2 when the tree's formula cannot be obtained, naming the unit); a process case builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and after `--convert` the tree's own prose-owed.sh exits 0; the usage line is unchanged; every guard the step adds is pinned by a case only it decides, among them, red first: `grade-prose.sh --convert` on a tree whose `grade_prose.signature` raises exits 2, its stderr names `signature-formula-disagreement` and the unit, and `GRADED` is left byte-identical ⟦criterion 3⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 194 | 44 | 88 | 15127 | 1397668 | 228072 | 1.09 | 860 | 2/2 | 0/5 | nothing-left |  |  | full |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's (the GRADED line the tree's own grade_prose writes), leaves every other GRADED line byte-identical, and exits 0; pinned by a process case that builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and reads the tree's own prose-owed.sh exit 0 after `--convert`, and by a case where a unit already valid under the tree's formula keeps its GRADED line byte-identical ⟦added⟧ ⟦criterion 3⟧ | 12 | 2 | 3 | 0 | 0 | 0 | 296 | 60 | 120 | 22450 | 1936990 | 271952 | 1.38 | unknown | 2/2 | unknown | unknown |  |  | already-satisfied |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's (the GRADED line the tree's own grade_prose writes), leaves every other GRADED line byte-identical, and exits 0; pinned by a process case that builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and reads the tree's own prose-owed.sh exit 0 after `--convert`, and by a case where a unit already valid under the tree's formula keeps its GRADED line byte-identical, and by a case only the per-unit guard in `resign` decides: two units in one directory with identical text and claims, both signed under the running formula, only one on `--convert`'s list — `--convert` re-signs the listed unit and leaves the unlisted unit's GRADED line byte-identical (red first, with the `fields[0] == unit` guard removed); every guard the step adds is pinned by a case only it decides ⟦added⟧ ⟦criterion 3⟧ | 13 | 4 | 2 | 0 | 0 | 0 | 275 | 61 | 122 | 25474 | 1971092 | 322509 | 1.50 | 1235 | 2/2 | 1/5 | nothing-structural |  |  | already-satisfied |
| skill-edit step for the unit `skills/tdd/SKILL.md`, pin file `skills/tdd/REQUIREMENTS.md`: the Draft PR step's regrade block, after grading the units the run signed, runs `$S/grade-prose.sh --convert` on the tree so a unit the default branch signed under a formula the branch replaces is re-signed under the tree's before the rebased tip's full suite, its exit folded into the block's highest exit code, and DP71's requirement says so; `skills/tdd/SKILL.md` grades PASS against its list and is re-signed in `skills/tdd/GRADED` inside this step ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 207 | 7 | 14 | 29182 | 525211 | 324552 | 1.16 | 244 | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/veri-merge/SKILL.md`, pin file `skills/veri-merge/REQUIREMENTS.md`: after the rebase and before the push, the merge runs `$S/grade-prose.sh --convert` at the worktree root and commits any GRADED line it rewrote, so the merged tree's `prose-owed.sh` exits 0 without a person recomputing a signature while reading a conflict, with a requirement row saying so; `skills/veri-merge/SKILL.md` grades PASS against its list and is re-signed in `skills/veri-merge/GRADED` inside this step ⟦skill-edit⟧ ⟦criterion 3⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 34 | 5 | 10 | 4736 | 81351 | 35795 | 0.15 | 66 | unknown | unknown | unknown |  |  | full |
| The one-snapshot invariant is pinned: `run-conductor.sh` runs the procedure from the commit in `.tdd/issue-<n>-skill-commit`, refuses with exit 2 a recorded commit the clone cannot resolve, and re-pins only under `VERI_NEW_SKILL=1`; a case pins each of the three ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 16 | 32 | 5584 | 569065 | 64431 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_grade_prose_process.py — test_2037_the_draft_pr_regrade_block_run_as_written_on_a_branch_that_signed_one_unit_exits_0 and test_2089_the_draft_pr_regrade_block_run_as_written_exits_with_the_highest_code_any_units_grading_returned[0,0-0] and [1,0-1] fail: the regrade block now exits 2 because `grade-prose.sh --convert` raises "FileNotFoundError: [Errno 2] No such file or directory: 'REQUIREMENTS.md'" on a tree with no root REQUIREMENTS.md ⟦suite-repair⟧ ⟦criterion 4⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 148 | 33 | 64 | 8491 | 931085 | 204085 | 0.69 | 761 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `grade-prose.sh <requirements-file> <unit>`, run at the root of a tree that carries its own `skills/tdd/scripts/veri/grade_prose.py` whose `signature` formula differs from the running grader's, signs a PASS under the tree's own formula (the signature and GRADED line the tree's own grade_prose writes), so a tree whose own `skills/tdd/scripts/prose-owed.sh <root>` exits 0 before the grade still has it exit 0 after; a tree carrying no such module, or one whose formula agrees, is signed exactly as today. Pinned by a process case (stub claude, real git tree in tmp_path) that grades a unit on such a tree and reads the tree's prose-owed.sh exit; red on today's code ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.09 |
| When the tree at the grading root carries its own `skills/tdd/scripts/veri/grade_prose.py` but its signature for the unit cannot be obtained (the module fails to import, or its `signature` raises), a passing `grade-prose.sh <requirements-file> <unit>` writes no GRADED line and exits 2, its stderr naming the cause `signature-formula-disagreement`, the unit, and the running grader's signature beside what the tree's formula gave (or that it gave none); the usage line is unchanged ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's, leaves every other GRADED line byte-identical, and exits 0 (2 when the tree's formula cannot be obtained, naming the unit); a process case builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and after `--convert` the tree's own prose-owed.sh exits 0; the usage line is unchanged; every guard the step adds is pinned by a case only it decides, among them, red first: `grade-prose.sh --convert` on a tree whose `grade_prose.signature` raises exits 2, its stderr names `signature-formula-disagreement` and the unit, and `GRADED` is left byte-identical ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 12 | 0.10 |
| `grade-prose.sh --convert`, run at a tree's root without launching any grader leaf, re-signs under the tree's own formula every listed unit whose committed GRADED signature is valid under the running grader's formula but not under the tree's (the GRADED line the tree's own grade_prose writes), leaves every other GRADED line byte-identical, and exits 0; pinned by a process case that builds a rebased branch in the #2474 shape (a unit's GRADED line landed on the default branch after the cut, under the old formula, while the branch changes the formula) and reads the tree's own prose-owed.sh exit 0 after `--convert`, and by a case where a unit already valid under the tree's formula keeps its GRADED line byte-identical, and by a case only the per-unit guard in `resign` decides: two units in one directory with identical text and claims, both signed under the running formula, only one on `--convert`'s list — `--convert` re-signs the listed unit and leaves the unlisted unit's GRADED line byte-identical (red first, with the `fields[0] == unit` guard removed); every guard the step adds is pinned by a case only it decides ⟦added⟧ ⟦criterion 3⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 106 | 0.13 |
| fix the full-suite failure: skills/tdd/scripts/tests/py/test_grade_prose_process.py — test_2037_the_draft_pr_regrade_block_run_as_written_on_a_branch_that_signed_one_unit_exits_0 and test_2089_the_draft_pr_regrade_block_run_as_written_exits_with_the_highest_code_any_units_grading_returned[0,0-0] and [1,0-1] fail: the regrade block now exits 2 because `grade-prose.sh --convert` raises "FileNotFoundError: [Errno 2] No such file or directory: 'REQUIREMENTS.md'" on a tree with no root REQUIREMENTS.md ⟦suite-repair⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 21 | 21 | 20 | 21 | 21 | 18 | 24 | 24 | 21 | 18 | 2 | 20 | 19 | 17 | 21 | 4 | 20 | 24 | 19 | 4 | 4 | 4 | 19 | 22 | 19 | 21 | 25 | 19 | 24 | 22 | 22 | 24 | 19 | 20 | 22 | 21 | 21 | 22 | 22 | 21 | 22 | 23 | 25 | 4 | 22 | 22 | 21 | 2 | 3 | 22 | 23 | 22 | 21 | 14 | 21 | 1 | 21 |
| fast | 17 | 16 | 16 | 17 | 17 | 16 | 16 | 16 | 17 | 17 | 17 | 17 | 17 | 16 | 17 | 18 | 17 | 19 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 16 | 17 | 17 | 17 | 17 | 17 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 20 | 21 | 3 | 5 | 5 | 5 | 5 | 5 | 4 | 4 | 3 | 5 | 23 | 3 | 4 | 5 | 22 | 22 | 3 | 3 | 4 | 2 | 2 | 20 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 184 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 354 | 706 | 185350 | 11537664 | 2235102 | 22.67 (estimate) |
