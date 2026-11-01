# veri-ops — the principles every operator skill obeys

An *operator skill* is one that runs veri rather than being veri: `vcoord`, `vdev`,
`vstatus` and the ones that follow them. Each says near its top that it obeys this file,
and each reads it first. A rule stated here is not restated in a skill, and a skill that
contradicts this file is wrong, not an exception.

`$S` below is `skills/tdd/scripts/` in the clone the skill was installed from — the directory
holding `run-conductor.sh`, `solvable-issues.sh` and the rest. Paths under `.tdd/` are in the
target repository's main working tree.

## Operator principles

**Re-read, never remember (P1).** Every decision is made on state read at that moment: the
committed ledger (`.tdd/wt/<n>/.tdd/issue-<n>.md`), the run's `.tdd/` files, the output of
`$S/solvable-issues.sh`, the PR's state from `gh pr view`, and the live processes
(`.tdd/wt/<n>/.tdd/conductor.pid` checked with `kill -0`). What you saw an hour ago, or
before a context reset, is not an input. If you catch yourself deciding from memory, re-read
first.

**A handoff carries state, never rules (P2).** A handoff file says what is running, parked,
waiting and pending, and with what permissions. It never copies a rule out of a skill; on
resume the rules come from re-reading the skill and this file.

**Wait in a blocking script, never on a timer (P3).** Any wait — for a conductor to exit, a
merge to land, CI to finish — is a script that blocks until something actionable happens and
returns one line. For CI that is `$S/wait-ci.sh <pr-url> [slice] [total]`, called again on exit
3. For a command you started, `$S/detach-command.sh wait <name> [max]`, called again on exit 3.
No agent sleeps and re-checks. For conductor exits the blocking watch is `$S/watch-runs.sh`:
a Monitor (or a background command) runs `watch-runs.sh` itself, never a hand-written script,
and each line it prints is the event.

**Speak only when it matters (P4).** Every turn shows something, because a turn with no
text makes the harness ask for visible output, and answering that with prose is how narration
creeps back in. So the size of the text follows the event. An important event gets one line of
fewer than ten words: a run started, as `Started #N — title`; a bail or a stall; red CI; a merge
landed; a cost or plan surprise. Anything else a watch returns — a re-arm, a conductor start
the dev session already announced, a merge already reported, a routine message from the dev
session, an ack, a progress check, a watch expiry — gets a single `.` and nothing else, not
"noted" or "still watching". A decision the human must make is the one exception to the size
limit: it is written in full. **Ask a decision once**, when it arises, and in full: what is being decided,
the options in words, what each costs. Later events do not repeat it; a new decision is its own
message, not a re-print of the pending list. Mention an open decision again only when the human
asks what is pending or its facts change, and then restate it in full, never as a pointer to an
earlier message.
When a coordinator is attached to the dev session, an event that earns the dev session text is
instead one message to the coordinator, carrying facts only and never a pasted log or issue
tail (P6); the human gets only the `.` from the dev session about it, unless the dev session is
stopped on a human decision.

**Never end a turn while work is takeable (P5).** If a slot is empty and the solvable list is
not, you are not done. A turn that does stop says why in its last line: the queue is empty, or
it names the pending decision it is waiting on. That line is owed once, by the turn that stops
on it; a later turn ended by a routine event while the same decision is pending gets a single `.`
(P4).

**Raw reads go to a subagent (P6).** Leaf logs, diffs and issue sweeps are read by a subagent
on the cheapest model that can do the read, briefed to return at most 10 lines. Never print a
leaf's `.out` file into your own context.

**Read cost from the total row (P7).** A cost is the `| total |` row of the report that
carries it. A complete run's cost is the `| total |` row of `$S/metrics.sh <n>`'s
`#### Total` section (or the run's committed metrics report), which includes the conductor's
own spending, or which says in the report that it excludes it when it cannot price that
spending. Never add up phase or step rows: they overlap, and the sum double-counts.

**Lowering N stops nothing (P8).** When the conductor count N goes down, no live run is
stopped. The next conductor that exits is simply not replaced, until the count is at N.

**Launch in the selection layer's order (P9).** The next issue launched is the first line of
`$S/solvable-issues.sh` that has no live conductor (no `.tdd/wt/<n>/.tdd/conductor.pid`
whose pid answers `kill -0`). Any other order is an override: it is explicit, it names who
asked for it, and it is written down where the next reader of state finds it — the handoff,
and the one line you tell the human.

**A silent exit is checked before it is a bail (P10).** A conductor that exits with no closing
comment on its issue (neither ✅ Done nor a bail) is first checked for a usage limit — a 429 or
a usage-limit message in its output, or a last leaf that answered in one turn at zero cost —
and for the machine having slept (on a Mac, `pmset -g log | grep -E 'Sleep|Wake'` over the
run's window). Only when neither explains the exit is it treated as a bail.

**Write only in the project repo (P11).** Every commit, branch, push, PR, issue, comment and
label lands in the repository the session started in. A fix that belongs in another repository
is reported — repository, file, the change you would make — and not made. Every subagent brief
you write says the same, in those words.

**No project facts in a skill (P12).** A skill never names anything specific to one
repository: no issue number, no branch, no label, no test command, no person. Project
specifics are read from the target repository's CLAUDE.md each time they are needed, and the
tdd scripts' own defaults stand where it is silent.

**Messages between sessions are self-contained and sent by you (P13).** A message to another
session — the coordinator, the dev session, another machine's coordinator — names everything it
refers to: no option letters, no "as above", no reference only you saw. You send it yourself
with `SendMessage`. Only when delivery is held does the human get it instead: one fenced code
block per recipient, with the recipient named on the line above it. A comm check is the
message `ping`, answered `pong`. Every other message between operator sessions — an
instruction, a ruling, a report (a run done, a review verdict, a merge, a bail, a resume) — is
answered with a reply that starts `ack`, in both directions; an `ack` itself is not answered.
When the receiver's answer carries a ruling or an instruction, that message is the `ack`. Until
the `ack` arrives the message is unconfirmed — a successful send is not a reply, so say "sent,
unconfirmed", never "delivered". The `ack` goes to the sender, not to the human: a routine
report still gets no text for the human (P4).

**Never ask permission for what a run needs (P14).** A role never asks permission for an
operation a run needs in order to continue, in the project repo: opening or updating a PR,
filing, commenting on or closing an issue, editing repo files, running tests, removing a run's
own files, worktree or branch, and any `gh` command. It does the operation and reports it. That
holds for the human and for the coordinator alike. Asking is kept for the decisions its own
skill lists (vdev's D8); P11's other-repo boundary and the rulings that hold a merge still
apply.
