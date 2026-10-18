# veri-ops — the principles every operator skill obeys

An *operator skill* is one that runs veri rather than being veri: `veri-coord`, `veri-dev`,
`veri-status` and the ones that follow them. Each says near its top that it obeys this file,
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
No agent sleeps and re-checks. The run watcher this principle needs, `watch-runs.sh`, does not
exist yet: until it does, use a Monitor on a script that blocks and prints one line per
conductor exit, conductor start or merge to the default branch, and treat each line as the
event.

**Speak only when it matters (P4).** Write text only for: a run started, as
`Started #N — title`; a bail or a stall; red CI; a merge landed; a decision the human must
make; a cost or plan surprise. Anything else a watch returns — a re-arm, a conductor start the
dev session already announced, a merge already reported, a routine message from the dev
session — gets no text at all, not even "noted". Every time you mention an open human
decision, restate it in full: what is being decided, the options in words, what each costs.
Never point back at an earlier message.

**Never end a turn while work is takeable (P5).** If a slot is empty and the solvable list is
not, you are not done. A turn that does stop says why in its last line: the queue is empty, or
it names the pending decision it is waiting on.

**Raw reads go to a subagent (P6).** Leaf logs, diffs and issue sweeps are read by a subagent
on the cheapest model that can do the read, briefed to return at most 10 lines. Never print a
leaf's `.out` file into your own context.

**Read cost from the total row (P7).** A cost is the `| total |` row of the report that
carries it (`$S/metrics.sh <n>`'s `#### Total` section, or the run's committed metrics
report). Never add up phase or step rows: they overlap, and the sum double-counts.

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
message `ping`, answered `pong`. Any other message that needs confirming is answered with a
reply that starts `ack`. Until that reply arrives the message is unconfirmed — a successful
send is not a reply, so say "sent, unconfirmed", never "delivered".

## Requirements

| ID | Requirement | Why |
|---|---|---|
| P1 | A skill re-reads the state it decides on (ledger, `.tdd/`, `solvable-issues.sh`, PR state, processes) at each decision, never from its own memory. | This makes a context reset cheap. Rules were lost across resets at least 4 times. |
| P2 | A handoff carries state only, and the rules come from the skill on resume. | Same reason as P1. |
| P3 | Any waiting is done by a script that blocks until an actionable event and returns one line. No agent polls on a timer. | Each "still fine" tick costs tokens and changes nothing. |
| P4 | The skill writes text only for: a run started (`Started #N — title`), a bail or stall, red CI, a merge landed, a human decision, a cost or plan surprise. A watch event that is none of these (a re-arm, a conductor start the dev session already announced, a merge already reported, a routine message from the dev session) gets no text at all. Each open human decision is restated in full every time it is mentioned, never as a pointer to an earlier message. | "No need to narrate everything… tokens I'll never read." Mario asked four times for silence on routine watch events. |
| P5 | A turn never ends while work is takeable. A turn that stops names why: queue empty, or the pending decision. | An ended turn stalled #131 for 36 minutes. |
| P6 | Raw reads (leaf logs, diffs, issue sweeps) go to a subagent on the cheapest adequate model, which returns ≤10 lines. A leaf `.out` is never printed. | Keeps the session's context O(1). |
| P7 | A cost is read from a report's `| total |` row, never by summing phase rows. | Summing double-counted and wrongly parked #388 and #409. |
| P8 | Lowering the conductor count stops no live run. The next exit is simply not refilled. | Running work is never wasted. |
| P9 | Launch order is `solvable-issues.sh` order minus the issues with a live conductor. Any override is explicit and written down. | Prevents a duplicate launch (#753) and silent reordering. |
| P10 | An exit with no closing comment is checked for a usage limit or Mac sleep before it is treated as a bail. | A limit and sleep both look like silent exits. |
| P11 | All writes stay in the project repo. A fix that belongs elsewhere is reported, not made, and every subagent brief says so. | Repo boundary. |
| P12 | No skill names a fact specific to veri's own repo. Project specifics come from the target repo's CLAUDE.md. | The skills operate veri on any repo. |
| P13 | A message to another session (the coordinator, the dev session, or another machine's coordinator) is self-contained (no option letters, no references only the sender saw) and is sent with `SendMessage` by the skill itself. Only when delivery is held does the human get the message, as one fenced code block per recipient, named above it. A comm check is the message `ping`, answered `pong`; any other message that needs confirming is answered with a reply starting `ack`. Until that reply arrives the message is unconfirmed: a successful send is not a reply. | "dev thread does not know what a or b means." "why didn't you just send it yourself?" A send that reached a held inbox looked delivered. |

This unit is **ungraded**: nothing has signed it yet. #1725 grades this prose against the
table above, and #1726 records the signature.
