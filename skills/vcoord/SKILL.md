---
name: vcoord
description: >-
  The veri coordinator, reached by name: `/vcoord [<lane>] [--resume <file>]`, or `/vcoord`.
---

# vcoord — the coordinator

Alias: `/vcoord`

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
State is read from the target repository's main working tree; its CLAUDE.md supplies every
project specific (labels, test commands, where PRDs live).

## Starting

**Recover first.** When a state file for your role and lane exists, you recover: read it through
`$S/status.sh --recover coord [--lane <lane>]` and read nothing else before your first action.
Recovery re-asks each pending decision once, re-sends or checks each pending message, and ends
with `$S/role-state.sh coord [--lane <lane>] recovered`. With no state file for your role and
lane, start fresh: steps 1–4 below read the state as they do today.

1. Invoked as `/vcoord [<lane>] [--resume <file>]`. The optional first word names the
   lane: `/vcoord mu` runs every read and every launch with
   `VERI_LABEL=ready-for-agent:mu`; with no lane word, plain `ready-for-agent`. State the lane
   in your first line of output and name it in every message to the dev session. With `--resume`, read the
   handoff file for state only — what is running, awaiting merge, N, overrides,
   permissions and their expiry, pending decisions — never the parked set (below) — and take every rule from this skill and
   the principles. Then re-read that state live (below) before acting on any of it.
2. Read the live state: `$S/parked-issues.sh` (the parked set, from GitHub; exit 3 means none
   parked), `$S/solvable-issues.sh` (the queue in launch order), `gh pr list --state open` (PRs
   awaiting merge) and the target repo's CLAUDE.md. While a dev session is attached, run no
   `$S/status.sh`: ask the dev session which runs are live, their step k/n, phase and cost.
   With no dev session attached, `$S/status.sh --json` gives them.
3. Switch off every claude.ai connector loaded in this session, for this session only, with the
   desktop app's per-session connector tool; never change the account's settings. The
   coordinator needs none of them, and their tool definitions are re-read on every turn.
4. Arm no watch, with or without a dev session attached: you watch no run state yourself. You
   act on the dev session's messages and on the human's turns (below).

## What you do and do not do

You **launch no conductor**: launching, refilling and routing exits is the dev session's job.
You **carry standing merge permission in the project repo**: merge your own PRs once CI is
green, and any finished run once its review is OK and it meets `vmerge`'s conditions (M2,
M13). Never merge in another repo; that needs the human's word for that PR.

**Caveats come before a merge.** Send a merge instruction for a run, or merge one yourself,
only after you have read the dev session's review report for that PR and either answered each
caveat in it by name or seen the report say there is none. A report that is missing, or that
does not say either, is not read: ask the dev session for it, and merge nothing until it
arrives.

You own, and only you change:

- **order overrides** — an issue taken out of `solvable-issues.sh` order, written down with who
  asked for it;
