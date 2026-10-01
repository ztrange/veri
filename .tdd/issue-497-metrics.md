### 📊 Metrics — issue 497

Wall time for the issue: 9703 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 5 of 23 planned.
Outcome: the run bailed — step-too-big, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 1 | 2 | 0 | 106 | 92 | 12 | 24 | 8071 | 481951 | 123914 | 1.25 |
| red | 18 | 7 | 1 | 0 | 2615 | 856 | 155 | 296 | 64748 | 7408315 | 842163 | 9.52 |
| green | 22 | 7 | 4 | 0 | 5277 | 843 | 192 | 380 | 74670 | 8966556 | 822128 | 9.87 |
| refactor | 12 | 5 | 0 | 0 | 927 | 343 | 74 | 148 | 26459 | 3314742 | 453291 | 5.45 |
| exhausted | 1 | 0 | 0 | 0 | 47 | 37 | 7 | 14 | 3656 | 328190 | 47418 | 0.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 2128 | 3.68 |
| green | 6073 | 8.75 | 1062 | 1.93 |
| refactor | 0 | 0.00 | 43 | 0.53 |
| exhausted | 0 | 0.00 | 47 | 0.52 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| lib/exit-contract.sh, sourced not run, provides refuse: it prints its message (if given) then the caller's $USAGE on stderr and exits 2 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 279 | 69 | 134 | 26725 | 3278449 | 320861 | 3.76 | 2258 | 1/2 | 1/5 | nothing-structural |  |  | full |
| lib/exit-contract.sh provides require_args <n> "$@": it refuses with the caller's $USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 194 | 36 | 74 | 13407 | 1629259 | 202520 | 2.84 | 560 | unknown | 1/5 | nothing-left |  |  | full |
| lib/exit-contract.sh provides to_contract <code>: it prints the code unchanged when it is 0, 1, 2 or 3 and prints 2 for any other code ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 137 | 40 | 76 | 12168 | 1642578 | 234953 | 2.45 | 265 | unknown | 0/5 | nothing-left |  |  | full |
| A script that sources lib/exit-contract.sh and then ends with a code outside 0–3 — a `set -e` abort on a failing command, or a last command's status — exits 2 instead, unless that exit is a declared pass-through ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 206 | 49 | 94 | 16488 | 2183786 | 251454 | 2.78 | 355 | unknown | 1/5 | nothing-left |  |  | full |
| A script that sources lib/exit-contract.sh can declare an exit a pass-through, and that exit hands on its code unmapped even when it is outside 0–3, while every undeclared exit outside 0–3 still ends as 2 ⟦added⟧ ⟦criterion 4⟧ | 15 | 5 | 2 | 0 | 0 | 0 | 587 | 126 | 248 | 49858 | 5925836 | 584473 | 6.86 | 2591 | 2/2 | 3/5 | nothing-left |  |  | full |
| The missing-argument audit finds its own subjects: every script whose source prints a usage line is called without its required arguments and must exit 2 with its own usage text on stderr, with no hand-kept roster ⟦criterion 2⟧ | 12 | 2 | 2 | 0 | 0 | 0 | 676 | 108 | 212 | 50887 | 5357895 | 570739 | 6.66 | unknown | green 1/2, red 2/2 | unknown | unknown |  | exhausted | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| lib/exit-contract.sh, sourced not run, provides refuse: it prints its message (if given) then the caller's $USAGE on stderr and exits 2 ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 292 | 0.82 |
| lib/exit-contract.sh provides require_args <n> "$@": it refuses with the caller's $USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 324 | 1.10 |
| lib/exit-contract.sh provides to_contract <code>: it prints the code unchanged when it is 0, 1, 2 or 3 and prints 2 for any other code ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.71 |
| A script that sources lib/exit-contract.sh and then ends with a code outside 0–3 — a `set -e` abort on a failing command, or a last command's status — exits 2 instead, unless that exit is a declared pass-through ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 73 | 0.84 |
| A script that sources lib/exit-contract.sh can declare an exit a pass-through, and that exit hands on its code unmapped even when it is outside 0–3, while every undeclared exit outside 0–3 still ends as 2 ⟦added⟧ ⟦criterion 4⟧ | 2 | 3/5 | nothing-left | PASS | 0 | 145 | 1.45 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 0 | 2 | 1 | 234 | 0 | 239 | 0 | 232 | 0 | 226 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 14 | 2 | 103 | 1 | 103 | 2 | 0 | 1 | 1 | 0 | 1 | 5 | 0 | 3 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 5 | 5 |
| fast | 12 | 13 | 13 | 12 | 12 | 12 | 11 | 12 | 12 | 12 | 13 | 13 | 13 | 12 | 12 | 13 | 13 | 14 | 13 | 13 | 13 | 13 | 13 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 814 | 827 | 833 | 826 | 855 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 440 | 862 | 177604 | 20499754 | 2288914 | 26.60 |
