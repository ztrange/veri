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

1. Invoked as `/vcoord [<lane>] [--resume <file>]`. The optional first word names the
   lane: `/vcoord mu` runs every read and every launch with
   `VERI_LABEL=ready-for-agent:mu`; with no lane word, plain `ready-for-agent`. State the lane
   in your first line of output and name it in every message to the dev session. With `--resume`, read the
   handoff file for state only — what is running, awaiting merge, N, overrides,
   permissions and their expiry, pending decisions — never the parked set (below) — and take every rule from this skill and
   the principles. Then re-read that state live (below) before acting on any of it.
2. Read the live state: `$S/status.sh --json` (every run, its step k/n, phase, cost),
   `$S/parked-issues.sh` (the parked set, from GitHub; exit 3 means none parked),
   `$S/solvable-issues.sh` (the queue in launch order), `gh pr list --state open` (PRs
   awaiting merge) and the target repo's CLAUDE.md.
3. Switch off every claude.ai connector loaded in this session, for this session only, with the
   desktop app's per-session connector tool; never change the account's settings. The
   coordinator needs none of them, and their tool definitions are re-read on every turn.
4. Arm the watch (below) and stay in it.

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
  memory. To un-park, remove the `parked` label from the issue.

File every issue through `/vfile`, and groom through `/vgroom`; show any split or
criteria rewrite to the human first.

**Propose `priority`** for an issue whose landing makes future runs cheaper — a slower suite
made faster, a leaf cost cut, a recurring bail cause removed — or gives the human something
usable, or feedback on a plan, sooner (P16). Propose it to the human with the saving or the gain
in one line; the label is applied only on their yes.

**Never fix veri by hand.** When veri itself misbehaves — a script, a prompt, the skill — you
file the issue that fixes it, in the repository that holds veri, and only if that is the
project repo; otherwise you report repository, file and change (P11). You do not edit the code.

**Run `vmerge` and `vjudge` through a subagent** on the cheapest model that can do the job.
Brief it to read the skill at `<base dir>/../<skill>/SKILL.md` and to return at most 10 lines.

**Load `vhandoff` yourself**, by reading `<base dir>/../vhandoff/SKILL.md`.

## Watching

Watch through the blocking watch of P3, `$S/watch-runs.sh`, which prints one line per
conductor exit. Run `watch-runs.sh` itself
under a Monitor (or as a background command), never a hand-written script. When the watch returns, re-read the state the line names
(P1), act if it calls for it, and re-arm at once; a re-arm gets a single `.` (P4).

On each event:

- **Conductor start** the dev session already announced, **merge** already reported, routine
  dev-session message, watch expiry, a progress check you made yourself: a single `.`; re-arm. This
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

Answer every report the dev session sends (a run done, a review verdict, a merge, a bail, a
resume) with a one-line reply starting `ack` — or with the ruling or instruction it prompts,
which is then the `ack` (P13). The `ack` goes to the dev session only; a routine report still
gets no text for the human (P4).

**Unattended** — the human away, or `afk` given — send the dev session only the message kinds
the human approved. With no approval stated, that is one kind: refill an empty slot. Everything
else waits for the human, written down as a pending decision.

## Stopping

Stop only when the queue is empty and no run is live, or on a pending human decision you name
in full (P5) — once, in the turn that first stops on it. Stopping the coordinator stops no
conductor.
