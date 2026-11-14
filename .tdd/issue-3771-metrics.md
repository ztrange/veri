### 📊 Metrics — issue 3771

Wall time for the issue: 4288 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 26 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $12.77 over 237 turns, in 5 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80913 tokens, largest 155894 tokens
Conductor context: first turn 80913 tokens, largest 152210 tokens
Conductor context: first turn 80914 tokens, largest 145548 tokens
Conductor context: first turn 80939 tokens, largest 134734 tokens
Conductor context: first turn 135160 tokens, largest 197394 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.52 | 80913 |
| 2 | $0.09 | 87772 |
| 3 | $0.06 | 90634 |
| 4 | $0.03 | 90850 |
| 5 | $0.05 | 92892 |
| 6 | $0.04 | 93233 |
| 7 | $0.04 | 93707 |
| 8 | $0.04 | 93977 |
| 9 | $0.04 | 94279 |
| 10 | $0.04 | 94954 |
| 11 | $0.07 | 99748 |
| 12 | $0.07 | 103234 |
| 13 | $0.04 | 104655 |
| 14 | $0.07 | 107639 |
| 15 | $0.04 | 108544 |
| 16 | $0.08 | 113358 |
| 17 | $0.04 | 114272 |
| 18 | $0.05 | 114758 |
| 19 | $0.05 | 116167 |
| 20 | $0.05 | 117054 |
| 21 | $0.05 | 119452 |
| 22 | $0.11 | 127602 |
| 23 | $0.09 | 133571 |
| 24 | $0.07 | 137439 |
| 25 | $0.10 | 144282 |
| 26 | $0.05 | 145079 |
| 27 | $0.05 | 145599 |
| 28 | $0.05 | 145977 |
| 29 | $0.06 | 147165 |
| 30 | $0.05 | 147735 |
| 31 | $0.05 | 148235 |
| 32 | $0.05 | 148786 |
| 33 | $0.05 | 149775 |
| 34 | $0.06 | 150488 |
| 35 | $0.05 | 150914 |
| 36 | $0.04 | 151207 |
| 37 | $0.06 | 151778 |
| 38 | $0.05 | 152399 |
| 39 | $0.07 | 155061 |
| 40 | $0.05 | 155536 |
| 41 | $0.05 | 155894 |
| 42 | $0.52 | 80913 |
| 43 | $0.08 | 87776 |
| 44 | $0.05 | 90554 |
| 45 | $0.04 | 92664 |
| 46 | $0.05 | 94317 |
| 47 | $0.08 | 101321 |
| 48 | $0.04 | 101783 |
| 49 | $0.03 | 102066 |
| 50 | $0.03 | 102287 |
| 51 | $0.04 | 102947 |
| 52 | $0.07 | 107425 |
| 53 | $0.03 | 107956 |
| 54 | $0.05 | 109111 |
| 55 | $0.04 | 110498 |
| 56 | $0.04 | 110955 |
| 57 | $0.03 | 111403 |
| 58 | $0.04 | 111672 |
| 59 | $0.04 | 112351 |
| 60 | $0.04 | 114048 |
| 61 | $0.04 | 115140 |
| 62 | $0.04 | 115430 |
| 63 | $0.04 | 116077 |
| 64 | $0.04 | 116466 |
| 65 | $0.04 | 117056 |
| 66 | $0.04 | 117762 |
| 67 | $0.04 | 118545 |
| 68 | $0.03 | 119026 |
| 69 | $0.04 | 119517 |
| 70 | $0.04 | 119815 |
| 71 | $0.04 | 120292 |
| 72 | $0.04 | 120638 |
| 73 | $0.04 | 121343 |
| 74 | $0.03 | 121726 |
| 75 | $0.05 | 122433 |
| 76 | $0.03 | 122887 |
| 77 | $0.04 | 123280 |
| 78 | $0.09 | 130237 |
| 79 | $0.04 | 130736 |
| 80 | $0.04 | 130880 |
| 81 | $0.05 | 131661 |
| 82 | $0.11 | 140834 |
| 83 | $0.05 | 143082 |
| 84 | $0.05 | 144340 |
| 85 | $0.05 | 145417 |
| 86 | $0.05 | 146577 |
| 87 | $0.05 | 147717 |
| 88 | $0.04 | 148472 |
| 89 | $0.05 | 148839 |
| 90 | $0.06 | 151337 |
| 91 | $0.04 | 151740 |
| 92 | $0.05 | 152210 |
| 93 | $0.52 | 80914 |
| 94 | $0.08 | 87777 |
| 95 | $0.05 | 90532 |
| 96 | $0.05 | 92601 |
| 97 | $0.09 | 100711 |
| 98 | $0.07 | 105425 |
| 99 | $0.04 | 105852 |
| 100 | $0.03 | 106140 |
| 101 | $0.04 | 106361 |
| 102 | $0.04 | 107077 |
| 103 | $0.03 | 107774 |
| 104 | $0.04 | 108171 |
| 105 | $0.04 | 109196 |
| 106 | $0.04 | 109424 |
| 107 | $0.04 | 110283 |
| 108 | $0.04 | 111667 |
| 109 | $0.04 | 111957 |
| 110 | $0.04 | 112677 |
| 111 | $0.11 | 122031 |
| 112 | $0.04 | 122852 |
| 113 | $0.04 | 123269 |
| 114 | $0.04 | 123541 |
| 115 | $0.04 | 123963 |
| 116 | $0.04 | 124830 |
| 117 | $0.04 | 125695 |
| 118 | $0.04 | 126124 |
| 119 | $0.05 | 126803 |
| 120 | $0.04 | 127128 |
| 121 | $0.04 | 127967 |
| 122 | $0.04 | 128869 |
| 123 | $0.05 | 129486 |
| 124 | $0.04 | 129930 |
| 125 | $0.04 | 130729 |
| 126 | $0.05 | 132433 |
| 127 | $0.08 | 137599 |
| 128 | $0.05 | 138382 |
| 129 | $0.04 | 138694 |
| 130 | $0.04 | 139353 |
| 131 | $0.05 | 139926 |
| 132 | $0.04 | 140741 |
| 133 | $0.05 | 141560 |
| 134 | $0.06 | 144164 |
| 135 | $0.05 | 144811 |
| 136 | $0.04 | 145093 |
| 137 | $0.04 | 145548 |
| 138 | $0.52 | 80939 |
| 139 | $0.08 | 87800 |
| 140 | $0.05 | 90499 |
| 141 | $0.03 | 90957 |
| 142 | $0.10 | 99309 |
| 143 | $0.03 | 100149 |
| 144 | $0.03 | 100797 |
| 145 | $0.04 | 101274 |
| 146 | $0.03 | 101645 |
| 147 | $0.03 | 102309 |
| 148 | $0.07 | 106939 |
| 149 | $0.04 | 107764 |
| 150 | $0.03 | 108239 |
| 151 | $0.03 | 108896 |
| 152 | $0.04 | 109362 |
| 153 | $0.03 | 109854 |
| 154 | $0.04 | 111212 |
| 155 | $0.04 | 112064 |
| 156 | $0.04 | 112942 |
| 157 | $0.04 | 113990 |
| 158 | $0.04 | 114646 |
| 159 | $0.03 | 115590 |
| 160 | $0.04 | 116610 |
| 161 | $0.11 | 126002 |
| 162 | $0.04 | 126399 |
| 163 | $0.04 | 127829 |
| 164 | $0.04 | 128588 |
| 165 | $0.04 | 129361 |
| 166 | $0.05 | 130152 |
| 167 | $0.04 | 131227 |
| 168 | $0.06 | 134408 |
| 169 | $0.04 | 134734 |
| 170 | $0.03 | 135160 |
| 171 | $0.03 | 135953 |
| 172 | $0.03 | 136711 |
| 173 | $0.03 | 137205 |
| 174 | $0.03 | 138086 |
| 175 | $0.03 | 138614 |
| 176 | $0.03 | 139162 |
| 177 | $0.04 | 140315 |
| 178 | $0.03 | 141043 |
| 179 | $0.04 | 142477 |
| 180 | $0.03 | 143163 |
| 181 | $0.03 | 143710 |
| 182 | $0.03 | 144170 |
| 183 | $0.04 | 145103 |
| 184 | $0.04 | 146202 |
| 185 | $0.03 | 146631 |
| 186 | $0.04 | 147890 |
| 187 | $0.04 | 148688 |
| 188 | $0.04 | 149421 |
| 189 | $0.04 | 150244 |
| 190 | $0.03 | 150710 |
| 191 | $0.04 | 151791 |
| 192 | $0.04 | 153257 |
| 193 | $0.04 | 153971 |
| 194 | $0.04 | 154929 |
| 195 | $0.05 | 157058 |
| 196 | $0.04 | 157836 |
| 197 | $0.04 | 158666 |
| 198 | $0.04 | 159416 |
| 199 | $0.04 | 160586 |
| 200 | $0.05 | 162424 |
| 201 | $0.04 | 162843 |
| 202 | $0.04 | 164046 |
| 203 | $0.04 | 164332 |
| 204 | $0.07 | 168854 |
| 205 | $0.04 | 169129 |
| 206 | $0.04 | 169755 |
| 207 | $0.05 | 171169 |
| 208 | $0.04 | 172111 |
| 209 | $0.04 | 172446 |
| 210 | $0.04 | 172767 |
| 211 | $0.04 | 173096 |
| 212 | $0.04 | 173657 |
| 213 | $0.05 | 175195 |
| 214 | $0.04 | 175725 |
| 215 | $0.04 | 175999 |
| 216 | $0.04 | 176664 |
| 217 | $0.04 | 177699 |
| 218 | $0.05 | 179027 |
| 219 | $0.05 | 180368 |
| 220 | $0.04 | 180679 |
| 221 | $0.04 | 181023 |
| 222 | $0.05 | 182172 |
| 223 | $0.05 | 183674 |
| 224 | $0.05 | 185343 |
| 225 | $0.04 | 186140 |
| 226 | $0.04 | 186861 |
| 227 | $0.04 | 187062 |
| 228 | $0.05 | 188279 |
| 229 | $0.05 | 189425 |
| 230 | $0.04 | 189631 |
| 231 | $0.04 | 190081 |
| 232 | $0.05 | 191184 |
| 233 | $0.04 | 191647 |
| 234 | $0.04 | 192248 |
| 235 | $0.08 | 197394 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 2 | 24 | $0.00 |
| 🛠️ Refactor | 0 | 0 | $0.00 |
| 🔎 verify-green | 0 | 0 | $0.00 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 2 | 24 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 4 | 4 | 0 | 0 | 85 | 73 | 13 | 26 | 9081 | 277190 | 115417 | 0.41 |
| prose | 4 | 0 | 0 | 0 | 107 | 99 | 4 | 8 | 16138 | 60317 | 243561 | 0.78 |
| skill-edit | 1 | 0 | 0 | 0 | 12 | 10 | 3 | 6 | 1006 | 199556 | 100592 | 0.28 |
| red | 28 | 14 | 1 | 0 | 1238 | 396 | 123 | 236 | 46080 | 2226674 | 545936 | 2.36 |
| green | 28 | 10 | 1 | 0 | 2717 | 382 | 137 | 258 | 45339 | 2628021 | 509392 | 2.20 |
| refactor | 13 | 3 | 0 | 0 | 332 | 80 | 42 | 72 | 8247 | 544315 | 236404 | 0.73 |
| red-repair | 1 | 0 | 0 | 0 | 22 | 15 | 6 | 10 | 2042 | 98926 | 20128 | 0.08 |
| red-contradicted | 1 | 0 | 0 | 0 | 40 | 24 | 7 | 12 | 3550 | 129136 | 22561 | 0.10 |
| exhausted | 1 | 0 | 0 | 0 | 130 | 10 | 3 | 6 | 1010 | 44126 | 14898 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 33 | 31 | 2 | 0 | 2825 | 377 | 124 | 242 | 41470 | 2257885 | 619482 | 2.19 |
| developer | claude-sonnet-5-5 | 31 | 0 | 0 | 0 | 965 | 362 | 135 | 244 | 46327 | 2239838 | 598197 | 2.18 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 774 | 241 | 72 | 134 | 27552 | 1450665 | 247057 | 1.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 178 | 0.41 | 331 | 0.81 |
| green | 420 | 0.32 | 479 | 0.62 |
| refactor | 0 | 0.00 | 56 | 0.11 |
| red-repair | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 40 | 0.10 |
| exhausted | 0 | 0.00 | 130 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md`: a catalogue bullet for `$S/preflight.sh <n> <slug>` meeting the issue's SC row: its two arguments; the per-call output (one line naming the call and its exit code, then that call's stdout and stderr unchanged); the `stopped at <step> <call>` last line, `<step>` being `PREFLIGHT.md`'s step number; the `waiting on <name>` last line; the `.tdd/issue-<n>-preflight` file written on exit 0 in the run's worktree, one `key=value` per line, keys `worktree`, `fast_cmd`, `full_cmd`, `alone_cmd`, `baseline`, `full`, `full_tier_mode`, `default_branch`, `model_develop_red`, `model_revise_green`, `model_verify_green`, `timeout`, printed again as its last lines; exit codes 0 every call clean, 3 a wait's slice ran out (call it again), 2 a branch that already holds a ledger (and bad arguments), otherwise the stopping call's own code ⟦criterion 17⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 109 | 7 | 14 | 17144 | 259873 | 344153 | 1.06 | 145 | unknown | unknown | unknown |  |  | full |
| `preflight.sh` run with no arguments exits 2, prints a usage line naming `preflight.sh <n> <slug>` on stderr and makes no inner call; the step adds the `/bin/sh` shim `skills/tdd/scripts/preflight.sh` over a new module `skills/tdd/scripts/veri/preflight.py` by the ported-script convention (`status.sh` the worked example) (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) | 5 | 2 | 0 | 0 | 0 | 0 | 50 | 23 | 42 | 6081 | 392653 | 99671 | 0.35 | 304 | unknown | 0/5 | nothing-left |  |  | full |
| On a fresh run with every inner call faked clean, `preflight.sh <n> <slug>` makes PREFLIGHT.md's step 1 to 3 front calls in this order: `git rev-parse --is-inside-work-tree`, `git status --porcelain`, `gh api user`, `claude auth status`, `leaf-launchable.sh`, `issue-worktree.sh <n> <slug>` (the slug taken verbatim from its argument, never derived), `stop-requested.sh --clear` run in the worktree `issue-worktree.sh` printed (with `.tdd/ci-conflict-rebased` removed there), then the claim `unlabel-issue.sh <n>` (SKILL.md 1.6's slot, before any baseline); every call after `issue-worktree.sh` runs with that worktree as its cwd; the module keeps an ordered list of PREFLIGHT.md's numbered steps (1 to 7) that its calls are grouped under (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 111 | 32 | 62 | 12752 | 597546 | 131523 | 0.64 | 1048 | 1/2 | 0/5 | nothing-left |  |  | full |
| For every inner call it makes, `preflight.sh` prints, in call order, one line naming the call and its exit code, followed by exactly what that call wrote to stdout and to stderr, unchanged (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 58 | 19 | 36 | 6832 | 317057 | 93461 | 0.33 | 520 | unknown | 0/5 | nothing-left |  |  | full |
| When `leaf-launchable.sh` exits 1, `preflight.sh` makes no later call (no `issue-worktree.sh`, no `unlabel-issue.sh`), exits 1, and its last stdout line is `stopped at 2 leaf-launchable.sh` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 42 | 18 | 32 | 4909 | 272108 | 91631 | 0.31 | 396 | unknown | 0/5 | nothing-left |  |  | full |
| When `git status --porcelain` exits 0 but prints a path (a dirty caller's checkout), `preflight.sh` makes no later call (no `gh api user`), exits 1, and its last stdout line is `stopped at 1 git status --porcelain` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 59 | 23 | 44 | 6521 | 383130 | 108795 | 0.38 | unknown | unknown | 1/5 | nothing-left |  |  | full |
| When `claude auth status` exits 0 but its JSON reports `"loggedIn": false`, `preflight.sh` makes no later call (no `leaf-launchable.sh`), exits 1, and its last stdout line is `stopped at 2 claude auth status` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 67 | 26 | 50 | 7321 | 443612 | 128840 | 0.52 | 983 | 1/2 | 0/5 | nothing-left |  |  | full |
| Run for an issue whose branch already holds a ledger (the issue's run worktree already holds `.tdd/issue-<n>.md`), `preflight.sh <n> <slug>` exits 2 before any inner call (the spy records none) and names the resume path (`RESUME.md`) on stderr (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 11⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 21 | 40 | 5783 | 358405 | 98807 | 0.34 | 476 | unknown | 0/5 | nothing-left |  |  | full |
| After the claim, with every inner call faked clean and `baseline-full-tier.sh` printing `run`, `preflight.sh` makes PREFLIGHT.md step 3's remaining calls in the worktree in this order: `worktree-setup.sh <n>` (its exit 3 goes on), the issue body read `gh api repos/{owner}/{repo}/issues/<n> -q .body` into a temp file outside the worktree, `requirements-preflight.sh <body-file>`, `detect-test-command.sh --tier fast --issue <body-file> <worktree>`, `detach-command.sh start <name> <fast-cmd>` then `detach-command.sh wait <name>` with `VERI_ISSUE=<n>` and no `--alone`, `detect-test-command.sh --tier all --issue <body-file> <worktree>`, `baseline-full-tier.sh <n> <full-cmd>`, then the full tier's `detach-command.sh start` and `wait` (no `--alone`), then `full-tier-time.sh --record <seconds> <full-cmd>` for the green full tier (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 136 | 46 | 86 | 17279 | 883436 | 151451 | 0.64 | 690 | 0/? | 1/5 | nothing-left |  |  | full |
| When the baseline's `detach-command.sh wait` exits 1 (a red baseline), `preflight.sh` exits 1 with last stdout line `stopped at 3 detach-command.sh wait`, makes no later call, re-runs no failing test alone and writes no `suite-flake` event (no `event.sh` call, no `--alone` on the wait); the flake judgement stays the conductor's (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 12⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 60 | 21 | 42 | 7186 | 361608 | 109684 | 0.38 | 543 | unknown | 1/5 | nothing-left |  |  | full |
| When the baseline's `detach-command.sh wait` exits 3 (its slice ran out), `preflight.sh` makes no later call, exits 3, and its last stdout line is `waiting on <name>`, the detached run's name (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 6⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 45 | 18 | 32 | 5485 | 272573 | 98468 | 0.33 | 509 | unknown | 0/5 | nothing-left |  |  | full |
| After the full tier, with every inner call faked clean, `preflight.sh` makes PREFLIGHT.md steps 4 to 7 in this order and then exits 0: `gh api repos/{owner}/{repo} -q .default_branch`, `refactor-budget.sh 0` and `refactor-budget.sh --issue 0` (each exit 0 or 3 goes on), `step-budget.sh`, `adjudicate.sh --check-budget`, `leaf-model.sh develop-red`, `leaf-model.sh revise-green`, `leaf-model.sh verify-green`, `leaf-timeout.sh <baseline> --full <full>`, `<baseline>` and `<full>` being the elapsed whole seconds (rounded up) of the two tier runs read from an injected clock (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 12 | 3 | 0 | 0 | 0 | 0 | 228 | 71 | 128 | 26119 | 1389070 | 236988 | 1.38 | unknown | red 1/2, green 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `preflight.sh` run with no arguments exits 2, prints a usage line naming `preflight.sh <n> <slug>` on stderr and makes no inner call; the step adds the `/bin/sh` shim `skills/tdd/scripts/preflight.sh` over a new module `skills/tdd/scripts/veri/preflight.py` by the ported-script convention (`status.sh` the worked example) (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| On a fresh run with every inner call faked clean, `preflight.sh <n> <slug>` makes PREFLIGHT.md's step 1 to 3 front calls in this order: `git rev-parse --is-inside-work-tree`, `git status --porcelain`, `gh api user`, `claude auth status`, `leaf-launchable.sh`, `issue-worktree.sh <n> <slug>` (the slug taken verbatim from its argument, never derived), `stop-requested.sh --clear` run in the worktree `issue-worktree.sh` printed (with `.tdd/ci-conflict-rebased` removed there), then the claim `unlabel-issue.sh <n>` (SKILL.md 1.6's slot, before any baseline); every call after `issue-worktree.sh` runs with that worktree as its cwd; the module keeps an ordered list of PREFLIGHT.md's numbered steps (1 to 7) that its calls are grouped under (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.06 |
| For every inner call it makes, `preflight.sh` prints, in call order, one line naming the call and its exit code, followed by exactly what that call wrote to stdout and to stderr, unchanged (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| When `leaf-launchable.sh` exits 1, `preflight.sh` makes no later call (no `issue-worktree.sh`, no `unlabel-issue.sh`), exits 1, and its last stdout line is `stopped at 2 leaf-launchable.sh` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |
| When `git status --porcelain` exits 0 but prints a path (a dirty caller's checkout), `preflight.sh` makes no later call (no `gh api user`), exits 1, and its last stdout line is `stopped at 1 git status --porcelain` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 56 | 0.11 |
| When `claude auth status` exits 0 but its JSON reports `"loggedIn": false`, `preflight.sh` makes no later call (no `leaf-launchable.sh`), exits 1, and its last stdout line is `stopped at 2 claude auth status` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.07 |
| Run for an issue whose branch already holds a ledger (the issue's run worktree already holds `.tdd/issue-<n>.md`), `preflight.sh <n> <slug>` exits 2 before any inner call (the spy records none) and names the resume path (`RESUME.md`) on stderr (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 11⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |
| After the claim, with every inner call faked clean and `baseline-full-tier.sh` printing `run`, `preflight.sh` makes PREFLIGHT.md step 3's remaining calls in the worktree in this order: `worktree-setup.sh <n>` (its exit 3 goes on), the issue body read `gh api repos/{owner}/{repo}/issues/<n> -q .body` into a temp file outside the worktree, `requirements-preflight.sh <body-file>`, `detect-test-command.sh --tier fast --issue <body-file> <worktree>`, `detach-command.sh start <name> <fast-cmd>` then `detach-command.sh wait <name>` with `VERI_ISSUE=<n>` and no `--alone`, `detect-test-command.sh --tier all --issue <body-file> <worktree>`, `baseline-full-tier.sh <n> <full-cmd>`, then the full tier's `detach-command.sh start` and `wait` (no `--alone`), then `full-tier-time.sh --record <seconds> <full-cmd>` for the green full tier (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 111 | 0.11 |
| When the baseline's `detach-command.sh wait` exits 1 (a red baseline), `preflight.sh` exits 1 with last stdout line `stopped at 3 detach-command.sh wait`, makes no later call, re-runs no failing test alone and writes no `suite-flake` event (no `event.sh` call, no `--alone` on the wait); the flake judgement stays the conductor's (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 12⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 116 | 0.11 |
| When the baseline's `detach-command.sh wait` exits 3 (its slice ran out), `preflight.sh` makes no later call, exits 3, and its last stdout line is `waiting on <name>`, the detached run's name (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 6⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.06 |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `preflight.sh` run with no arguments exits 2, prints a usage line naming `preflight.sh <n> <slug>` on stderr and makes no inner call; the step adds the `/bin/sh` shim `skills/tdd/scripts/preflight.sh` over a new module `skills/tdd/scripts/veri/preflight.py` by the ported-script convention (`status.sh` the worked example) (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) | 1 | 0 | 1 | nothing-left 1 |
| On a fresh run with every inner call faked clean, `preflight.sh <n> <slug>` makes PREFLIGHT.md's step 1 to 3 front calls in this order: `git rev-parse --is-inside-work-tree`, `git status --porcelain`, `gh api user`, `claude auth status`, `leaf-launchable.sh`, `issue-worktree.sh <n> <slug>` (the slug taken verbatim from its argument, never derived), `stop-requested.sh --clear` run in the worktree `issue-worktree.sh` printed (with `.tdd/ci-conflict-rebased` removed there), then the claim `unlabel-issue.sh <n>` (SKILL.md 1.6's slot, before any baseline); every call after `issue-worktree.sh` runs with that worktree as its cwd; the module keeps an ordered list of PREFLIGHT.md's numbered steps (1 to 7) that its calls are grouped under (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| For every inner call it makes, `preflight.sh` prints, in call order, one line naming the call and its exit code, followed by exactly what that call wrote to stdout and to stderr, unchanged (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| When `leaf-launchable.sh` exits 1, `preflight.sh` makes no later call (no `issue-worktree.sh`, no `unlabel-issue.sh`), exits 1, and its last stdout line is `stopped at 2 leaf-launchable.sh` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 4⟧ | 1 | 0 | 1 | nothing-left 1 |
| When `git status --porcelain` exits 0 but prints a path (a dirty caller's checkout), `preflight.sh` makes no later call (no `gh api user`), exits 1, and its last stdout line is `stopped at 1 git status --porcelain` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 1 | 0 | nothing-left 1 |
| When `claude auth status` exits 0 but its JSON reports `"loggedIn": false`, `preflight.sh` makes no later call (no `leaf-launchable.sh`), exits 1, and its last stdout line is `stopped at 2 claude auth status` (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| Run for an issue whose branch already holds a ledger (the issue's run worktree already holds `.tdd/issue-<n>.md`), `preflight.sh <n> <slug>` exits 2 before any inner call (the spy records none) and names the resume path (`RESUME.md`) on stderr (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 11⟧ | 1 | 0 | 1 | nothing-left 1 |
| After the claim, with every inner call faked clean and `baseline-full-tier.sh` printing `run`, `preflight.sh` makes PREFLIGHT.md step 3's remaining calls in the worktree in this order: `worktree-setup.sh <n>` (its exit 3 goes on), the issue body read `gh api repos/{owner}/{repo}/issues/<n> -q .body` into a temp file outside the worktree, `requirements-preflight.sh <body-file>`, `detect-test-command.sh --tier fast --issue <body-file> <worktree>`, `detach-command.sh start <name> <fast-cmd>` then `detach-command.sh wait <name>` with `VERI_ISSUE=<n>` and no `--alone`, `detect-test-command.sh --tier all --issue <body-file> <worktree>`, `baseline-full-tier.sh <n> <full-cmd>`, then the full tier's `detach-command.sh start` and `wait` (no `--alone`), then `full-tier-time.sh --record <seconds> <full-cmd>` for the green full tier (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 1⟧ | 1 | 1 | 0 | nothing-left 1 |
| When the baseline's `detach-command.sh wait` exits 1 (a red baseline), `preflight.sh` exits 1 with last stdout line `stopped at 3 detach-command.sh wait`, makes no later call, re-runs no failing test alone and writes no `suite-flake` event (no `event.sh` call, no `--alone` on the wait); the flake judgement stays the conductor's (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 12⟧ | 1 | 1 | 0 | nothing-left 1 |
| When the baseline's `detach-command.sh wait` exits 3 (its slice ran out), `preflight.sh` makes no later call, exits 3, and its last stdout line is `waiting on <name>`, the detached run's name (a small unit case in skills/tdd/scripts/tests/py/unit/test_preflight.py driven in-process with run_cli, every inner call made through the one wrapper `veri/preflight.py` calls them by and faked there by an in-process spy that records each call and answers its exit code, stdout and stderr; no real git, gh, claude, suite or clock) ⟦criterion 6⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 10 | 3 | 7 | nothing-left 10 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 2 | 3 | 4 | 3 | 3 | 4 | 5 | 3 | 3 | 3 | 4 | 7 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 3 | 3 | 4 | 5 | 7 | 6 | 5 | 4 | 5 | 5 | 10 | 3 | 4 | 4 | 3 | 5 | 10 | 6 | 5 | 3 | 9 | 5 | 7 | 5 | 9 | 6 | 8 | 9 | 9 | 5 | 4 | 6 | 6 | 5 | 5 | 6 | 4 | 7 |
| fast | 0 | 22 | 21 | 23 | 23 | 29 | 25 | 23 | 25 | 24 | 25 | 26 | 26 | 42 | 46 | 30 | 32 | 51 | 40 | 27 | 29 | 73 | 44 | 65 | 75 | 58 | 76 | 65 | 34 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 4 | 3 | 4 | 6 | 4 | 6 | 3 | 7 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 338 | 634 | 132493 | 6208261 | 1808889 | 19.82 (estimate) |
