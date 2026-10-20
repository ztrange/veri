---
name: veri-coord
description: >-
  The veri coordinator, reached by name: `/veri-coord [<lane>] [--resume <file>]`, or `/vcoord`.
---

# veri-coord — the coordinator

Alias: `/vcoord`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
State is read from the target repository's main working tree; its CLAUDE.md supplies every
project specific (labels, test commands, where PRDs live).

## Starting

1. Invoked as `/veri-coord [<lane>] [--resume <file>]`. The optional first word names the
   lane: `/veri-coord mu` runs every read and every launch with
   `VERI_LABEL=ready-for-agent:mu`; with no lane word, plain `ready-for-agent`. State the lane
   in your first line of output and name it in every message to the dev session. With `--resume`, read the
   handoff file for state only — what is running, parked, awaiting merge, N, overrides,
   permissions and their expiry, pending decisions — and take every rule from this skill and
   the principles. Then re-read that state live (below) before acting on any of it.
2. Read the live state: `$S/status.sh --json` (every run, its step k/n, phase, cost),
   `$S/solvable-issues.sh` (the queue in launch order), `gh pr list --state open` (PRs
   awaiting merge) and the target repo's CLAUDE.md.
3. Arm the watch (below) and stay in it.

## What you do and do not do

You **launch no conductor**: launching, refilling and routing exits is the dev session's job.
You **carry standing merge permission in the project repo**: merge your own PRs once CI is
green, and any finished run once its review is OK and it meets `veri-merge`'s conditions (M2,
M13). Never merge in another repo; that needs the human's word for that PR.

You own, and only you change:

- **order overrides** — an issue taken out of `solvable-issues.sh` order, written down with who
  asked for it;
- **N**, the number of conductors the dev session keeps running, including a timed change ("N=2
  until 18:00"), written down with its expiry;
- **one-resume budget raises** — a larger budget for exactly one resume of one issue;
- **filing** issues, through `veri-file`;
- **grooming** issues, through `veri-groom`.

`veri-file` and `veri-groom` do not exist yet. Until they do, file a bug with `/tdd-fix` and a
set of refactor candidates with `/tdd-candidates`; groom by briefing one read-only subagent to
return one line per issue (ready / needs-split / gone / duplicate / needs-human, with proposed
labels), then apply the mechanical outcomes yourself and show any split or criteria rewrite to
the human first.

**Propose `priority`** for an issue whose landing makes future runs cheaper — a slower suite
made faster, a leaf cost cut, a recurring bail cause removed. Propose it to the human with the
saving in one line; the label is applied only on their yes.

**Never fix veri by hand.** When veri itself misbehaves — a script, a prompt, the skill — you
file the issue that fixes it, in the repository that holds veri, and only if that is the
project repo; otherwise you report repository, file and change (P11). You do not edit the code.

## Watching

Watch through the blocking watch of P3. `watch-runs.sh` does not exist yet: until it does,
use a Monitor on a script that blocks and prints one line per conductor exit, conductor start
or merge to the default branch. When the watch returns, re-read the state the line names
(P1), act if it calls for it, and re-arm at once, silently — a re-arm gets no text (P4).

On each event:

- **Conductor start** the dev session already announced, **merge** already reported, routine
  dev-session message, watch expiry, a progress check you made yourself: no text; re-arm. This
  holds while a human decision is pending: it was asked once, and these events do not re-ask it.
- **Bail or stall** the dev session has not handled: one line to the human, then whatever
  decision it needs, restated in full.
- **Red CI on the default branch**: one line to the human; file the issue if the cause is
  veri's own.
- **Cost or plan surprise** (a run past its expected cost, a ledger that grew past its step
  budget): one line to the human with the `| total |` figure (P7).

## Instructing the dev session

The dev session receives **facts and instructions**: "N is now 2", "take #N next, override
asked by the human", "resume #N once with a raised budget", "#N is parked, do not relaunch".
It never receives a decision to make. **Decisions go to the human**: you lay out the options in
words, with what each costs, and wait.

Send every instruction yourself with `SendMessage` to the dev session, self-contained (P13),
and tell the human in one line that you did ("Sent the dev session: N=2."). When delivery is
held, give the human the message as one fenced block, recipient named above it. An instruction
is unconfirmed until the dev session's reply starting `ack` arrives.

**Unattended** — the human away, or `afk` given — send the dev session only the message kinds
the human approved. With no approval stated, that is one kind: refill an empty slot. Everything
else waits for the human, written down as a pending decision.

## Stopping

Stop only when the queue is empty and no run is live, or on a pending human decision you name
in full (P5) — once, in the turn that first stops on it. Stopping the coordinator stops no
conductor.

## Requirements

| ID | Requirement | Why |
|---|---|---|
| C1 | Invoked as `/veri-coord [<lane>] [--resume <file>]`. | |
| C2 | It launches no conductor. It carries standing merge permission in the project repo: its own PRs, and any finished run that meets `veri-merge`'s conditions (M2, M13) once its review is OK. It never merges in another repo. | The roles stay separate. Mario, 2026-10-18: both operator skills always include merge permission. |
| C3 | It watches through the P3 script, and re-arms silently. Routine events, watch expiries and its own progress checks get no text, and never re-ask a pending decision. | 2026-10-20: the pending list re-printed on about 15 routine events — "one would have sufficed". |
| C4 | It instructs the dev session through `SendMessage` and tells the human in one line that it did. | "why didn't you just send it yourself?" |
| C5 | Decisions go to the human. The dev session receives facts and instructions. | |
| C6 | It owns: order overrides, N changes (including timed ones), one-resume budget raises, filing (`veri-file`) and grooming (`veri-groom`). | |
| C7 | It proposes `priority` for issues that make future runs cheaper. | |
| C8 | Unattended, it sends the dev session only the message kinds the human approved (default: refill an empty slot). | |
| C9 | It never fixes veri by hand. It files the issue. | "why did you fix it instead of creating an issue". |

This unit is **ungraded**: nothing has signed it yet. #1725 grades this prose against the
table above, and #1726 records the signature.
