# Plan for #4455 — PRD 036.9: a notice when test runs keep queueing

- [x] A leg waiting for T writes an entry under `VERI_PYTEST_WAITERS` named for its pid, holding the workers it waits for and its start time, while the workers it starts with are unchanged by it ⟦criterion 1⟧
- [x] A leg's waiter entry is gone once it registers and starts pytest ⟦criterion 1⟧
- [x] A leg ended by TERM while it waits has removed its waiter entry by the time it exits ⟦criterion 1⟧
- [x] A waiter entry the leg cannot write is one stderr line naming it, and the wait goes on
- [x] `dispatch.sh` prints `queueing <k> waiting for T=<t>, <w> workers in use: a lower N would shorten the wait` and exits 0, after that poll's launch, when the last 3 polls' waiter counts are each above 0 and the newest exceeds the oldest; an equal count prints nothing ⟦criterion 2⟧ ⟦criterion 4⟧
- [x] `VERI_QUEUE_POLLS` sets how many polls' counts the rule reads ⟦criterion 2⟧
- [x] The counts are kept in the main working tree's `.tdd/dispatch-notified`, so a restarted `dispatch.sh` continues them ⟦criterion 2⟧
- [x] Once printed, the notice is not printed again until a poll counts no waiter ⟦criterion 3⟧
- [x] The real count reads only live waiter entries: one whose pid is gone or runs under another start time does not count, nor do `core-wait` events or wait markers ⟦criterion 1⟧ ⟦criterion 5⟧
- [x] CLAUDE.md's Testing idiom, `SCRIPTS.md`'s `dispatch.sh` entry and vdev's *Speaking* notice list name the waiter entries and the `queueing` notice, with their rows graded ⟦criterion 2⟧ ⟦criterion 6⟧
