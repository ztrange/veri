# Plan for #4018 — PRD 028.2: a red CI gets a flake check before it spends the repair step

- [x] `VERI_CI_FLAKE_RERUNS` is a `tunables.TABLE` entry, default `1`, a whole number >= 0, refusal "a whole number", and `run-conductor.sh` given a value that is not a whole number exits 2 before preflight naming it and its value ⟦criterion 1⟧
- [x] `ci-flake.sh <n> <head-sha> <run-id> '<alone-cmd>' <log-file>` reads from a `gh run view --log-failed` log whose lines carry gh's job, step and timestamp prefix the test targets `rerun-alone.sh` reads from the unprefixed runner output, and runs each once alone through `<alone-cmd>` with the target as `$1` ⟦criterion 2⟧
- [x] It exits 1, writing no event and making no re-run, when the log names no target or a target stays red alone ⟦criterion 4⟧
- [x] `JOURNAL.md` and `veri/event_table.py` declare `ci-rerun` and `ci-flake` with keys `head`, `run`, `files`, and the sample journal fixture holds them ⟦criterion 9⟧
- [x] When every target passes alone and `gh run rerun <run-id> --failed` is accepted, it exits 0, writes one `ci-rerun head= run= files=` event and no `suite-flake`, drops the head's CI wait marks, and prints the targets one per line ⟦criterion 5⟧
- [x] It exits 2, writing no `ci-rerun` event, on bad arguments, an unreadable log, a head that is not 40 hex, or `gh` refusing the re-run ⟦criterion 6⟧
- [x] It exits 2, making no re-run, when an alone run gets no answer within its bound, or the log holds a non-empty line without gh's prefix
- [x] It exits 3, running nothing and writing no event, when issue `<n>`'s `ci-rerun` events since its last `conductor-start` number `VERI_CI_FLAKE_RERUNS` or more, or one names `<head-sha>` ⟦criterion 3⟧
- [x] With `REVISE_BUDGET=0`, `VERI_ADJUDICATE_BUDGET=0` and a ledger holding a `⟦ci-repair⟧` step it still re-runs and exits 0, making no `gh pr ready` call ⟦criterion 8⟧
- [x] After a `ci-rerun` event for a head, `wait-ci.sh` on that head answers neither exit 0 nor exit 1 from a check run that completed before the event ⟦criterion 7⟧
- [ ] `DRAFT-PR.md` sub-step 2, `SCRIPTS.md`'s `ci-flake.sh` entry and `CLAUDE.md`'s budgets invariant state the flake check, graded; DP52 dropped ⟦criterion 10⟧ ⟦criterion 11⟧
