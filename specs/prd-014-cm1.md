# PRD 014 CM1: what the conductor spends composing routine comments

Measured with `skills/tdd/scripts/metrics.sh <issue>` afresh at the branch tip, after the later-record fix, run in this
worktree, whose `.tdd/` reads the main checkout's `conductor-<n>.log`. Dollars are output tokens at
`veri/prices.py`'s `claude-opus-5-5` output rate ($20.00 per million tokens). The families are CM3's.
**Every per-family token or dollar figure is an average-split estimate**: a result record's output total is
split evenly across its turns, so a family's tokens are its turns times that average, not a count of what the
comment itself cost.

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
| ✅ Step done | 12 | 5809 | 0.12 | 1 | 523 | 0.01 |
| ✅ Done | 10 | 4552 | 0.09 | 1 | 523 | 0.01 |
| 🔴 Red | 16 | 8258 | 0.17 | 6 | 3258 | 0.07 |
| 🟢 Green | 13 | 6676 | 0.13 | 5 | 2695 | 0.05 |
| 🛠️ Refactor | 7 | 3643 | 0.07 | 1 | 523 | 0.01 |
| 🔎 verify-green | 15 | 7796 | 0.16 | 5 | 2695 | 0.05 |
| 🔎 verify-refactor | 7 | 3643 | 0.07 | 1 | 523 | 0.01 |
| 🔎 verify-<phase> (revised) | 9 | 4678 | 0.09 | 4 | 2172 | 0.04 |
| 🗺️ Plan | 1 | 523 | 0.01 | 1 | 563 | 0.01 |
| 🗺️ verify-plan | 1 | 523 | 0.01 | 1 | 563 | 0.01 |
| ▶️ Resuming | 7 | 3420 | 0.07 | 1 | 523 | 0.01 |
| ⛔ Bailed | 5 | 2607 | 0.05 | 1 | 563 | 0.01 |
| ⏹️ Stopped | 0 | 0 | 0.00 | 0 | 0 | 0.00 |
| **Total** | **73** | **36667** | **0.73** | **21** | **11343** | **0.23** |

The Total row counts each comment message once: a message matching two families (a `🔴 Red` comment that also
matches `🔎 verify-red`) is one turn, so the Total is below the sum of the rows.

| run | comment turns / all conductor turns | comment dollars / conductor dollars |
| --- | ---: | ---: |
| #2488 | 73 / 523 (14.0%) | $0.73 / $27.65 (2.6%) |
| #2517 | 21 / 141 (14.9%) | $0.23 / $7.24 (3.2%) |

## Decision

Composing routine comments is 73 and 21 comment messages, about 14% of a conductor's turns, and about 3% of its
dollars ($0.23 to $0.73 a run, an average-split estimate). The dollars are small, so 014.4b to 014.4g do **not**
go ahead as filed on a cost saving. They are rewritten to serve data alone: a scripted comment is rendered from
the journal and ledger so the thread mirrors them exactly, and none is justified by a saving. Any of them whose
data benefit does not hold on its own is closed before mu reaches it. With two runs, neither with an event log,
the sample is thin; it is enough to rule out a cost case, not to size a data case.
