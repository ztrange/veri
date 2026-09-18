### 📊 Metrics — issue 276

Wall time for the issue: 23965 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/303.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 10 | 5 | 0 | 0 | 633 | 409 | 79 | 152 | 31201 | 3546752 | 395886 | 4.75 |
| green | 11 | 5 | 0 | 0 | 17341 | 691 | 155 | 302 | 44225 | 8139264 | 471557 | 6.76 |
| refactor | 11 | 5 | 0 | 0 | 5412 | 468 | 115 | 226 | 34347 | 6161049 | 462733 | 4.82 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A leaf launched through run-leaf.sh that runs `git config --global <key> <value>` leaves the operator's global config byte-identical, and the leaf reads the value back ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 394 | 69 | 130 | 25065 | 3369587 | 244126 | 3.44 | 5261 | unknown | 0/5 | nothing-left |
| The leaf's private global config starts as a copy of the operator's, so a key already present there is visible to the leaf ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 42 | 80 | 13704 | 1821638 | 222331 | 2.35 | 2838 | unknown | 1/5 | nothing-structural |
| verify.sh exits 2 naming the file when the operator's global git config changed between a verifier's launch and its exit ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 296 | 74 | 146 | 23231 | 3805976 | 270512 | 3.71 | 6372 | unknown | 1/5 | nothing-left |
| prompts/_shared.md forbids changing global or user-level configuration and names environment variables and throwaway directories as the way to simulate conditions ⟦criterion 4⟧ | 7 | 3 | 0 | 0 | 0 | 1 | 336 | 73 | 146 | 21648 | 3868949 | 271011 | 3.17 | 3470 | unknown | 0/5 | nothing-left |
| prompts/_develop-shared.md carries the same prohibition, so developer leaves — whose reach is the same — are told it too | 7 | 3 | 0 | 0 | 0 | 1 | 364 | 91 | 178 | 26125 | 4980915 | 322196 | 3.67 | 5980 | unknown | 0/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 349 | 680 | 109773 | 17847065 | 1330176 | 16.34 |
