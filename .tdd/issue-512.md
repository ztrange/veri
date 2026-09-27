# Plan for #512 — flaky: supervise.test.sh case 50 kills the slept-through leaf, because the clock-suspend stub jumps the clock before it records the suspension

- [x] The clock-suspend stub records the suspension before, or atomically with, its clock jump, so the injected awake clock never reads higher than the true awake seconds at any moment during the stub's run ⟦criterion 1⟧
- [x] Case 50's slept-through leaf stays suspended across two watchdog polls before it exits 0, and still reports status 0 with secs in the awake range ⟦criterion 1⟧
- [x] Repair: clock-suspend moves the wall clock and the awake clock in one atomic write, so no watchdog poll ever sees one moved without the other — case 50 still failed status=2 in 1 of 17 runs because, with the suspension recorded first, one poll saw the awake clock 100 s behind the wall clock, supervise.sh credited that as sleep, a log write at the same poll reset seen_at and discarded the credit, and the next poll read 100 s of silence ⟦added⟧ ⟦criterion 1⟧
- [x] The slept-through case reports status=0 with secs in the awake range on 20 consecutive runs of supervise.test.sh, recorded in the PR body ⟦human-owed⟧ ⟦criterion 2⟧
- [x] supervise.sh's kill policy and VERI_POLL are unchanged: git diff origin/main -- skills/tdd/scripts/supervise.sh is empty, recorded in the PR body ⟦human-owed⟧ ⟦criterion 3⟧
