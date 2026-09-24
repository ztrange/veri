# Plan for #271 — A work queue assigns issues to named workers: workqueue.sh is the only writer of .tdd/workqueue, and a worker loops next → run → merge → done

- [x] `workqueue.sh assign <worker> <issue>...` appends one `<worker>	<issue>	queued	` line per issue to `.tdd/workqueue`, in the order given ⟦criterion 1⟧
- [x] `workqueue.sh <unknown-subcommand> …` (e.g. `workqueue.sh frobnicate alpha 12`) exits 2 and leaves `.tdd/workqueue` byte-identical (absent if it was absent) ⟦added⟧ ⟦criterion 1⟧
- [x] `workqueue.sh frobnicate alpha 12` in a repo with no `.tdd/workqueue` exits 2 and leaves `.tdd/workqueue` absent ⟦added⟧ ⟦criterion 1⟧
- [x] `workqueue.sh assign` refuses with exit 2, leaving the file byte-identical, an issue already `queued` or `running` for any worker ⟦criterion 1⟧
- [x] `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, read from `VERI_GH_JSON` fixtures ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `workqueue.sh next <worker>` exits 3 with empty stdout when none of that worker's `queued` items is launchable ⟦criterion 2⟧
- [ ] `workqueue.sh start <worker> <issue>` moves that worker's `queued` item to `running` ⟦criterion 3⟧
- [ ] `workqueue.sh done <worker> <issue> <sha>` moves that worker's `running` item to `merged`, recording the sha as its detail ⟦criterion 3⟧
- [ ] `workqueue.sh park <worker> <issue> <reason>` moves that worker's `running` item to `parked`, recording the reason as its detail ⟦criterion 3⟧
- [ ] `start`, `done` or `park` naming an item another worker owns exits 1 and leaves the file byte-identical ⟦criterion 3⟧
- [ ] `start` on an item not `queued`, or `done`/`park` on an item not `running`, exits 1 and leaves the file byte-identical ⟦criterion 3⟧
- [ ] After any sequence of `assign`, `start`, `done`, `park` and refused calls, every issue ever assigned is still a line in the file ⟦criterion 4⟧
- [ ] N `assign`/`start` calls run in parallel leave a well-formed file containing every write ⟦criterion 5⟧
- [ ] A write that cannot take the lock exits 2 without touching the file ⟦criterion 5⟧
- [ ] `workqueue.sh show` prints every item grouped by worker, each with its issue and state
- [ ] `workqueue.sh show <worker>` prints only that worker's items
- [ ] Called from a linked worktree, `workqueue.sh` reads and writes `.tdd/workqueue` under the repository's main working tree, not the worktree's own
- [ ] The worker loop is documented in a `WORKER.md` beside `SKILL.md`, naming each `workqueue.sh` call (`next`, `start`, `done`, `park`) ⟦criterion 6⟧
- [ ] `SKILL.md` tells a session born as a worker to `Read` `WORKER.md`, the way it points a scope at `SCOPE-LOOP.md` ⟦criterion 6⟧
- [ ] `CONTEXT.md` defines **worker** and **work queue** ⟦criterion 6⟧

## Owed steps

- `workqueue.sh assign` with no worker, or with a worker and no issue, exits 2 and leaves the queue file byte-identical
- `workqueue.sh assign` refuses with exit 2, leaving the file byte-identical, when the same issue is named twice in one call

## Owed steps

- `solvable-issues.sh`'s `## Blocked by` parsing (its `blockers()`, `blocker_ref` and `is_open()`) lives in one shared module under `skills/tdd/scripts/lib/` that `solvable-issues.sh` imports, with its output and exit codes unchanged for every existing fixture
- `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, another worker's and a non-`queued` one, by calling that shared module rather than parsing blockers itself, read from `VERI_GH_JSON` fixtures
