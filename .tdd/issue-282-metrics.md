### 📊 Metrics — issue 282

Wall time for the issue: 5187 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 2 of 7 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 9 | 4 | 0 | 0 | 2528 | 1177 | 113 | 218 | 90596 | 6076605 | 477156 | 8.17 |
| green | 16 | 2 | 5 | 0 | 17920 | 3395 | 386 | 754 | 255065 | 30922871 | 1114893 | 28.46 |
| x | 4 | 0 | 0 | 1 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0.00 |
| refactor | 4 | 2 | 0 | 0 | 1926 | 425 | 62 | 116 | 32007 | 3373185 | 207776 | 3.51 |
| pin | 1 | 1 | 0 | 0 | 158 | 60 | 12 | 24 | 4170 | 625290 | 37252 | 0.32 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 1979 | 4.69 |
| green | 0 | 0.00 | 15843 | 26.76 |
| x | 0 | 0.00 | 4 | 0.00 |
| refactor | 0 | 0.00 | 1058 | 2.05 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| supervise.sh on a sub-second clock: with fractional VERI_HEARTBEAT/VERI_TIMEOUT/VERI_POLL, a stub leaf that stops writing is killed as stuck and one that keeps writing is not ⟦criterion 3⟧ | 13 | 3 | 1 | 1 | 1 | 0 | 883 | 122 | 232 | 67634 | 6710119 | 412226 | 6.77 | unknown | 1/2 | unknown | unknown |
| wait-leaf.sh accepts a fractional VERI_POLL and returns the recorded code within tens of milliseconds of the completion file landing ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 217 | 24 | 48 | 16328 | 1246413 | 93626 | 1.50 | unknown | unknown | unknown | unknown |
| with no tunables set supervise.sh, wait-leaf.sh and verify.sh keep default heartbeat 180 s, poll 1 s, and a malformed tunable value is still exit 2 ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 683 | 83 | 160 | 47967 | 4684811 | 277719 | 5.46 | 3388 | unknown | 2/5 | structural-owed |
| verify.test.sh and supervise.test.sh run on the fast clock and together take at most 20 s, with no case removed and every assertion kept ⟦criterion 1⟧ | 8 | 1 | 3 | 0 | 0 | 0 | 2372 | 224 | 440 | 168995 | 19000426 | 666023 | 17.64 | unknown | 2/2 | unknown | unknown |
| verify.test.sh and supervise.test.sh run on the fast clock and together take at most 45 s on the CI runner, with no case removed and every assertion kept ⟦criterion 1⟧ | 5 | 1 | 1 | 0 | 0 | 0 | 902 | 120 | 232 | 80914 | 9356182 | 387483 | 9.09 | unknown | 1/2 | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 573 | 1112 | 381838 | 40997951 | 1837077 | 40.46 |
