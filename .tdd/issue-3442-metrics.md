### 📊 Metrics — issue 3442

Wall time for the issue: 1471 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.66 over 56 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80148 tokens, largest 174642 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.50 | 80148 |
| 2 | $0.07 | 86620 |
| 3 | $0.03 | 88014 |
| 4 | $0.03 | 90021 |
| 5 | $0.02 | 90330 |
| 6 | $0.02 | 90784 |
| 7 | $0.02 | 91052 |
| 8 | $0.02 | 91367 |
| 9 | $0.02 | 91944 |
| 10 | $0.07 | 98659 |
| 11 | $0.02 | 99064 |
| 12 | $0.02 | 99647 |
| 13 | $0.03 | 101459 |
| 14 | $0.03 | 102252 |
| 15 | $0.02 | 102677 |
| 16 | $0.03 | 103529 |
| 17 | $0.03 | 104785 |
| 18 | $0.04 | 106981 |
| 19 | $0.04 | 109046 |
| 20 | $0.03 | 110428 |
| 21 | $0.03 | 110987 |
| 22 | $0.03 | 111610 |
| 23 | $0.03 | 112488 |
| 24 | $0.11 | 124049 |
| 25 | $0.03 | 125015 |
| 26 | $0.03 | 125854 |
| 27 | $0.04 | 127521 |
| 28 | $0.05 | 130626 |
| 29 | $0.03 | 131473 |
| 30 | $0.03 | 132423 |
| 31 | $0.03 | 133177 |
| 32 | $0.03 | 133664 |
| 33 | $0.04 | 135647 |
| 34 | $0.04 | 137185 |
| 35 | $0.03 | 138095 |
| 36 | $0.04 | 139166 |
| 37 | $0.03 | 140006 |
| 38 | $0.04 | 141290 |
| 39 | $0.04 | 142248 |
| 40 | $0.03 | 142769 |
| 41 | $0.04 | 144100 |
| 42 | $0.06 | 147926 |
| 43 | $0.04 | 148868 |
| 44 | $0.03 | 149345 |
| 45 | $0.10 | 158283 |
| 46 | $0.05 | 160365 |
| 47 | $0.03 | 160602 |
| 48 | $0.03 | 160954 |
| 49 | $0.04 | 162093 |
| 50 | $0.04 | 163456 |
| 51 | $0.04 | 164589 |
| 52 | $0.04 | 164984 |
| 53 | $0.05 | 167042 |
| 54 | $0.04 | 168092 |
| 55 | $0.04 | 168876 |
| 56 | $0.08 | 174642 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 0 | 0 | $0.00 |
| 🛠️ Refactor | 0 | 0 | $0.00 |
| 🔎 verify-green | 0 | 0 | $0.00 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 0 | 0 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1163 | 5347 | 14184 | 0.05 |
| red | 5 | 2 | 0 | 0 | 175 | 137 | 34 | 68 | 13946 | 818878 | 121316 | 0.73 |
| green | 7 | 0 | 3 | 0 | 498 | 204 | 55 | 106 | 20103 | 1150130 | 144615 | 0.80 |
| red-supersede | 1 | 0 | 0 | 0 | 104 | 97 | 15 | 30 | 10715 | 509313 | 44743 | 0.27 |
| diff | 1 | 1 | 0 | 0 | 32 | 12 | 3 | 6 | 906 | 53183 | 26295 | 0.08 |
| pin | 1 | 0 | 1 | 0 | 23 | 20 | 5 | 10 | 1499 | 94501 | 19692 | 0.07 |
| exhausted | 1 | 0 | 0 | 0 | 17 | 14 | 2 | 4 | 1288 | 21834 | 13120 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 4 | 4 | 0 | 399 | 128 | 35 | 70 | 11152 | 612404 | 134119 | 0.51 |
| developer | claude-opus-5-5 | 5 | 0 | 0 | 0 | 198 | 162 | 36 | 72 | 16970 | 916300 | 130801 | 0.97 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 264 | 203 | 44 | 84 | 21498 | 1124482 | 119045 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 175 | 0.73 |
| green | 0 | 0.00 | 498 | 0.80 |
| red-supersede | 0 | 0.00 | 104 | 0.27 |
| diff | 0 | 0.00 | 32 | 0.08 |
| pin | 0 | 0.00 | 23 | 0.07 |
| exhausted | 0 | 0.00 | 17 | 0.10 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| After `report-cache.sh refresh` runs on a repo with annotated vN.M tags, `.tdd/report-cache.json` holds a record listing exactly the tags `status.sh --report`'s Landed section lists, each with name, date and the issue it closes as `status.py` derives it; in the same case, a tag created before the `.tdd/status-last` since time is absent from the record (a process case: real git tags) ⟦criterion 1⟧ | 16 | 3 | 4 | 0 | 0 | 0 | 484 | 114 | 224 | 48457 | 2647839 | 369781 | 2.06 | unknown | red 1/2, green 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 1 | 1 | 1 | 3 | 2 | 1 | 2 | 2 | 2 |
| fast | 16 | 7 | 18 | 6 | 7 | 6 | 7 |  |  |  |
| target | 1 | 2 | 2 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 115 | 226 | 49620 | 2653186 | 383965 | 4.77 (estimate) |
