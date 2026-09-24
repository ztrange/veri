# Plan for #271 — A work queue assigns issues to named workers: workqueue.sh is the only writer of .tdd/workqueue, and a worker loops next → run → merge → done

- [ ] `workqueue.sh assign <worker> <issue>...` appends one `<worker>	<issue>	queued	` line per issue to `.tdd/workqueue`, in the order given ⟦criterion 1⟧
- [ ] `workqueue.sh assign` refuses with exit 2, leaving the file byte-identical, an issue already `queued` or `running` for any worker ⟦criterion 1⟧
- [ ] `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, read from `VERI_GH_JSON` fixtures ⟦criterion 2⟧
- [ ] `workqueue.sh next <worker>` exits 3 with empty stdout when none of that worker's `queued` items is launchable ⟦criterion 2⟧
- [ ] `workqueue.sh start <worker> <issue>` moves that worker's `queued` item to `running` ⟦criterion 3⟧
- [ ] `workqueue.sh done <worker> <issue> <sha>` moves a `running` item to `merged` recording the sha, and `park <worker> <issue> <reason>` moves it to `parked` recording the reason ⟦criterion 3⟧
- [ ] `start`, `done` or `park` on another worker's item, or from any state but the one its transition starts from, exits 1 and leaves the file byte-identical ⟦criterion 3⟧
- [ ] After any sequence of `assign`, `start`, `done`, `park` and refused calls, every issue ever assigned is still a line in the file ⟦criterion 4⟧
- [ ] N `assign`/`start` calls run in parallel leave a well-formed file containing every write ⟦criterion 5⟧
- [ ] A write that cannot take the lock exits 2 without touching the file ⟦criterion 5⟧
- [ ] `workqueue.sh show [<worker>]` prints the queue grouped by worker with each item's state, only that worker's items when one is named
- [ ] Called from a linked worktree, `workqueue.sh` reads and writes `.tdd/workqueue` under the repository's main working tree, not the worktree's own
- [ ] The worker loop is documented in a `WORKER.md` beside `SKILL.md`, naming each `workqueue.sh` call (`next`, `start`, `done`, `park`) ⟦criterion 6⟧
- [ ] `CONTEXT.md` defines **worker** and **work queue** ⟦criterion 6⟧
