# PRD 014 CM1: what the conductor spends composing routine comments

Measured with `skills/tdd/scripts/metrics.sh <issue>` at branch tip `01af52c706`, run in this
worktree, whose `.tdd/` reads the main checkout's `conductor-<n>.log`. Dollars are output tokens at
`veri/prices.py`'s `claude-opus-5-5` output rate ($20.00 per million tokens). The families are CM3's.

## Runs measured

Two runs have a conductor transcript in the main checkout's `.tdd/`: #2488 and #2517.
**Neither has an event log on this machine**: the main checkout's `.tdd/events.jsonl` holds no
event of either issue, so `metrics.sh` prints "Outcome: none yet" for both. Strictly, then, no run
meets "transcript and event log both exist"; the figures below come from the transcripts alone, and
the transcripts show the sessions' result records (#2488: 8 sessions, 523 turns, $27.65; #2517:
2 sessions, 141 turns, $7.24). Five runs, CM1's count, are not reachable here.

## Conductor comments, by family

| family | #2488 turns | #2488 output tokens | #2488 $ | #2517 turns | #2517 output tokens | #2517 $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ✅ Step done | 7 | 3495 | 0.07 | 0 | 0 | 0.00 |
| ✅ Done | 5 | 2276 | 0.05 | 1 | 523 | 0.01 |
| 🔴 Red | 8 | 4084 | 0.08 | 3 | 1649 | 0.03 |
| 🟢 Green | 5 | 2465 | 0.05 | 0 | 0 | 0.00 |
| 🛠️ Refactor | 5 | 2665 | 0.05 | 0 | 0 | 0.00 |
| 🔎 verify-green | 6 | 2940 | 0.06 | 0 | 0 | 0.00 |
| 🔎 verify-refactor | 5 | 2665 | 0.05 | 0 | 0 | 0.00 |
| 🔎 verify-<phase> (revised) | 3 | 1603 | 0.03 | 2 | 1086 | 0.02 |
| 🗺️ Plan | 1 | 523 | 0.01 | 1 | 563 | 0.01 |
| 🗺️ verify-plan | 1 | 523 | 0.01 | 1 | 563 | 0.01 |
| ▶️ Resuming | 1 | 559 | 0.01 | 0 | 0 | 0.00 |
| ⛔ Bailed | 3 | 1567 | 0.03 | 1 | 563 | 0.01 |
| ⏹️ Stopped | 0 | 0 | 0.00 | 0 | 0 | 0.00 |
| **Total** | **50** | **25365** | **0.50** | **9** | **4947** | **0.09** |

Totals are the sums of the rows (dollars are the sum of the rounded rows).

| run | comment turns / all conductor turns | comment dollars / conductor dollars |
| --- | ---: | ---: |
| #2488 | 50 / 523 (9.6%) | $0.50 / $27.65 (1.8%) |
| #2517 | 9 / 141 (6.4%) | $0.09 / $7.24 (1.2%) |

## Decision

Composing routine comments costs about 1 to 2% of a conductor's dollars (roughly $0.09 to $0.50 a
run). That is negligible, so 014.4b to 014.4g do **not** go ahead as filed, on a cost saving. They are
rewritten to serve data alone: a scripted comment is rendered from the journal and ledger so the
thread mirrors them exactly, and none is justified by a saving. Any of them whose data benefit does
not hold on its own is closed before mu reaches it. With two runs, neither with an event log,
the sample is thin; it is enough to rule out a cost case, not to size a data case.
