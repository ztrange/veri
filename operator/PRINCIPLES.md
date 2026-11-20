# veri-ops — the principles every operator skill obeys

An *operator skill* is one that runs veri rather than being veri: `vdev`,
`vstatus` and the ones that follow them. Each says near its top that it obeys this file,
and each reads it first. A rule stated here is not restated in a skill, and a skill that
contradicts this file is wrong, not an exception.

`$S` below is `skills/tdd/scripts/` in the clone the skill was installed from — the directory
holding `run-conductor.sh`, `solvable-issues.sh` and the rest. Paths under `.tdd/` are in the
target repository's main working tree.

## Operator principles

**Re-read, never remember (P1).** Every decision is made on state read at that moment: the
committed ledger (`.tdd/wt/<n>/.tdd/issue-<n>.md`), the run's `.tdd/` files, the output of
`$S/solvable-issues.sh`, the PR's state from `gh pr view`, and the live processes: a
conductor is live only when the first line of `.tdd/wt/<n>/.tdd/conductor.pid`, its pid, answers
`kill -0` and that pid's start time matches the file's second line, the rule `$S/status.sh --json`
applies, so the check is never hand-rolled. What you saw an hour ago, or before a context reset,
is not an input. If you catch yourself deciding from memory, re-read
first.

**Saved state carries state, never rules (P2).** The role state file
(`.tdd/role-<role>.state`), and in a terminal a handoff file, say what is running, parked,
waiting and pending, and with what permissions. Neither copies a rule out of a skill; on
recovery or resume the rules come from re-reading the skill and this file.

**Wait in a blocking script, never on a timer (P3).** Any wait — for a conductor to exit, a
merge to land, CI to finish — is a script that blocks until something actionable happens and
returns one line. For CI that is `$S/wait-ci.sh <pr-url> [slice] [total]`, called again on exit
3. For a command you started, `$S/detach-command.sh wait <name> [max]`, called again on exit 3.
No agent sleeps and re-checks. The one blocking watch for operator sessions over conductors, launches and merges is
`$S/dispatch.sh`: it runs as one background command, never under a Monitor and never a
hand-written script, and each line it prints is the event.