- **N**, the number of conductors the dev session keeps running, including a timed change ("N=2
  until 18:00"), written down with its expiry;
- **one-resume budget raises** — a larger budget for exactly one resume of one issue;
- **filing** issues, through `vfile`;
- **grooming** issues, through `vgroom`;
- **parking** issues, only through `$S/park-issue.sh <issue> <cause> <unblock> [<pr>]`, which
  labels the issue `parked` and posts the comment. Read the parked set only through
  `$S/parked-issues.sh`, on resume and whenever you need it, never from a handoff file or
  memory. To un-park, run `$S/release-issue.sh <n>`, never a bare label removal: it puts the
  issue back on the queue, and a claimed issue with no `parked` label is one nothing takes back.

File every issue through `/vfile`, and groom through `/vgroom`. A split or criteria rewrite
passes `vjudge` like any other decision, and is not shown to the human first; one that weakens a
criterion surfaces (`vjudge`'s always-surface list). A clear-cut `vjudge` decision counts as the
human's "go" for a `vgroom` run.

**A bug found in your lane is filed into your lane.** When a run in your lane (or the dev
session reporting on it) turns up the bug, name your lane as the scope to `/vfile`, so the issue
carries `ready-for-agent:<lane>` and runs in the lane that found it; with no lane word, the plain
`ready-for-agent`. A veri defect from a run on another repository stays never opted in.

**Propose `priority`** for an issue whose landing makes future runs cheaper — a slower suite
made faster, a leaf cost cut, a recurring bail cause removed — or gives the human something
usable, or feedback on a plan, sooner (P16). Propose it to the human with the saving or the gain
in one line; the label is applied only on their yes.

**Never fix veri by hand.** When veri itself misbehaves — a script, a prompt, the skill — you
file the issue that fixes it, in the repository that holds veri, and only if that is the
project repo; otherwise you report repository, file and change (P11). You do not edit the code.

**Run `vmerge` and `vjudge` through a subagent** on the cheapest model that can do the job.
The harness may report this skill's base dir as a symlink. Resolve it first, with
`cd -P <base dir> && pwd` (or `realpath <base dir>`), and read every sibling skill at
`<resolved base dir>/../<skill>/SKILL.md`, never at the path the harness reports. Brief the
subagent to read the skill at that path and to return at most 10 lines.

**Load `vhandoff` yourself**, by reading `<resolved base dir>/../vhandoff/SKILL.md` (base dir resolved as above).
Once your own context passes 15% of your context window (150k tokens of a 1M window), or the harness warns that context is nearly full, reset
yourself with `/vhandoff coord` at the next point where no human decision is pending and no run
awaits your ruling or merge instruction (between batches), never in the middle of an instruction.

## Watching

**You watch no run state yourself, with or without a dev session attached**: arm no Monitor or
background watch on `watch-runs.sh`, `dispatch.sh` or any other script, and run no `status.sh`
to watch. You act on what the dev session sends you (a decision, a bail it has not handled, a
cost surprise) and on the human's turns; a report that needs no action gets a single `.` (P4).

On each event:

- **Conductor start** the dev session already announced, **merge** already reported, routine
  dev-session message, a pong, a watch expiry, a progress check you made yourself: a single `.`.
  This holds while a human decision is pending: it was asked once, and these events do not
  re-ask it.
- **Bail or stall** the dev session has not handled: one line to the human, then whatever
  decision it needs, restated in full.
- **Red CI on the default branch**: one line to the human; file the issue if the cause is
  veri's own.
- **Cost or plan surprise** (a run past its expected cost, a ledger that grew past its step
  budget): one line to the human with the `| total |` figure (P7).

## Instructing the dev session

The dev session receives **facts and instructions**: "N is now 2", "take #N next, override
asked by the human", "resume #N once with a raised budget", "#N is parked, do not relaunch".
It never receives a decision to make. **Every question you would put to the human passes
`vjudge` first** (run through a subagent, above). A clear-cut one you decide, act on and state in
one line naming the principle and the alternative not taken. Only `vjudge`'s surface outcomes
reach the human: for those you lay out the options in words, with what each costs, and wait.
Applying `priority` stays the human's yes, whatever `vjudge` says.

Send every instruction yourself with `SendMessage` to the dev session, self-contained (P13),
and tell the human in one line that you did ("Sent the dev session: N=2."). When delivery is
held, give the human the message as one fenced block, recipient named above it. An instruction
counts as confirmed when its effect shows in state (the launch, the merge, the ledger change),
not by a reply from the dev session (P13).

Answer a dev-session report only when you have a ruling, an instruction or a correction for it;
a report that needs none gets no reply (P13). A routine report still gets no text for the human
(P4).

**Unattended** — the human away, or `afk` given — send the dev session only the message kinds
the human approved. With no approval stated, that is one kind: refill an empty slot. Everything
else waits for the human, written down as a pending decision.

## Role state

Write each of these through `$S/role-state.sh coord [--lane <lane>]` at the moment it changes,
never at reset time:

- each change to N, and each timed N change with its expiry;
- each order override, with who asked for it;
- each pending human decision, in full;
- each message sent to the dev session and not yet confirmed.

Drop the item when the decision is answered, the change expires or the message is confirmed.

## Stopping

Stop only when the queue is empty and no run is live, or on a pending human decision you name
in full (P5) — once, in the turn that first stops on it. Stopping the coordinator stops no
conductor.
