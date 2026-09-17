### 📊 Metrics — issue 219

Wall time for the issue: 18431 s, from the first event of the log to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/259.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 17 | 7 | 0 | 0 | 1665 | 686 | 134 | 256 | 61567 | 6278228 | 753222 | 9.42 |
| green | 14 | 7 | 0 | 0 | 7962 | 594 | 155 | 296 | 46101 | 7973368 | 611866 | 6.98 |
| refactor | 17 | 7 | 1 | 0 | 6029 | 746 | 167 | 334 | 58316 | 9294586 | 720251 | 8.11 |
| pin | 3 | 3 | 0 | 0 | 696 | 144 | 39 | 74 | 9175 | 2113725 | 128606 | 1.04 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 1469 | 2.37 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| verify.sh relaunches a verifier leaf that exited without being killed and printed no VERDICT: line, and returns the relaunched attempt's verdict (stub prints no verdict first, VERDICT: PASS second → exit 0, two launches) | 6 | 3 | 0 | 0 | 0 | 282 | 59 | 112 | 19791 | 3038061 | 262945 | 2.85 | 1611 | unknown | 0/5 | nothing-left |
| no-verdict relaunches stop after VERI_NO_VERDICT_RETRIES (default 1): a stub that never prints a verdict yields exit 2 after exactly 1 + VERI_NO_VERDICT_RETRIES launches, and VERI_NO_VERDICT_RETRIES=0 yields exit 2 after one launch | 6 | 3 | 0 | 0 | 0 | 223 | 51 | 102 | 17207 | 2686170 | 256868 | 2.77 | 1816 | unknown | 1/5 | triage |
| a non-integer VERI_NO_VERDICT_RETRIES makes verify.sh exit 2 without launching any verifier leaf | 5 | 3 | 0 | 0 | 0 | 193 | 43 | 84 | 13554 | 2130454 | 205749 | 2.09 | 1839 | unknown | 1/5 | triage |
| a verifier killed by supervise.sh (exit 2, stuck or hard timeout) is not relaunched by verify.sh: exit 2 after supervise.sh's own attempts, whatever VERI_NO_VERDICT_RETRIES is | 3 | 1 | 0 | 0 | 0 | 109 | 28 | 54 | 9360 | 1337031 | 128121 | 1.73 | unknown | unknown | unknown | unknown |
| VERI_STUCK_RETRIES does not change the no-verdict relaunch count, and VERI_NO_VERDICT_RETRIES does not change supervise.sh's stuck retry count | 2 | 1 | 0 | 0 | 0 | 68 | 20 | 36 | 6837 | 956649 | 91113 | 1.06 | unknown | unknown | unknown | unknown |
| a clean exit with no VERDICT: line is recorded in the event log under a cause distinct from a leaf killed before rendering one, on each relaunch and on the final exit 2 | 5 | 3 | 0 | 0 | 0 | 222 | 49 | 94 | 17158 | 2586036 | 244378 | 2.61 | 2302 | unknown | 2/5 | triage |
| metrics.sh reports no-verdict relaunches per run as their own count, distinct from retries and revise | 8 | 3 | 1 | 0 | 0 | 423 | 96 | 188 | 34314 | 5371000 | 389705 | 4.67 | 2353 | 1/2 | 1/5 | nothing-left |
| a relaunch's verifier prompt is byte-identical to the first attempt's, and build-verify-prompt.sh gains no parameter | 3 | 1 | 0 | 0 | 0 | 127 | 26 | 50 | 9332 | 1297410 | 127032 | 1.60 | unknown | unknown | unknown | unknown |
| SKILL.md's exit-2 branch says a clean exit with no verdict is relaunched rather than bailed, and a new ADR docs/adr/0020-*.md records it, naming ADR-0011 and SKILL.md's exit-2 branch as what it narrows | 6 | 3 | 0 | 0 | 0 | 267 | 62 | 122 | 24759 | 3435783 | 226151 | 2.72 | 3597 | unknown | 1/5 | triage |
| CLAUDE.md's budgets invariant names VERI_NO_VERDICT_RETRIES as a fourth axis and why it is not merged with VERI_STUCK_RETRIES | 7 | 3 | 0 | 0 | 0 | 256 | 61 | 118 | 22847 | 2821313 | 281883 | 3.47 | 1967 | unknown | 1/5 | triage |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 495 | 960 | 175159 | 25659907 | 2213945 | 25.55 |
