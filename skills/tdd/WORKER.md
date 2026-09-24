# tdd — working a queue

A worker's half of the `tdd` skill. `SKILL.md` is resident in every conductor request; this
file is not — it is read only by a session born as a **worker** `<name>`, the way a scope run
reads `SCOPE-LOOP.md`. The issues it works are the ones assigned to `<name>` in the **work
queue**, `.tdd/workqueue` in the main working tree, and `workqueue.sh` is the only thing that
writes that file: every state change below is one of its calls, never an edit by hand.

## The worker loop

Repeat until `next` says there is nothing left:

1. `workqueue.sh next <name>` — prints the first `queued` issue of yours whose `## Blocked by`
   names no open issue. Exit 3, with nothing printed, means nothing is launchable: stop.
2. `workqueue.sh start <name> <issue>` — moves the item `queued` → `running`. A refusal
   (exit 1) means it is not yours or not `queued`; do not launch it.
3. Launch `run-conductor.sh <issue>` detached, and wait for it to finish.
4. Read what it left:
   - **A draft PR** — merge it under the merge lock, then
     `workqueue.sh done <name> <issue> <merge-sha>` moves the item `running` → `merged`.
   - **A bail** — read it. On the issue's second bail,
     `workqueue.sh park <name> <issue> <reason>` moves the item `running` → `parked`,
     recording why.
5. Go back to 1.

The judgement calls — merging, reading a bail — stay yours. The queue's state changes are the
script's: nothing else writes `.tdd/workqueue`, and no line in it is ever deleted.