**Speak only when it matters (P4).** Every turn shows something, because a turn with no
text makes the harness ask for visible output, and answering that with prose is how narration
creeps back in. So the size of the text follows the event. **The dev session prints `.` and
nothing else**, as vdev's *Speaking* says: a run's events are on its issue (its claim, step
ticks, bails, merges), not in the transcript. A decision it asks in its own transcript, in a
session without `start_session` (vdev's *When to stop and ask*), is written in full: a decision
the human must make is the one exception to the size limit. **Ask a decision once**, when it arises, and in full: what is being decided,
the options in words, what each costs. Later events do not repeat it; a new decision is its own
message, not a re-print of the pending list. Mention an open decision again only when the human
asks what is pending or its facts change, and then restate it in full, never as a pointer to an
earlier message; a dev session with `start_session` restates it only inside its own question
session, never in its transcript (vdev's *Speaking*).

**Never end a turn while work is takeable (P5).** If a slot is empty and the solvable list is
not, you are not done. A turn that does stop says why in its last line: the queue is empty, or
it names the pending decision it is waiting on. That line is owed once, by the turn that stops
on it; a later turn ended by a routine event while the same decision is pending gets a single `.`
(P4). A stopping turn of the dev session prints `.`: its reason is already in state, the empty
`$S/solvable-issues.sh` or an open question file. The exception is a session without
`start_session`, where the turn that stops on a decision names it once.

**Investigation goes to a subagent (P6).** An operator role does no investigation in its own
context. Every lookup that takes more than one command — reading source, grepping for how a
script works, git archaeology, a log, a diff, an issue sweep — goes to one subagent on the
cheapest adequate model, briefed to return at most 10 lines. Never print a leaf's `.out` file
into your own context. Independent single commands go out as parallel calls in one message,
not one per turn.

**Read cost from the total row (P7).** A cost is the `| total |` row of the report that
carries it. A complete run's cost is the `| total |` row of `$S/metrics.sh <n>`'s
`#### Total` section (or the run's committed metrics report), which includes the conductor's
own spending, or which says in the report that it excludes it when it cannot price that
spending. Never add up phase or step rows: they overlap, and the sum double-counts.

**Lowering N stops nothing (P8).** When the conductor count N goes down, no live run is
stopped. The next conductor that exits is simply not replaced, until the count is at N.

**Launch in the selection layer's order (P9).** The next issue launched is the first line of
`$S/solvable-issues.sh` that has no live conductor (no `.tdd/wt/<n>/.tdd/conductor.pid`
whose first-line pid answers `kill -0` with its start time matching the second line, the rule
`$S/solvable-issues.sh` already applies to the issues it lists). Any other order is an override: it is explicit, it names who
asked for it, and it is written down in the role state file, which every reset reads, never in
a handoff; the dev session tells the human nothing of it (vdev's *Speaking*).

**A silent exit is checked before it is a bail (P10).** A conductor that exits with no closing
comment on its issue (neither ✅ Done nor a bail) is first checked for a usage limit — a 429 or
a usage-limit message in its output, or a last leaf that answered in one turn at zero cost —
for an API outage — a conductor log ending in an API-unreachable error, as vbail defines it,
and nothing wider — and for the machine
having slept (on a Mac, `pmset -g log | grep -E 'Sleep|Wake'` over the run's window). Only
when none of the three explains the exit is it treated as a bail.

**Write only in the project repo (P11).** Every commit, branch, push, PR, issue, comment and
label lands in the repository the session started in. A fix that belongs in another repository
is reported — repository, file, the change you would make — and not made. Every subagent brief
you write says the same, in those words.

**No project facts in a skill (P12).** A skill never names anything specific to one
repository: no issue number, no branch, no label, no test command, no person. Project
specifics are read from the target repository's CLAUDE.md each time they are needed, and the
tdd scripts' own defaults stand where it is silent.

**Messages between sessions are self-contained and sent by you (P13).** A message to another
session — vdev or one of its question sessions — names everything it
refers to: no option letters, no "as above", no reference only you saw. You send it yourself
with `SendMessage`. Only when delivery is held does the human get it instead: one fenced code
block per recipient, with the recipient named on the line above it. A comm check is the
message `ping`, answered `pong`, and runs only when a role starts or recovers from its role state file. No
other message between operator sessions — an instruction, a ruling, a report (a run done, a
review verdict, a merge, a bail, a resume) — is answered with an `ack`, in either direction. A
message gets a reply only when the receiver has a ruling, an instruction or a correction to
send. A sent message is confirmed by the effect it causes, read from state
(P1) — the launch, the merge, the ledger change — never by a reply. Until that effect is
observed, say "sent, unconfirmed", never "delivered"; a successful send is not a confirmation.
A routine report still gets no text for the human (P4).

**Never ask permission for what a run needs (P14).** A role never asks permission for an
operation a run needs in order to continue, in the project repo: opening or updating a PR,
filing, commenting on or closing an issue, editing repo files, running tests, removing a run's
own files, worktree or branch, and any `gh` command. It does the operation and reports it. Asking is kept for the decisions its own
skill lists (vdev's D8); P11's other-repo boundary and the rulings that hold a merge still
apply.

**Smaller slices outrank cheaper ones (P16).** When the size of a slice and what it costs pull
apart, take the smaller slice: continuous delivery of value, shorter feedback loops, manageable
bites of work. A plan, an issue or a group of issues is never made larger to save money, and
saving money is never the reason for its size. This ranks only those two: it grants no
real-money spend, which stays the human's.

**A decision goes to the human as plain text (P21).** An operator role never asks the human
through a question tool (`AskUserQuestion`) or a blocking end-of-turn box: either stops the role
until the human answers. A decision goes out once, as plain text (P4), and only its own item waits;
everything else goes on. It is not repeated on routine turns. When the human's next message
arrives, whatever it is about, the role answers it and then restates every pending decision in
full, a third case beyond the two P4 names. A dev session with `start_session` meets this inside
each pending decision's own question session, never in its own transcript (vdev's *Speaking*).

**Every question passes the judge first (P22).** An operator role passes each question through
`vjudge` before it reaches the human; only what the judge surfaces reaches the human. Two
exceptions. In `/vplan` every design decision still reaches the human, the judge reviewing the
planner's recommendation for it and never settling or withholding it. `/vish` runs in the user's
own session, so its questions go straight to the user, never through `vjudge`.
