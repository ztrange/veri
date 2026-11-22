# Audit: the 32 "production code no test requires" verify-green REJECTs

Source: `~/.veri/runs/ztrange-veri-dashboard/{13,18,19,26,27,28}.jsonl` (the `verdict` events named
`verify-green` with verdict `REJECT` whose reason does not open with `MISSING_TEST`, each paired with the
last developer `launch` before it), the leaf transcripts under
`~/.claude/projects/-Users-marioferreira-Documents-repos-personal-veri-dashboard--tdd-wt-<n>/`, and the
green diffs the reasons name. Measured 2026-11-21; skill pin 647e07a4a6. The journals and transcripts live
on the development Mac only.

Conventions of the table:

- **Leaf**: the developer leaf launched last before the REJECT (`revise-green-n` is `develop-revise`
  redoing green). 6 of the 32 follow a `revise-green`, 26 a `develop-green`.
- **Kind on the probe's list**: the list in `develop-green.md` step 2 is branch, guard, default, flag,
  parameter, `__main__` block, flush, encoding line. A condition clause (`x &&`, `|| x`, `{{if}}`,
  `{{with}}`) counts as a guard. Loop order, loop exits (`break`), state resets, bookkeeping
  assignments, wrapper expressions, markup literals, route prefixes and table entries are not on it.
- **Probe in transcript**: any command of the leaf that removes added code and reruns a suite, the
  `.orig` copy included. Searched: every Bash command and every Edit of the leaf. `no` means none.
- **Criterion asked**: the step's criterion text names the behaviour the item implements.
- "in tree" marks a leaf whose report says the implementation was already in the working tree when it
  started and whose transcript holds no write: it ran the suites and reported (8 `develop-green` leaves).

