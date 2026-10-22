# PRD 011 requirements: operator skills, graded prose

This is the requirements list for PRD 011 (#1712). Its child issues cite the IDs below, so it lives on `main`, where a leaf can read it. Each line makes one
claim that a reviewer, a grader or a test can mark true or false. **Why** says why the
requirement exists, and the grader never sees it. When a skill is written, its rows move to
`skills/<name>/REQUIREMENTS.md`. The file is deleted once every section has moved.

IDs are stable: a reworded requirement keeps its ID, and a dropped one leaves a gap.

---

## G: grading prose against a requirements list (code, built by veri under `/tdd`)

| ID | Requirement | Why |
|---|---|---|
| G1 | A *prose unit* is one file, or one `##` section of a file, that has a requirements list of its own. | Grading a 213 kB SKILL.md whole costs ~79k tokens; a section costs a fraction. |
| G2 | A requirements list is a Markdown table with the columns `ID`, `Requirement` and `Why`. Its location is either `REQUIREMENTS.md` beside the unit or a named section of one. | One format means one parser and no second convention. |
| G3 | The parser rejects (exit 2, naming the line) a duplicate ID, an empty requirement, and a row that has no ID. | A malformed list must never grade as PASS by having nothing to check. |
| G4 | The grader receives the unit's text and the `ID` + `Requirement` columns only: never `Why`, a diff, a commit message or the author's rationale. | The same blindness `build-verify-prompt.sh` guarantees for verifiers. |
| G5 | The grader first analyses freely, then ends its reply with a `BEGIN GRADES` … `END GRADES` block: one `<ID>: PASS\|FAIL — <reason>` line per requirement, in list order, then `VERDICT: PASS` or `VERDICT: REJECT`. | Without room to reason, the grader "corrected" FAIL lines inside its answer (PoC pass 2). |
| G5a | The parser reads only the final block and derives the verdict from its lines. A missing block, text after it, a missing, extra or reordered ID, or a `VERDICT` that disagrees with the lines is no verdict (exit 2). | A model's own VERDICT line contradicted its lines once (PoC pass 1). |
| G6 | `grade-prose.sh <unit>` exits 0 on PASS, 1 on REJECT, and 2 when no verdict was obtained (a malformed reply, a missing line, a killed or stuck leaf). | Exit codes are the API, and the gap between 1 and 2 is load-bearing. |
| G7 | The grader is launched through `supervise.sh`, with its own leaf role, on the model named in the committed `skills/tdd/grader.conf` as a full model id (never an alias). No environment variable overrides it. | Every leaf goes through the supervisor. CI must be able to recompute the model part of a signature (T1), and an alias's meaning shifts between releases. |
| G8 | Each grading records its cost and its per-requirement results in `.tdd/events.jsonl`. | The lane's price must be read from the log, not estimated. |
| G9 | The grader's suites run with a stub `CLAUDE_BIN` covering PASS, REJECT, a malformed reply and a hang. No suite calls a real model. | The plumbing is tested, while the judgement is measured (S1–S3). |

## S: stability (measured by the PoC on 2026-10-17, see `specs/grader-poc.md`; repeated when slice 2 lands)

| ID | Requirement | Why |
|---|---|---|
| S1 | Each requirement in the first three lists is graded twice on unchanged prose, and the two verdicts are recorded side by side. | #489's open question: is a list gradable the same way twice? |
| S2 | A requirement whose verdict flips between the two runs is rewritten until it holds, or dropped. The rewrite is recorded. | A flip means the requirement is ambiguous, not the prose. |
| S3 | The cost per unit is recorded (tokens and $), with a projection for every unit in veri. | It prices the lane before anything depends on it. |
| S4 | The slice ends with a written go/no-go. On no-go, the R slices below do not start. | The substring suites go only once their replacement has been shown to work. |

## T: when grading runs, and the signature that records a PASS

| ID | Requirement | Why |
|---|---|---|
| T1 | A unit's *signature* is a sha256 over four inputs: the unit's text, the `ID` + `Requirement` columns of its list, the grader's prompt template, and the model id read from `grader.conf`. | It names exactly the inputs that can change a verdict, and each one is committed, so CI can recompute it. |
| T2 | `Why` cells are not part of the signature. | The grader never sees `Why`, so editing one cannot change a verdict. |
| T3 | Signatures are recorded in `skills/<skill>/GRADED`, one line per unit: unit, signature, date, and the grading's event id. | One file per skill, so it is reviewable and traceable to the run that graded it. |
| T4 | Only `grade-prose.sh` writes a signature line, and only when every requirement of the unit PASSes. | The signature means "an agent approved this pair", nothing less. |
| T5 | When a requirement changes, the unit is regraded against its whole list, not only the changed IDs. | A changed requirement can interact with unchanged ones. |
| T6 | `prose-owed.sh` lists every unit whose current signature differs from its recorded one, or that has no recorded one. It is deterministic and calls no model. | This is the "unchanged, so no regrade" decision, made as pure logic. |
| T7 | `make unit`, and so CI, fails when `prose-owed.sh` lists anything, naming each unit. A unit without a requirements list is never owed. | Prose and requirements cannot drift apart on `main` unnoticed, whoever merges and however. |
| T8 | CI never runs the grader. | It would bill a model call on every push, and CI holds no model credentials. |
| T9 | `grade-prose.sh --owed` grades exactly the units `prose-owed.sh` lists. | A grader prompt or model change makes every unit owed, by T1, and is paid for deliberately. |
| T10 | `prose-owed.sh` also fails on an *orphan*: a `GRADED` line whose unit no longer exists, for example after a heading rename. | Nothing is silently left behind. A rename shows up as a new owed unit plus an orphan line. |
| T11 | When two branches touch one unit, their `GRADED` lines conflict on rebase. The conflict is resolved by regrading on the rebased tip, never by hand. | The combined prose is a new pair that nobody has graded. |
| T12 | Graded prose changes only in a ⟦skill-edit⟧ step (K). Red, Green and Refactor leaves never edit a unit that has a requirements list, and `make unit`'s owed check fails a branch whose edits to such a unit were not graded and signed. | The grader, not a substring suite, checks prose; the owed check catches an edit that bypassed the step. |

Considered and set aside: no signature, with `make merge-gates` grading whatever the branch diff
touches. It needs no new file, but it is enforced only where the gate runs (a merge from the
GitHub UI skips it), it records nothing that shows a grading happened, and it cannot see a
grader change. A signature can be recomputed by hand without grading; the threat it guards
against is forgetting, not forgery.

## R: removing the substring suites (refactor, built by veri under `/tdd`)

| ID | Requirement | Why |
|---|---|---|
| R1 | A test whose assertion is "this prose contains or omits text X" is deleted, but only after the unit it reads has a requirements list carrying that assertion's intent and grades PASS. | This is Parallel Change: the replacement exists before the old check goes. |
| R2 | A test that asserts a fact the code depends on stays. Examples: a script SKILL.md names exists, a phase name is one the code accepts, a heading a parser reads exists, a launch line runs against a stub. | Those facts are deterministic, and a grader would check them worse. |
| R3 | Each removal issue lists, per deleted case, the requirement ID that now carries it, or says why it carries nothing. | A deleted guard must be traceable. |
| R4 | Helpers, guards and `affected-suites` rules that served only deleted tests are deleted with the last test that used them. | Prevents dead code. |
| R6 | Removal is cut by unit, so each removal issue covers the suites that read one unit. | Keeps issues small, and aligns with PRD 010's split of SKILL.md into event files. |
| R7 | A unit's requirements list is added in a ⟦skill-edit⟧ step (K) and must grade PASS on the prose as it already is, before any suite that reads the unit is deleted. | The list is the replacement, and it has to hold before the old check goes. |

---

## K: the ⟦skill-edit⟧ step (prose; its helpers are G and T)

| ID | Requirement | Why |
|---|---|---|
| K1 | Graded prose changes in a ⟦skill-edit⟧ step of an ordinary `/tdd` run. The planner emits one for each criterion that changes a unit with a requirements list; the conductor runs it by the procedure in `skills/tdd/SKILL-EDIT.md`, which it reads only when such a step comes up, in place of Red, Green and Refactor. | One issue and one PR per change, code and prose together, with no second loop and no post-merge step. The conductor gains a pointer, not a procedure. |
| K2 | One step edits one unit. A change spanning several units is planned as one step per unit, each with its own K3–K8. | Keeps each grading to one unit's context. |
| K3 | The requirements diff (rows added, reworded or dropped; IDs stable) is written in the issue, under `## Requirements`, and is approved when the issue is filed. The step's author applies it as written and adds no rows of its own. A step whose issue states no requirements diff changes only prose, graded against the existing list. | The list is the spec, and it is the human's; approving it at filing keeps an unattended run from waiting on a person. |
| K4 | Before editing prose, the step grades the current prose against the new list. If the changed IDs already PASS, it records that and the step ends without editing. | This is the Red: it proves the change is a change. |
| K5 | The author updates the prose, seeing the requirements and the grader's FAIL reasons, never a `Why` cell. | |
| K6 | The grader judges the new prose against the whole list. On REJECT the author revises, up to a budget (`VERI_SKILL_EDIT_BUDGET`, default 3). When the budget is spent, the run bails as for an exhausted revise, naming the failing IDs. | |
| K7 | Before signing, the step checks that the author's diff does not touch `GRADED`. If it does, the attempt is rejected. | Only the grading may sign (T4). |
| K8 | On PASS, the step writes the signature (T4) and commits the list, the prose and `GRADED` together as the step's commit. Before the PR is readied, after the run's last rebase, every unit the run signed is regraded on the rebased tip; a REJECT there is handled as a red full suite. | A later step or the rebase can change a signed unit (T11); the signature has to hold for the tip that merges. |
| K9 | A resumed run redoes an unfinished ⟦skill-edit⟧ step from its start, with its budget reset. | A step takes minutes, and partial-step resume costs more than a redo. |
| K10 | The step changes nothing outside the unit's own file and requirements list, except its `GRADED` line. | |

Considered and set aside: a separate `/veri-skill-edit` loop, run outside `/tdd` with the human approving each requirements diff. It kept the conductor unchanged, but split every change that needs code and prose into two issues in sequence, needed its own lane and label, and left the issue open past its code PR. The requirements diff is approved at filing instead (K3), and the procedure lives in a file the conductor reads only when needed.

## P: principles every operator skill obeys (stated once, in `operator/PRINCIPLES.md`)

| ID | Requirement | Why |
|---|---|---|
| P1 | A skill re-reads the state it decides on (ledger, `.tdd/`, `solvable-issues.sh`, PR state, processes) at each decision, never from its own memory. | This makes a context reset cheap. Rules were lost across resets at least 4 times. |
| P2 | A handoff carries state only, and the rules come from the skill on resume. | Same reason as P1. |
| P3 | Any waiting is done by a script that blocks until an actionable event and returns one line. No agent polls on a timer. | Each "still fine" tick costs tokens and changes nothing. |
| P4 | Every turn shows text, sized by the event. An important event (a run started as `Started #N — title`, a bail or stall, red CI, a merge landed, a cost or plan surprise) gets one line of fewer than ten words. Every other event (a re-arm, a conductor start the dev session already announced, a merge already reported, a routine message from the dev session, an ack, a progress check, a watch expiry) gets a single `.` and nothing else. A human decision is written in full, asked once when it arises; later events never repeat it, and it is restated in full, never as a pointer, only when the human asks what is pending or its facts change. When a coordinator is attached to the dev session, an event that earns the dev session text is one message to the coordinator, carrying facts only and never a pasted log or issue tail (P6); the human gets only the `.` from the dev session about it unless the dev session is stopped on a human decision. | "No need to narrate everything… tokens I'll never read." Mario asked four times for silence on routine watch events. 2026-10-20: the pending list was re-printed on about 15 routine events — "one would have sufficed"; the same day the mu dev session recapped every coordinator message to Mario as well. 2026-10-21: an empty turn makes the harness ask for visible output, so "." for routine and under ten words for important (PR #2011). |
| P5 | A turn never ends while work is takeable. A turn that stops names why: queue empty, or the pending decision — once, by the turn that stops on it, not by every later routine-event turn. | An ended turn stalled #131 for 36 minutes. |
| P6 | Raw reads (leaf logs, diffs, issue sweeps) go to a subagent on the cheapest adequate model, which returns ≤10 lines. A leaf `.out` is never printed. | Keeps the session's context O(1). |
| P7 | A cost is read from a report's `\| total \|` row, never by summing phase rows. | Summing double-counted and wrongly parked #388 and #409. |
| P8 | Lowering the conductor count stops no live run. The next exit is simply not refilled. | Running work is never wasted. |
| P9 | Launch order is `solvable-issues.sh` order minus the issues with a live conductor. Any override is explicit and written down. | Prevents a duplicate launch (#753) and silent reordering. |
| P10 | An exit with no closing comment is checked for a usage limit or Mac sleep before it is treated as a bail. | A limit and sleep both look like silent exits. |
| P11 | All writes stay in the project repo. A fix that belongs elsewhere is reported, not made, and every subagent brief says so. | Repo boundary. |
| P12 | No skill names a fact specific to veri's own repo. Project specifics come from the target repo's CLAUDE.md. | The skills operate veri on any repo. |
| P13 | A message to another session (the coordinator, the dev session, or another machine's coordinator) is self-contained (no option letters, no references only the sender saw) and is sent with `SendMessage` by the skill itself. Only when delivery is held does the human get the message, as one fenced code block per recipient, named above it. A comm check is the message `ping`, answered `pong`; every other message between operator sessions (instruction, ruling or report) is answered, in both directions, with a reply starting `ack`, or with the ruling or instruction it prompts; an `ack` is not answered. Until that reply arrives the message is unconfirmed: a successful send is not a reply. The `ack` goes to the sender, never as text to the human. | "dev thread does not know what a or b means." "why didn't you just send it yourself?" A send that reached a held inbox looked delivered. 2026-10-20: the coordinator left the dev session's reports unanswered — "when getting a message from dev do you not ack?" |

## D: `veri-dev`, run the dev session

| ID | Requirement | Why |
|---|---|---|
| D1 | Invoked as `/veri-dev [<lane>] [N] [--resume <file>]`. N defaults to 1. It carries standing merge permission in the project repo for the runs it finishes; it never merges in another repo. | Mario, 2026-10-18: both operator skills always include merge permission. |
| D2 | It keeps exactly N conductors running while the solvable list is non-empty. | Idle slots were the recurring waste. |
| D3 | Each conductor is a detached `run-conductor.sh <n>`, never a conductor run inline. | An inline conductor costs ~60k tokens per issue in the session. |
| D4 | It launches the next issue only after the previous launch's ledger exists. | A claim appears only ~10 minutes into a run. |
| D5 | On each exit it routes by fact: ✅ Done → review, then `veri-merge` on OK; a bail → `veri-bail`; no closing comment → P10. | |
| D6 | After every merge, park or exit it recounts and refills to N. | |
| D7 | It applies the coordinator's changes to N or to the order at the next slot decision. | |
| D8 | It stops and asks only for: red CI it cannot fix, a ⟦human-owed⟧ step, an unresolvable conflict, a decision a ledger step asks for. | |
| D9 | It does not file, groom or reprioritise issues, and does not edit veri's scripts. | Those are the coordinator's job, and a veri fix is an issue for veri. |
| D10 | Where it describes reporting to the coordinator, it says that with a coordinator attached each event P4 lets it speak about goes to the coordinator, not to the human, unless it stops and asks (D8). It says so as a pointer to P4, never a copy of P4's rule. | 2026-10-20: the mu dev session re-stated a pending decision to Mario about 15 times. A copied rule drifts from P4. |

## C: `veri-coord`, run the coordinator

| ID | Requirement | Why |
|---|---|---|
| C1 | Invoked as `/veri-coord [<lane>] [--resume <file>]`. | |
| C2 | It launches no conductor. It carries standing merge permission in the project repo: its own PRs, and any finished run that meets `veri-merge`'s conditions (M2, M13) once its review is OK. It never merges in another repo. | The roles stay separate. Mario, 2026-10-18: both operator skills always include merge permission. |
| C3 | It watches through the P3 script, and re-arms with a single `.` (P4). Routine events, watch expiries and its own progress checks get a single `.`, and never re-ask a pending decision. | 2026-10-20: the pending list re-printed on about 15 routine events — "one would have sufficed". |
| C4 | It instructs the dev session through `SendMessage` and tells the human in one line that it did. It answers every dev-session report with an `ack`, or with the ruling the report prompts. | "why didn't you just send it yourself?" 2026-10-20: "when getting a message from dev do you not ack?" |
| C5 | Decisions go to the human. The dev session receives facts and instructions. | |
| C6 | It owns: order overrides, N changes (including timed ones), one-resume budget raises, filing (`veri-file`) and grooming (`veri-groom`). | |
| C7 | It proposes `priority` for issues that make future runs cheaper. | |
| C8 | Unattended, it sends the dev session only the message kinds the human approved (default: refill an empty slot). | |
| C9 | It never fixes veri by hand. It files the issue. | "why did you fix it instead of creating an issue". |

## M: `veri-merge`, land one finished run

| ID | Requirement | Why |
|---|---|---|
| M1 | Invoked as `/veri-merge <issue-or-PR>`. It merges with the standing permission `veri-dev` and `veri-coord` carry in the project repo, or with explicit permission; never in another repo. | |
| M2 | It merges only when all of these hold: the last comment is ✅ Done; the ledger has no unchecked step and no `⟂ refactor pending`; every ⟦human-owed⟧ line is ticked. | |
| M3 | An unticked ⟦human-owed⟧ line gets one read-only review subagent. NOT OK goes to the human. | |
| M4 | It holds the merge lock from the first write to the last, and releases it on every exit path. | |
| M5 | If `main` moved, it rebases and force-pushes with `--force-with-lease` pinned to the recorded sha. | The bare form silently clobbers. |
| M6 | An empty or missing CI rollup is not a pass. | |
| M7 | The CI wait is capped at 2× the average of the last 5 runs, and at 10 minutes. | "30 min is too much." |
| M8 | A zero-step CI failure with a payments annotation goes to the human as billing. | |
| M9 | It runs `make merge-gates` when the repo has that target, and refuses to merge while `prose-owed.sh` lists any unit (T6). | |
| M10 | Deleting the branch, cutting the tag and removing the worktree each happen only after `state == MERGED` is read. | Deleting an open PR's head closes it (PR #74). |
| M11 | The tag is `vN.M`, chosen with `--sort=-v:refname`, with the capability in the issue's words as its message. | Lexically `v0.9` > `v0.10`. |
| M12 | It reports one line: PR url, merge sha, tag. | |
| M13 | It does not merge a run that ended with an open question for the human. | Merging would answer the question for them. |

## H: `veri-handoff`, reset a role's context without stopping runs

| ID | Requirement | Why |
|---|---|---|
| H1 | Invoked as `/veri-handoff dev\|coord`. Resume is `/veri-dev --resume <file>` or `/veri-coord --resume <file>`. | |
| H2 | For the dev role, it refuses while a merge is in flight, the lock is held, or a launch is half done. | |
| H3 | It writes the handoff to `.tdd/handoff-<role>.md` in the main clone. | `/tmp` and scratch dirs vanish mid-run. |
| H4 | It carries: time, main sha and tag, live conductors (issue, step k/n, phase, cost), parked runs with their reason, PRs awaiting merge, N and any timed change, overrides and one-off permissions with their expiry, pending decisions. | |
| H5 | It carries no rule that the role's skill states (P2). | |
| H6 | It is ≤40 lines, and every item names its issue number and title. | |
| H7 | It stops no conductor. | Conductors are detached and outlive both sessions. |
| H8 | It prints the resume command in a fenced block. | |

## A: `veri-status`, progress since the last ask

| ID | Requirement | Why |
|---|---|---|
| A1 | Invoked as `/veri-status`. It reports what changed since the previous ask, whose time is kept in `.tdd/status-last`. | |
| A2 | Sections, in order: **Landed** (PR, tag, capability) · **Running** (per issue: awake wall time, steps k/n, phase, cost, model split) · **Queue** (counts by label, blockers, drain ETA at the current N) · **Waiting** (ready PRs, empty slots, bails, decisions). | The format Mario specified twice. |
| A3 | Every ETA comes from observed rates and carries a range. | |
| A4 | It reads `status.sh --json`, `metrics.sh`, `git tag` and `gh`. More than three reads go to one subagent. | |

## Q: `veri-report`, the state of every active PRD

| ID | Requirement | Why |
|---|---|---|
| Q1 | Invoked as `/veri-report`. It reports on every active PRD: an open issue whose title starts `PRD <nnn>`, a draft included. | "how is prd009 going?", then "gimme a status of all active prds". |
| Q2 | Per PRD: the issues solved, the issues left, an ETA under the current plan, and how many issues are still owed (work the PRD names that no issue covers yet). | The operator's four questions, asked together. |
| Q3 | A PRD's children are the issues whose title starts with its `PRD <nnn>` and the issues its body or comments link, the PRD itself excluded. The ETA counts only the lanes whose label the open children carry, at the observed per-issue rate of those lanes, and is a range. | PRD 009's children carry the PRD in their titles; PRD 011's are linked from its body. A PRD no lane holds has no ETA, and it says so. |
| Q4 | The owed count is an estimate with the PRD sections it comes from named, never a bare number. It reads the PRD text through one subagent, which returns the sections that have no issue. | Filing is the coordinator's call; the report only sizes it. |

## B: `veri-bail`, triage a stopped run

| ID | Requirement | Why |
|---|---|---|
| B1 | Invoked as `/veri-bail <issue>`. `veri-dev` calls it on every exit that is not ✅ Done. | |
| B2 | It classifies from facts before acting: usage limit, sleep, killed-stuck, a budget, revise-exhausted, red baseline, a ledger question. | Not from the comment's wording. |
| B3 | A usage limit or sleep is not a bail: it saves any uncommitted leaf edit as a patch, restores the tree, and resumes when usage is back. | |
| B4 | A first real bail is resumed once, with `VERI_NEW_SKILL=1` when the fix it needs landed after its launch. | |
| B5 | A second bail is parked: one issue comment with the cause and what would unblock it, then the next issue is taken. | |
| B6 | Budget raises and ledger amendments come only from the coordinator or the human, and apply to that one resume. | |
| B7 | It leaves the run's logs in place. | |

## X: `veri-stop`, stop runs without wasting work

| ID | Requirement | Why |
|---|---|---|
| X1 | Invoked as `/veri-stop [<issue>\|--all] [ledger\|leaf\|now]`, default `ledger`, mapped to `stop-run.sh --mode`. | The three grades Mario asked for. |
| X2 | After each conductor exits, it shows a clean tree, an empty `@{u}..HEAD` and a committed ledger, and reports where each run would resume. | Nothing should exist only locally. |
| X3 | It is never used to lower N (P8). | |

## F: `veri-file`, file a bug or refactor veri can take

| ID | Requirement | Why |
|---|---|---|
| F1 | Invoked as `/veri-file bug\|refactor [<one line>]`. It replaces `tdd-fix` and `tdd-candidates`. | One filer. |
| F2 | For a bug, it asks only for what the line left out among: happened, expected, steps, environment. | |
| F3 | A refactor's acceptance criteria are structural predicates. | |
| F4 | `## Blocked by` holds only blocker lines or `None.`. | Every `#N` in that section blocks. |
| F5 | `Test command:` appears once, on the last line. | |
| F6 | A sweep (the same fix at N sites) has one covering criterion plus its guard's go-red criterion, and the sites are listed under Problem. | #1037: per-site criteria cost $60 and 17 steps. |
| F7 | It adds the opt-in label only when the human said to take the issue. | The label alone opts an issue in. |
| F8 | Before filing, it searches for duplicates and related issues, and names any follow-ups. | "why did you not include that in the initial filing". |
| F9 | It checks that every input a criterion names exists, and that the criterion's literal rule meets its goal. | Three coordinator-written criteria missed their goal. |
| F10 | It reports the url and whether the issue is now solvable. | |

## GR: `veri-groom`, triage, label, prioritise, split

| ID | Requirement | Why |
|---|---|---|
| GR1 | Invoked as `/veri-groom [<issue>...\|--unlabelled\|--refactor-owed]`. | |
| GR2 | One read-only subagent returns one line per issue: ready / needs-split / gone / duplicate / needs-human, plus proposed labels. | |
| GR3 | Mechanical outcomes are applied: labels, a close with a reason, `Blocked by` fixes. | |
| GR4 | A split or a criteria rewrite is shown to the human first unless they said "go". | |
| GR5 | `--refactor-owed` classifies each item GONE / FOLDS-INTO-OTHER / LIVE on `main`, consolidates the live ones into one issue per module, and closes the sources. | ~5–6 such items are filed per day. |

---

## Deferred to phase 2

PRD grilling, PRD → issues, the cloud-trial loop, and the second-machine work carve.