| # | Run | Step | Leaf | Rejected item | Kind | On probe's list | Probe in transcript | Criterion asked |
|---|-----|------|------|---------------|------|-----------------|---------------------|-----------------|
| 1 | 13 | VERI_HOME unset reads `~/.veri` | develop-green | `if err != nil {return nil, err}` on `os.UserHomeDir()` | guard | yes | no | no |
| 2 | 13 | conductor.pid on line 1, live pid is running | develop-green | (1) `strings.Cut` line-1 pid extraction; (2) `continue` on `Atoi` failure of the journal name | (1) parse expression; (2) guard | (1) no; (2) yes | no | (1) yes, "on line 1"; (2) no |
| 3 | 13 | same | revise-green-1 | `err != nil \|\|` before `syscall.Kill`; `if err != nil {continue}` after reading the pid file | guard, guard | yes | no | no |
| 4 | 13 | ending-event check, pid from line 1 only (added) | develop-green (in tree) | "two added guards" (the reason lists none) | guard | yes | no | not determinable |
| 5 | 13 | Running section on `/` | develop-green (in tree) | `{{if .Running}}` | guard | yes | no | no |
| 6 | 13 | stale run in its own section | develop-green (in tree) | `<h2>Stale</h2>` heading | markup literal | no | no | yes, "marked stale" |
| 7 | 13 | awake wall time | develop-green | `\|\| e.Awake == nil` (and its pointer type) | guard | yes | no | no |
| 8 | 13 | awake wall time | revise-green-1 | `filepath.Base(p) != issue+".jsonl"` `continue` in `AwakeWall` | guard | yes | no | no |
| 9 | 13 | steps done of planned | develop-green | `if json.Unmarshal(...) != nil {continue}` in `Steps` | guard | yes | no | no |
| 10 | 13 | PASS and REJECT counts | develop-green | `if e.Event != "verdict" {continue}` in `Verdicts` | guard | yes | no | yes, "the `verdict` events" |
| 11 | 13 | unknown event kind shown | develop-green | seven `case` entries (`plan`, `usage`, `verdict`, `done`, `bail`, `stop`, `exit`) | table entries | no | no | in part: a known list is implied, its members are not named |
| 12 | 13 | SSE stream | develop-green | `if home == "" {... ~/.veri}` fallback in `streamEvents` | default | yes | no | no |
| 13 | 13 | SSE stream | revise-green-1 | initial-offset loop; `len(data) <= offsets[path]` guard (items from the next revise's outcome; the reason cuts after "two additions") | loop; guard | in part | no | no |
| 14 | 13 | SSE stream | revise-green-2 | `offsets[path] = len(data)`; `strings.TrimSpace(...)` around the line | bookkeeping assignment; wrapper expression | no | no | no |
| 15 | 13 | SSE `data:` event (added) | develop-green | `int64(len(data)) <= sizes[p]` half of a guard; baseline `os.Stat` loop; `"GET "` route prefix | guard; loop; route prefix | in part | no | no |
| 16 | 18 | non-integer journal names skipped | develop-green (in tree) | `err != nil \|\|` in the skip condition (`n <= 0` already covers it) | guard | yes | no | no: the behaviour (`abc.jsonl` skipped) is asked, the guard is a redundant second form of it |
| 17 | 18 | one warning line for unknown kinds | develop-green | `{{with index $p.Events .}}` around the warning | guard | yes | no | no |
| 18 | 18 | age of Stale entries | develop-green | `e.TS != 0` in `LastTS` | guard | yes | no | no |
| 19 | 18 | `N older` in Stale | develop-green | `{{if .StaleOlder}}` | guard | yes | no | no |
| 20 | 19 | client-side card refresh | develop-green | `fresh[i] &&` in `page.js` | guard | yes | no | no |
| 21 | 26 | Parked Cause and Unblock | develop-green (in tree) | newest-first loop in `parkedReason` | loop order | no | no | no (belongs to a later step) |
| 22 | 26 | Bailed phase and class | develop-green (in tree) | reverse loop in `bailedReason` | loop order | no | no | no (belongs to a later step) |
| 23 | 26 | poll every 60 s | develop-green | `polled.IsZero() \|\|` in the poll guard | guard | yes | no | no |
| 24 | 26 | `GitHub unreadable since` line | develop-green | `pl.downSince = ""` in the success branch | state reset | no | partial: one sibling line, `pl.project.GitHubDownSince = ""`, was removed and the suites rerun in the same command as the final pair; `pl.downSince = ""` was not | no (belongs to a later step) |
| 25 | 27 | RP1 Recent section | develop-green | `e.Event == "done" &&` in `Recent` | guard | yes | no | yes, "a `done` event" |
| 26 | 27 | RP1 Recent section | develop-green (in tree) | `break` after `issues = append(issues, n)` | loop exit | no | no | no |
| 27 | 27 | RP1a (added) | develop-green | `break` after the first `done` event | loop exit | no | no | no (dedupe belongs to RP1b) |
| 28 | 27 | RP1a (added) | revise-green-1 | `if n <= 0 {continue}` in `Recent` | guard | yes | no | no |
| 29 | 27 | RP1a (added) | revise-green-2 | `e.Event == "done" &&` in `Recent` | guard | yes | no | yes, "a `done` event" |
| 30 | 27 | Recent section (added) | develop-green | 7-day cutoff; `e.Event == "done"` filter; `break` in `RecentDone` | guard; guard; loop exit | in part | no | in part: cutoff and `done` yes, `break` no |
| 31 | 27 | RP2 PR link | develop-green (in tree) | done/merged filter in `RecentPR`; literal `#` in the link text | guard; markup literal | in part | no | no |
| 32 | 27 | RP4 `N older` | develop-green | `{{if .RecentOlder}}`; `ts != 0 &&` in `OlderDone` | guard; guard | yes | no | no |

## What explains the REJECTs

Counts over the 32 rows. A row can sit under several causes, so the counts overlap and do not sum to 32.

| Cause | REJECTs | Rows |
|-------|---------|------|
| The probe was not run | **31** | all but 24; 25 `develop-green` and 6 `revise-green` |
| The probe was run and missed the item | 1 | 24 (a one-line removal that left its sibling) |
| The item's kind is not on the probe's list | 13 (8 with every item off the list, 5 with one off) | 2, 6, 11, 13, 14, 15, 21, 22, 24, 26, 27, 30, 31 |
| The code was written by `revise-green`, whose prompt carries no such rule | 6 | 3, 8, 13, 14, 28, 29 |
| The criterion's text asked for the item | 7 (4 fully, 3 in part) | 6, 10, 25, 29; in part 2, 11, 30 |

The largest is **the probe was not run**: 31 of 32. Every one of the 26 `develop-green` leaves was
launched with the probe in its prompt, and none ran it in full (row 24 removed one line). 19 REJECTs concern items of an
on-list kind (rows 1, 3, 4, 5, 7, 8, 9, 10, 12, 16 to 20, 23, 25, 28, 29, 32): a leaf that had run the
probe would have been told to remove each. The other 13 hold at least one item the list does not name, so
the probe as written would not have asked for its removal.

`.orig` check: of the 95 `develop-green` transcripts of runs 13, 18, 19, 26, 27, 28 and 35, 2 name `.orig`
(both in run 13), as the issue says, and neither belongs to a leaf of the 32 rows.

## The leaves that did not probe

What the transcript shows in the probe's place, for the 25 `develop-green` leaves with no probe
(row 24 aside):

- In 8 leaves the transcript holds no write at all (rows 4, 5, 6, 16, 21, 22, 26, 31): the leaf read the
  working tree and the test, ran the target package or `make test`, then the fast pair, and reported.
  Their code was already in the tree.
- In 10 leaves (rows 1, 2, 9, 11, 12, 19, 25, 27, 30, plus 24) the last action is one Bash command that
  writes the code (a heredoc, a `python3` `replace`, a `sed -i`) and runs the fast pair in the same
  command, so no run sits between the write and the report.
- In 8 leaves (rows 7, 10, 15, 17, 18, 20, 23, 32) the leaf wrote, ran the target package or `make test`
  once or twice to see the case pass (rows 15 and 19 also fixed a failure that run showed), then ran the fast pair.
  Each of those runs is a green check of the whole change, not a removal.
- No leaf copied a file to `.orig`, edited the added code out, or reran a suite against a version with
  an item removed (row 24 aside).
- In their own reports 13 of the 25 say so: "I did not run the probe step" (rows 2, 4, 9, 11, 12, 23, 31),
  "no probes" or "ran no probes" (rows 10, 26), "haven't probed" (row 25), "didn't re-probe" (row 16),
  "did not run the remove-and-rerun probe" (row 17), "(removing the new branch to see if the suite stays green)
  ... I skipped" (row 1). The other 12 do not mention it. The conductor has no report line for the probe, so
  neither answer is read by anything.

Where the probe instruction sits in the prompt the leaf was given: the rendered `develop-green` prompt of
run 13 has 219 lines and about 14.5k characters. The probe is lines 154 to 159, about 10.3k characters in
(70%), inside "What to do" item 2, **after** its first two sentences (iterate against the suite holding the
target case; run one suite through the two included fragments) and ahead of item 3, which
carries the `SUITE:` report line and the fast pair every leaf did run. It opens "Before that run, probe ...", a
sentence that points at "that run", the single-suite run, not at the final pair. The shared preamble
(lines 30 to 33) mentions `.orig` only to tell the leaf how to undo a probe, and the `Report` block asks for
`IMPL_PATH:` and `SUITE:` and nothing on the probe.

The `develop-revise` prompt (196 lines) holds no probe and no minimum rule: its only bound is "Do not
drift beyond what the criterion and the reason require" (line 121). The 6 `revise-green` leaves each removed
exactly what the verifier named and ran the fast pair; none probed the code they left or rewrote.

## Proposed fixes, one per cause

Each is an issue title; no fix is made in this issue.

1. The probe was not run: "develop-green reports a `PROBED:` line naming each added item and the result of its removal rerun, and the conductor refuses a report without it".
2. The probe was run and missed the item: "develop-green's `PROBED:` line is checked against the diff, so an added line with no named removal rerun is sent back before verify-green".
3. The kind is not on the probe's list: "develop-green's probe list names loop order, loop exits, state resets, bookkeeping assignments, markup literals, route prefixes and table entries".
4. The code was written by `revise-green`: "develop-revise.md carries the minimum rule and the removal probe for code a revise-green leaf writes".
5. The criterion's text asked for the item: "verify-green check 4 compares a removable item with the criterion text and, where the text names it, asks for a test instead of its removal".
