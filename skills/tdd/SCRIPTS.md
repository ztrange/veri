# The scripts catalogue

Entries for the scripts in `$S` (`<base directory>/scripts`), moved out of SKILL.md. `$S` is defined there.

- `$S/supervise.sh <name> <cmd> [args...]` — **the leaf launcher.** Spawns `<cmd>` under a
  heartbeat + hard-timeout watchdog, owns the `.tdd/<name>.log` progress log, and returns
  the captured output on stdout. **Exit 0 = success, 1 = leaf-failure, 2 = killed-stuck**
  (hung past the heartbeat window or over the hard timeout, **after** its stuck-retry
  budget). A one-line status goes to stderr. Tunables: `VERI_HEARTBEAT` (silence window s,
  default 180), `VERI_TIMEOUT` (hard cap s, default 900), `VERI_STUCK_RETRIES` (extra
  attempts after a killed-stuck, default 1 — the **liveness** axis, independent of both the
  conductor's verdict-axis `REVISE_BUDGET` and its cost-axis `VERI_REFACTOR_BUDGET`).
  Four more choose the **model** each leaf runs on, resolved here through
  `$S/leaf-model.sh` and passed to `claude --model`: `VERI_MODEL` (every leaf),
  `VERI_MODEL_DEVELOPER` (developer leaves only — `develop-*`, `revise-*`),
  `VERI_MODEL_REVISE` (only the developer leaves that redo rejected work — `revise-*` and
  `develop-exhausted` — beating `VERI_MODEL_DEVELOPER` for them) and
  `VERI_MODEL_VERIFIER` (verifier leaves only — `verify-*`, `verify-pin` included). A role
  variable beats `VERI_MODEL`; all four unset means the shipped defaults: sonnet for first-try
  developer leaves and verifiers, opus for the redo leaves and the conductor. The value goes through verbatim, so an alias (`sonnet`, `opus[1m]`) or a full id
  (`claude-sonnet-5`) both work.
  Because leaves **stream** (below), the default
  `VERI_HEARTBEAT` is a real silence window — a working leaf keeps it fresh, a genuinely
  hung one trips it — so just use the defaults; no need to pin heartbeat to the timeout.
  **Every leaf is launched through this — never call `run-leaf.sh` or `claude` directly.**
  It records its own final code in the completion file `.tdd/<name>.exit` on **every** path,
  killed-stuck included — that is what makes a detached launch waitable. And because a
  killed-stuck leaf is relaunched (`VERI_STUCK_RETRIES`), one call can take **more than one**
  `VERI_TIMEOUT` of wall time, which is why the wait below loops rather than naming one long
  timeout.
- `$S/detach-leaf.sh <cmd> [args...]` — **the detaching half of a detached launch.** Runs
  `<cmd>` as the leader of a **new session**, and so of a new process group, then returns at
  once. Every leaf launch below goes through it, and none uses `nohup` — *Launching a leaf*
  says why. Redirections go on the call as usual — the launched process inherits them.
- `$S/wait-leaf.sh <name> [max-seconds]` — **the foreground half of a detached launch.**
  Blocks polling for that completion file and exits with the code recorded in it as soon as
  it lands (0 / 1 / 2, the launcher's own contract), or **exit 3** — nothing to report yet —
  once `max-seconds` pass with no completion file. The default is 540 s, comfortably inside
  Claude Code's 10-minute cap on a single foreground Bash call. On a **3, call it again**:
  the leaf is still running. A 3 with no leaf running means no result was ever recorded —
  never success. A **2** also means the supervisor died without recording a status: no
  completion file, and the pid in `.tdd/<name>.pid` no longer runs a supervisor for that
  name. It takes the killed-stuck branch like any other 2.
- `$S/run-leaf.sh <prompt-file|-> [claude args...]` — the inner leaf invocation. Runs
  `claude -p --output-format stream-json` so the leaf **streams events as it works** (that
  is the supervisor's heartbeat), then appends the clean final result. You always run it
  *via* `supervise.sh`, not on its own. Tunable: `VERI_LEAF_TOOLS` — when set, passes
  `--tools <value>` to `claude` (`grade-prose.sh` sets it empty, so its grader has no tools).
  It always sets `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` in `claude`'s environment, and sets
  `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` to the leaf's effective timeout, the one
  `supervise.sh` enforces (`VERI_TIMEOUT`, else the run's `.tdd/issue-<n>-timeout`, else 900 s),
  unless the caller already set them.
- `$S/extract-result.sh` — pulls the final result text out of a leaf's stream-json (used
  by `run-leaf.sh`; passes plain text through unchanged).
- `$S/build-develop-prompt.sh <red|green|refactor|cover|transform|diff|structural|predicate|revise|exhausted|reconcile|over-budget|rebase|replaces-report|red-contradicted|red-repair|red-missing|red-supersede|expand|migrate|contract-a|contract-b> …` — assemble a **developer** leaf's prompt from a
  versioned template: `red <spec-file> <step-text> <test-cmd>`, `green <spec-file>
  <step-text> <test-cmd> <test-path> <target> <fast-cmd> [<owed-cases>]` (the optional 8th argument
  is the named cases still owed for deletion), `refactor <spec-file> <step-text>
  <test-cmd> <touched-files>`, `revise <phase> <spec-file> <step-text> <test-cmd>
  <reason-file>`, `red-repair <case> <report-file> <superseded>…` (the Red leaf that repairs one case the step's own Red wrote, edited in place; never creates a suite), `$S/build-develop-prompt.sh red-missing <spec-file> <step-text> <test-cmd> <reason-file>` (the Red leaf that adds the one case pinning the `MISSING_TEST:` behaviour the reason file names, editing no other case). Prints the prompt on stdout; **exit 2** with a diagnostic and **no
  stdout** on an unknown phase or a missing template, spec or reason file — never a partial
  prompt. The mirror of `build-verify-prompt.sh` and its opposite in emphasis: the verifier
  builder is defined by what it **cannot** carry (no rationale parameter, so blindness is
  structural), this one by what it **must** carry — the same instructions on every run of a
  phase, with only the variables changing. **Build every developer prompt with it**; a
  phase's instructions live in its template, not in prose you improvise per cycle.
- `$S/build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <red|green|refactor|pin|plan|rebase|transform|diff> <spec-file> <test-path> [target]` —
  assemble the blind verifier prompt. Used by `verify.sh`; you rarely call it directly.
- `$S/verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <red|green|refactor|pin|plan> <spec-file> <test-path> [target] | diff <spec-file> <branch-base-sha> <step-base-sha>` — the **verify
  verb**: build the blind prompt → launch the verifier leaf **through the supervisor** →
  parse the verdict. Prints the verifier's **reason** on stdout; **exit 0 = PASS, 1 =
  REJECT, 2 = malformed or killed-stuck**. The `pin` phase is the *already satisfied*
  check: the verifier confirms the test passes now, **fails** under a behaviour-removing
  mutation it applies and then reverts itself, and is behaviour-level — the same trivial
  / over-coupled / too-complex bar as `red`.
- `$S/refactor-owed.sh append|applied|not-done|render|list <file> …` — the structural leftovers a step's refactor leaf reports. `append <file> '<STEP>' [<bounds>]` reads the report on stdin; `applied <file> '<transform>' <sha> '<subject>'` records a candidate as applied, `<subject>` being the applying commit's subject, `"$(git log -1 --format=%s)"`, which `render` prints beside the sha so the row stays readable after a rebase rewrites it; `not-done <file> '<candidate>' <reason>` records a candidate the pass did not apply, which `render` shows under `### Not done`; `render <file>` prints the `## Refactor owed` section; `list <file>` prints each structural transform once. Exit **0** done, **1** a write failed, **2** a missing argument or an unknown verb, **3** `render` or `list` found nothing.
- `$S/mutation-parity.sh <pairs-table>` — proves each row of a `⟦replaces-case⟧` pairs table by applying its mutation: **exit 0** all proven, **exit 1** a REJECT, **exit 2** a bail. A row whose mutation no kept case catches prints `MISSING_TEST: <old>: no kept case fails when its mutation is applied` on stderr; saved to a reason file, that line routes through `wrong-test-route.sh` as `missing`.
- `$S/run-verdict.sh [--step "<STEP>"] [--fast-cmd '<cmd>'] <red|green|refactor|pin|plan> <spec-file> <test-path> [target]`
  — the **verdict launcher**: `verify.sh`'s own call, argument for argument, reached as a
  command rather than as a shell string. This is what `supervise.sh verdict-<phase>` runs;
  it passes every argument through untouched and `exec`s the verify verb, so the step title
  travels in argv and its exit code is `verify.sh`'s.
- `$S/parse-verdict.sh` — extracts `PASS|REJECT` + reason from a leaf's output (used by
  `verify.sh`).
- `$S/tick-issue-criterion.sh <n> "<substring>"` — tick a criterion checkbox in the
  issue body (the human-facing mirror).
- `$S/next-unchecked.sh < .tdd/issue-<n>.md` — print the **first unchecked ledger step**'s
  description; **exit 3** when none remain (the loop-done / nothing-to-resume signal).
- `VERI_STEP=<step> $S/wrong-test-route.sh <green-report> <red-test-id>` — routes a green report's `WRONG_TEST:`, or a report carrying `MISSING_TEST:` (a verify-green REJECT reason, a mutation-parity stderr saved to a file, a revise-green report answering `IMPOSSIBLE`): **exit 0** prints `fixture <path> <name>` (a helper, fixture or shared setup function defined in the test file `<path>` that is not a test case), `missing <behaviour>` (a behaviour no test pins; the report file is the `red-missing` brief), `red <case>` (an existing case other than the step's own that the criterion contradicts), `repair <case> <superseded>…` (a case the step's own Red wrote, per its red record or as `<red-test-id>`, with the older cases listed on `SUPERSEDED:` lines) or `supersede <case> <case>…` (two or more older cases named on `SUPERSEDED:` lines, which one `red-supersede` Red updates together), **exit 3** prints `revise`, **exit 2** bad arguments. `missing <behaviour>` is answered on exit 0 until the step's `"kind": "missing"` `reroute` events in `.tdd/events.jsonl` (with `VERI_STEP`) reach `VERI_MISSING_REROUTE_BUDGET` (default 3); then `missing-exhausted <behaviour>` is printed on **exit 1**. The other four routes (`red`, `repair`, `supersede`, `fixture`) stay free only for the step's first reroute of any kind: a later reroute that would take one of them (a `WRONG_TEST:` or `SUPERSEDED:` report) answers `revise` (exit 3) and spends one `REVISE_BUDGET` attempt.
- `$S/pin-fast-tier.sh '<fast-cmd>'` — run the fast tier over the tree a pin would commit,
  from the worktree. Takes the fast command as its one argument. On failure it writes the
  command's output to `.tdd/verify-pin.reason`. **Exit 0 = the command passed, 1 = it failed
  (output in the reason file), 2 = no command given.**
- `$S/pin-recheck.sh <base-sha>` — re-run each recorded mutation whose file the range touches:
  **exit 0** every such pin still goes red, printing any that need a look; **exit 1** a pin
  stayed green under its mutation, or a mutated run did not build, which prints
  `needs a look: <file> (mutation did not build)` on stdout; **exit 2** no answer; **exit 3** no record touches the range.
- `$S/tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase>] .tdd/issue-<n>.md "<substring>"` — check a step off
  in the **committed ledger**, in place (staged + committed together with that step's green
  code). Ticking a `⟦diff-checked⟧` step also re-records, via `tests-frozen.sh rerecord-earlier`, the
  earlier frozen cases its diff changed; **exit 2** can then follow the write of the ledger (the re-record failed). **Exit 3** if no unchecked step matched the substring — the file is left untouched,
  so a green commit that ticked nothing says so instead of reading as done.
  `--refactor-pending` appends ` ⟂ refactor pending` to that same line in the same write, so
  the green commit records the step as **green but not yet tidied**; that is the flag the
  green PASS ticks with, and the one the pin path must tick without — a pinned step runs no
  refactor loop, so a mark left there would never be cleared. A `⟦replaces-case⟧` step's
  deletion green after a pin PASS is a Green: it ticks with the flag and runs Refactor.
  `--phase <phase>` instead appends ` ⟂ <phase> done` to the first open step listing
  `⟦phases: …⟧` that matches, and leaves its checkbox `[ ]`; once every listed phase is marked
  the step reads as `done` to `ledger-steps.sh` and `next-unchecked.sh` skips it. **Exit 2**,
  ledger byte-identical, for a phase the step does not list or one that is not its next unmarked
  phase; also for a step listing `⟦phases: …⟧` ticked without `--phase`, and for `--phase` given
  with `--refactor-pending`. `--phase-owed <phase>` appends ` ⟂ <phase> owed` instead, under the
  same refusals; an owed phase ends the step, so it and every phase after it are never handed out
  again (see the exhausted-contract paragraph in `<base directory>/PHASED.md`). `$S/ledger-steps.sh next-phase < .tdd/issue-<n>.md` prints the first phased step's next
  unmarked phase, **exit 3** when none is left. The cycle loop runs a phased step through
  both — see `<base directory>/PHASED.md`.
- `$S/reorder-ledger-steps.sh .tdd/issue-<n>.md "<step>" before|after "<anchor>"` — the one sanctioned way to change the order of **unchecked** steps, committed on its own as a `plan:` commit; running it is an operator's decision, never the conductor's own.
- `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` — print the **first ticked step whose
  refactor is unverified**: the description of the first `- [x]` step carrying the
  ` ⟂ refactor pending` mark, with the mark stripped, so what comes back is the same text
  `next-unchecked.sh` hands the loop and the tick wrappers match on. **Exit 0** when it
  printed one; **exit 3** with empty stdout when no step carries the mark — every green step
  has been tidied, so a resume has no refactor loop to re-enter.
- `$S/ledger-growth.sh <plan-ledger-file> <ledger-file> | plan-sha | record-existing <ledger-file>` — called by the conductor at each ledger
  commit: compares the ledger with the plan commit's. The plan commit, `<plan-sha>`, is the newest
  `plan: scope` or `plan: rewrite` commit, so after a verify-plan REJECT the rewrite is the
  baseline: `git log --format='%H %s' | $S/ledger-growth.sh plan-sha` prints its sha (**exit 2**
  when the log holds none). Each step line the plan did not hold must match, by equal step text, a
  record `add-ledger-step.sh` wrote: a line of the tracked `.tdd/issue-<n>-added.md` beside the
  ledger (committed with it, so it survives a resume in a fresh worktree) or a `step-added` event
  of actor `add-ledger-step` in `events.jsonl`; and it must carry `⟦added⟧` unless it is a
  `⟦suite-repair⟧`, `⟦ci-repair⟧` or `--planned` insertion. The `⟦added⟧` lines never exceed
  `VERI_STEP_GROWTH` (default 5). Ticks, ` ⟂ refactor pending` and phase marks on planned lines
  are not growth. **Exit 0** when every line passes; **exit 1**, naming each failing line on
  stderr, when one lacks its record or `⟦added⟧`, or the cap is passed; **exit 2** on a missing
  argument, an unreadable ledger or plan file, or a malformed `VERI_STEP_GROWTH`.
  **`record-existing`** — the one-off migration for a ledger that grew before
  the records existed: writes `.tdd/issue-<n>-added.md` beside the ledger, one `- [ ] <step>` line, as
  `add-ledger-step.sh` writes it, for each step line the plan commit (the newest `plan: scope` or
  `plan: rewrite`) did not hold; `⟦suite-repair⟧`, `⟦ci-repair⟧` and `⟦added⟧` lines keep their marks.
  **Exit 0** once the file is written; **exit 2**, writing nothing, when `issue-<n>-added.md` already
  exists (so it runs once per ledger), when the history holds no plan commit, or when the ledger or the
  plan's copy cannot be read.
- `$S/suite-red-resume.sh check <ledger-file> <branch-red-file> <default-red-file> | insert <ledger-file> <branch-red-file>` — decide whether a resume may go on past a red baseline. Each red file lists one suite per line, optionally followed by ` — ` and its first FAIL line; suites compare by the part before ` — `. **Exit 0**, printing the branch-red file, when no branch-red suite is red on the default branch; **exit 1** naming on stderr each suite red on both; `check` reads no event log; **exit 2** with no arguments (a usage line) or an unreadable file. Called by the conductor's resume preflight. **`insert`** inserts one `⟦suite-repair⟧` step, `fix the full-suite failure: ` plus every line of the branch-red file joined by `; `, before the ledger's first unchecked step (after its last done step when none is unchecked), through `add-ledger-step.sh`, so `.tdd/issue-<n>-added.md` and a `step-added` event record it; that script's refusals keep their exit codes (1, 2).
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md "<substring>"` — the counterpart of
  `tick-ledger.sh --refactor-pending`: **strip the ` ⟂ refactor pending` mark** from the first
  ticked step matching the substring, in place, once that step's refactor has been verified.
  Nothing on stdout. **Exit 0** when it cleared the mark; **exit 3** when no ticked step both
  matched and carried it — the file is left byte-identical, because nothing is written unless
  the transform found its line.
- `$S/same-reject.sh <previous-reason-file> <current-reason-file>` — compare the `REASON:` lines of two rejections after collapsing runs of whitespace. **Exit 0** when equal; **exit 1** when they differ; **exit 2** with a usage line when called with no arguments, or when either file is missing or holds no `REASON:` line.
- `$S/add-ledger-step.sh [--planned] [--criterion <k>] <ledger> after|before|instead-of "<anchor substring>" '<text>' […]` — **grow
  the plan mid-run**: insert each text as `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` directly after
  the anchor step, directly before it, or in its place, inheriting the anchor's criterion
  unless `--criterion <k>` names the criterion the added steps serve — any whole number k ≥ 1,
  whether or not a step already carries `⟦criterion k⟧`. `VERI_STEP_GROWTH`
  (default 5) bounds how many `⟦added⟧` steps one ledger may hold, on a **fifth axis** of its
  own — plan growth, never merged with the other four. **Exit 0** = inserted; **exit 1** = the
  budget cannot hold them, so nothing is inserted and every text is appended as a plain bullet
  under a trailing `## Owed steps` heading instead; **exit 2** = the anchor matches no step or
  more than one, the budget is unreadable, or `--criterion` names a k that is
  not a whole number ≥ 1, with the ledger left byte-identical. Every text
  one growth is made of goes in **one call**: the script takes them all at once and reads the
  budget once per call, so a call per text would refuse a third text that one call either fits
  whole or files whole. Every insertion is marked in the log beside the call it made —
  `VERI_ISSUE=<n> VERI_ACTOR=conductor VERI_STEP="$(cat .tdd/issue-<n>.md | $S/ledger-steps.sh current)" $S/event.sh step-added
  anchor='<anchor>' added=<count>` — because a plan that changes with no record leaves the
  log unable to say which steps the run chose for itself; an exit 1 owes the same mark with
  `added=0`, since a step the budget refused is still a decision the run made.
  `--planned --criterion <k>` inserts steps for a criterion no step serves yet, without `⟦added⟧`, so they do not count toward `VERI_STEP_GROWTH` — the resume's own scoping, not discovered growth. The refusals are all **exit 2**, with nothing inserted and nothing filed as owed:
  `--planned without --criterion`, a criterion a ledger step already serves (the script says "already serves"),
  no readable spec file beside the ledger (the script says "cannot read the spec file", naming it),
  and a k that is not unticked in the issue body the run read (an unknown number or a ticked criterion).
- `$S/tests-frozen.sh record <record-file>|--step "<step>" [--red-case <red-test-id>] <test-file>… | check <record-file>|--step "<step>" | check-earlier <ledger> --step "<step>" [--except <case>]… | rerecord-earlier <ledger> --step "<step>" | rerecord-refactored <ledger> <green-sha> | rerecord-rebased <ledger> <pre-rebase-sha> | path "<step>"` — **freeze a step's tests between verify-red and verify-green.** `record --step` digests the given test files and also every test file (`transform-touches-tests.sh`'s rule) differing from `HEAD`: modified, deleted (recorded as deleted, so its deletion is not an unrecorded change) or untracked. With `--red-case <red-test-id>`, `record --step` first checks that the step's own Red case still exists: when it is gone (deleted, or its test file deleted) it exits 1, writes no record and names the deleted case; otherwise it records as without the flag. `check --step` exits 1 naming a recorded file whose digest changed, and also naming a test file outside the record that now differs from `HEAD`; a recorded-deleted file that exists again, and a tracked test file deleted after the record, are named too; a changed non-test file is never named. Exceptions: a `⟦replaces-case⟧` step may change the suite it names (any other unrecorded test file is still flagged), a `⟦guard-subject: <path>⟧` step may change the file it names (a guard suite or sourced test helper; any other unrecorded test file, the case Red wrote included, is still flagged), and a `⟦suite-repair⟧` or `⟦ci-repair⟧` step is never frozen, `record` writing nothing and `check` exiting 0. `rerecord-earlier` is run by `tick-ledger.sh` for a `⟦diff-checked⟧` step: it rewrites the earlier steps' frozen records of the cases that step's own diff (step base..HEAD) changed, at their content at HEAD, so a later `check-earlier` passes; any other step exits 3. `rerecord-refactored <ledger> <green-sha>` is run only after a verify-refactor PASS: it re-records every ticked step's frozen case that the refactor (the commits past `<green-sha>`) changed when the case kept its title, its assertion lines are identical modulo whitespace, and its body at `<green-sha>` matched the record; any other case is left as recorded, so `check-earlier` still refuses it. Exit 0 done; 3 nothing done because `.tdd/verdict-refactor.exit` does not hold 0; 2 no answer. `check-earlier`'s stdout line for a case changed by a `refactor:` commit says the record is stale against a verified refactor, rather than that a frozen case was edited. `rerecord-rebased <ledger> <pre-rebase-sha>`: for every ticked earlier step's recorded case whose body at `HEAD` differs from its record, it re-records the case at its `HEAD` body when its body at `<pre-rebase-sha>` matches the record and its body at `HEAD` equals its body on `origin/<default>`, and otherwise leaves that record untouched and names the case. Exit 0 every stale record re-recorded; 1 at least one stale case refused, each named on stdout as `<case> (<owning step>)`; 2 no answer (bad arguments, an unreadable ledger or record, a failing `git show`, a record that cannot be written); 3 no earlier record is stale, or the ledger file does not exist (a ledger that exists but cannot be read stays exit 2). For the other verbs, exit 2 = no answer (bad arguments, record missing or malformed; for `rerecord-earlier` also a ledger no commit touches, a failing `git show` of a recorded file, or a record that cannot be written).
- `$S/scope-check.sh <ledger> <repo-root>` — the check the conductor runs before the plan commit. Exit 0 = every named test module is existing or free; exit 1 = a new `test_<x>.py` names a basename already under `tests/py` (stderr names both paths), or a step line carries more than one `⟦criterion k⟧` tag (stderr names the step); exit 2 = bad arguments.
- `$S/classify-bail.sh <cause>` — deterministically classify a bail cause
  (`killed-stuck`/`no-verdict` → `system`, `revise-exhausted`/`missing-reroutes-exhausted` → `process`; unknown → exit
  non-zero). Used in the bail step in `<base directory>/BAIL.md` so the classification is consistent, not ad-hoc.
- `$S/stop-requested.sh [--clear]` — **has an operator asked this run to stop, and how?**
  Run from the worktree, it reads `.tdd/stop`. **Exit 0** = a stop was requested: the mode —
  `at-ledger`, `at-leaf` or `now` — is printed on stdout and nothing else, so capture it and
  enter *Stopping* (`<base directory>/STOPPING.md`) with it. **Exit 3** = no request, nothing on stdout; carry on. **Exit 2** =
  the file's first line is not one of the three modes, or an argument the script does not
  take: nothing on stdout, the complaint on stderr, `.tdd/stop` left as it was. `--clear`
  removes `.tdd/stop` and exits 0 whether or not it was there — the last act of *Stopping*
  (`STOPPING.md`).
- `$S/refactor-budget.sh [--issue] <count>` — **bound the refactor loop**, so a step costs the same on
  every run. Given the number of transforms applied so far this step, it decides whether
  another one may run: **exit 0** = still under budget (launch the next transform leaf),
  **exit 3** = budget spent (stop the loop, go to verify-refactor), **exit 2** =
  `VERI_REFACTOR_BUDGET` is not a whole number ≥ 0 — a misconfigured run, with a diagnostic
  on stderr and **nothing on stdout**, fail-closed the way `classify-bail.sh` is on an
  unrecognised cause. A one-line status goes to stdout on 0 and 3 alike (`refactor 5/5 —
  budget spent`), so your narration can mirror it. `VERI_REFACTOR_BUDGET` (default 5) is a
  **third** tunable on a **third axis**: `VERI_STUCK_RETRIES` is liveness (the leaf never
  answered), `REVISE_BUDGET` is verdict (it answered and was rejected), this one is **cost
  per step** — how much tidying one step is worth, decided once for the run instead of by
  your judgement mid-loop.
- `$S/event.sh <event> [key=value …]` — append one JSON line to the run's event log
  `.tdd/events.jsonl`, relative to the worktree you are in. `supervise.sh` and `verify.sh`
  call it from inside themselves, so their events are complete by construction; **your**
  marks — `step-start`, `step-done`, `pin`, `revise`, `bail`, `done`, `resume` — are prose,
  so each is prescribed below at the point the matching narration is, and the run's context
  (`VERI_ISSUE`, `VERI_ACTOR=conductor`, `VERI_STEP`, `VERI_PHASE`, `VERI_ATTEMPT`) rides on
  the call in the environment. The log is run state: it is ignored, never committed, and
  goes with the worktree.
- `$S/metrics.sh <n>` — the event log's **reader**: prints on stdout one markdown
  `### 📊 Metrics` report of what solving issue `<n>` cost — attempts, verdicts, kills,
  retries and budgets spent, per phase and per step. Everything it knows comes from
  `.tdd/events.jsonl` in the worktree you are in, so it is called there and at the end, once
  the marks it reads have all been written. The conductor both commits its output beside the
  ledger and pastes it into the issue thread (the *Draft PR* step, and `<base directory>/BAIL.md`): a run that
  never calls it leaves the figures computable and uncomputed, which from the issue thread is
  indistinguishable from not having them.
- `$S/over-budget.sh <tier> <seconds> <usual>` — say whether one recorded test-command run
  was slow enough to be worth a word: **exit 0** = over budget, **exit 1** = not, **exit 2** =
  `VERI_UNIT_BUDGET` or `VERI_TIME_WARN_RATIO` cannot be read (the same misconfiguration
  step 5's `time-budget.sh` preflight refuses). On exit 0 it prints **exactly one line**,
  carrying a ⏱; on exit 1 it prints nothing at all. **Paste that ⏱ line verbatim into that
  phase's narration** in the issue thread, and do nothing else with it: **nothing branches on
  this check** — not the phase's verdict, not a retry, not a bail. A slow run is a remark, and
  a run that is not slow leaves you an empty capture and therefore nothing to paste.
- `$S/capture-spec.sh <n>` — the **blind spec**, on stdout: the issue's body, plus a `## Bug`
  section carrying its what-happened, expected, steps to reproduce and environment when the
  issue carries the `bug` label (and nothing extra when it does not). Redirect it into
  `.tdd/issue-<n>-spec.md` (step 3). Exit 2 on a missing issue number.
- `$S/refresh-spec.sh <n> <spec-file>` — re-capture the blind spec as `capture-spec.sh <n>`
  would and compare it to `<spec-file>`. **Exit 3** identical, file untouched. **Exit 0**
  rewritten to the live capture. **Exit 1** the live `## Acceptance criteria` checkbox count
  differs from the file's, file untouched, both counts on stderr. **Exit 2** bad arguments or
  no answer from `gh`, file untouched. The conductor calls it.
- `$S/resume-clean.sh` — a resumed run's first act: discard what a killed leaf left uncommitted
  outside `.tdd/`, printing each discarded change as its `git status --porcelain` line. Exit 0.
- `$S/ensure-run-state-ignored.sh [repo-root]` — make the **target repo** ignore veri's run
  scratch (`.tdd/*.log`, `.rc`, `.prompt`, `.reason`, the blind spec) while keeping the ledger
  tracked. Writes the rule to **both** the worktree's `.gitignore` (committed, so the first
  `git add -A` never sweeps leaf logs into history) and the shared
  `$(git rev-parse --git-common-dir)/info/exclude` (never committed, read by every worktree,
  so the caller's checkout — still on the default branch — stops reporting `.tdd/` as
  untracked). Idempotent in both files; the word on stdout reports the `.gitignore` only,
  `added` when it wrote the rule there, `already present` when it was there — the exclude
  file is ensured either way. Run once per issue right after entering the worktree (step 1).
- `$S/issue-worktree.sh <n> <slug> | --remove <n>` — the **linked worktree the issue branch lives in**.
  Creates (or hands back) `<repo-root>/.tdd/wt/<n>` on branch `tdd/<n>-<slug>`, cut from
  **`origin/<default>` as just fetched** — never from the caller's `HEAD`, and never from the
  **local** branch of that name: that one **lags the remote by design**, since a run executes the skill pinned from
  `origin/<default>` and nothing obliges anyone to pull the primary clone, so a branch cut
  from it starts **stale** and its PR then owes a rebase over everything that landed meanwhile.
  The fetch moves no local branch and touches no working tree. `<default>`'s **name** is read
  from `refs/remotes/origin/HEAD`; when that ref is absent (an origin does not guarantee one) it
  is resolved from the remote itself with `git ls-remote --symref origin HEAD`, and when the
  remote names none either it exits 2 naming `refs/remotes/origin/HEAD` — never a guessed
  `main`. A local `main`/`master` is the fallback only when there is **no origin remote** at all:
  then it supplies both the name and the **base** itself, as before. Prints the worktree's **absolute path on stdout** — the only
  thing on stdout; git's chatter goes to stderr, so the path is safe to capture.
  **Idempotent**: a second call for the same issue prints the same path and creates nothing,
  which is what makes a resume land in the worktree the first run made — a **local** issue
  branch is checked out as it is, with no fetch. Only a **local** branch or a **registered
  worktree** makes a run a resume. A branch **only origin** holds is refused (exit 2) unless
  the run is a resume, even when this clone has fetched it (a remote-tracking ref is not a
  resume): it creates no branch and no worktree, and names the takeover — `git branch
  tdd/<n>-<slug> origin/tdd/<n>-<slug>` — after which the next run is a resume. A **stale**
  remote-tracking ref, whose branch origin no longer holds, is not a claim: the run cuts fresh
  from `origin/<default>`, as above. **Exit 0** = the path. **Exit 2** = no answer
  could be obtained — either the branch is **already checked out in another worktree** (it names
  that path and touches nothing: **never steal a checkout**, another conductor owns that run),
  or the default branch cannot be named, or fetching it failed — never a silent fallback to the
  stale local ref. And exit 2 when the worktree it would have handed back **holds a live
  conductor**: the pid in `.tdd/conductor.pid` there still answers `kill -0` **and** that
  process's start time matches the one recorded on the lock's second line, so it
  names that pid instead of printing the path (#170) — a second conductor `cd`'ing into a live
  run's worktree reads that run's ledger as its own and `RESUME.md` throws the live leaf's
  uncommitted work away. A lock whose pid is **dead**, or answers but with a start time other than the
  recorded one (a **reused** pid), is a bailed or killed run, still a resume, still the path.
  `$S/issue-worktree.sh --remove <n>` removes the worktree once the PR has landed, and
  **refuses** (exit 2) one holding uncommitted changes.
- `$S/detect-test-command.sh [--tier fast|all] [--issue <body-file>] [repo-root]` — print the one command that
  runs the **target repo's** suite of that tier on stdout; **exit 3** — the repo-wide *nothing to do*
  code — when no marker it trusts matched, which is your cue to ask the user. First match
  wins: for `--tier all` only, the issue body's own `Test command:` line, unless it equals the
  fast tier's command (#1225); then the repo's CLAUDE.md line for the tier; then the repo's
  `.veri/test-command`; then every inference (see *Detecting the test command*).
  `--tier fast` never reads the issue's line.
- `$S/worktree-setup.sh <n>` — run from inside a run worktree: runs the `veri: setup: <cmd>` line of its CLAUDE.md (read like `veri: all tests:`) once in the worktree root; exit 2 with no argument. Called by preflight.
- `$S/solvable-issues.sh [--repo <owner/name>] [--not-running]` — the **selection layer**: prints the
  numbers of the issues veri may take right now — open, labelled `ready-for-agent`, every
  issue under their `## Blocked by` heading closed, and not already claimed by an open PR
  saying `Closes #<n>` — one per line, in three bands: the issues labelled `priority` first,
  then the `bug`s, then the rest, each band ascending by number. The band only reorders that
  set, it never enlarges it — the four conditions run first, so a `priority` issue that is
  blocked, claimed or not opted in is still not printed. `VERI_PRIORITY_LABEL` names the
  first band's label (default `priority`; set-but-empty is **exit 2**, like `VERI_LABEL`),
  and the second band's is GitHub's own `bug`. **Exit 0** when it printed at least one,
  **exit 3** with empty stdout when none is takeable (nothing to do, not an error).
  `VERI_GH_JSON=<dir>` reads `issues.json` / `prs.json` fixtures instead of shelling out to
  `gh`, which is what makes it testable with no network. `VERI_GH_DRIVER` picks the route
  every GitHub read and write takes, through `veri/github.py`:
  `rest` (the default when unset) runs only `gh api`, `graphql` runs only the `gh issue` /
  `gh pr` command with no fallback, and `auto` tries GraphQL then REST. Set but empty, or any
  other value, is **exit 2**, with a stderr line naming `VERI_GH_DRIVER` and the value, checked
  at call time. Operations with no GraphQL route — issue edit and create, `gh_rest_list`,
  `gh_json` with no gh args — use REST under every value, and `VERI_GH_JSON` takes precedence
  over it. A Claude Code cloud session, where GraphQL is refused, needs nothing set: the
  default is already `rest`. The conductor does not call this —
  it is rung 2's, driven by the loop branch of this skill.
- `$S/wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]` — **wait one bounded slice
  for a PR's checks**, then be called again: *4. Draft PR*'s CI wait. Reads the check runs and
  commit statuses of the PR's head; given `<head-sha>`, a PR still reporting another head reads
  as pending. `<slice-seconds>` (default and cap 540) bounds this call; `<total-seconds>` (cap
  600) bounds the whole wait, and when it is not given it is twice the mean of the last 5
  completed CI runs, capped at 600; 540 when fewer than 5 exist or `gh` cannot answer; the
  slice length when reading them fails otherwise. The deadline does not run only while every
  pending check is `queued` (none `in_progress`), or the PR reports another head: it is
  recorded in `.tdd/ci-deadline-<sha>`, which later calls inherit, by the first call where that
  is not so — a check in progress, no check yet, or only a commit status pending. The first
  queued sighting is recorded in `.tdd/ci-queued-<sha>`. A draft PR records no deadline. **Exit 0** every check completed
  `SUCCESS`, `NEUTRAL` or `SKIPPED`, not all `SKIPPED`. **Exit 1** a completed check concluded
  anything else, or a commit status is `failure`/`error`; the failed check names go on stdout,
  comma-separated. **Exit 2** no answer: bad arguments, the rollup unreadable 3 times running, a
  PR with no checks (or only skipped ones) that conflicts with its base branch (stderr says
  `conflicts with its base branch`), a check still pending past the recorded deadline, an
  unreadable deadline file, or checks that never started — still queued more than
  `VERI_CI_QUEUE_WAIT` seconds after the first call that saw them queued. **Exit 3** still
  pending, no check yet, every one `SKIPPED`, or a mismatched head, when the slice runs out.
  With `VERI_CI_ON_PR=0`, a PR whose head has no check runs and no commit statuses exits 0, since
  there is nothing to wait for; checks that do exist are still waited on and read as above. A
  `VERI_CI_ON_PR` other than `0`, `1` or empty is an **exit 2**.
  Tunables: `VERI_POLL` poll interval (default 10 s), `VERI_CI_QUEUE_WAIT` (default 3600 s),
  `VERI_CI_ON_PR` (unset means checks are expected).
- `$S/stop-reason.sh <issue>` — why a run ended with no ✅ Done or ⛔ Bailed comment: the operator's helper. Exit 2 on no argument, an issue with no run under `.tdd/wt`, a missing events log, or a run whose `conductor-<n>.log` has no result record. Nothing in the procedure calls it.
- `$S/handoff-state.sh` — print a read-only snapshot of the run state for a context reset. Its first line is `main <sha> <tag>`: main's commit and the highest version tag by `git tag --sort=-v:refname`. Exit **0**, **2** no answer. The conductor does not call this; it is an operator's.
- `$S/merge-lock.sh take --pid <pid> | release --pid <pid> | release --force | holder | gate [--keep] --pid <pid> -- <cmd>` — the merge lock, `.tdd/merge.lock` in the main working tree. `take`: exit **0** the lock taken, after waiting while another holder has it; **2** no `--pid`, or a missing, unreadable or malformed holder record. `release`: exit **0** removed; **1** the caller is not the recorded holder and `--force` was not given; **2** neither `--pid` nor `--force`; **3** no lock. `holder`: exit **0** a live holder, printed; **1** a stale lock (the recorded pid dead, or its start time differs), printed as such; **2** an unreadable record; **3** the lock is free. `gate`: runs `<cmd>` and exits with its code; a code other than 0 or 3 (CI red, a refusing gate) releases the lock `<pid>` holds first, 0 and 3 keep it; with `--keep` (before `--`) every code keeps it, and a code other than 0 or 3 prints a note that the lock is kept (a conflict or a refused push); exit **2** no `--pid`, or no `--` and command, with no lock created or removed. Any verb: exit **2** no verb, or one other than these four. The conductor does not call this; it is an operator's (vmerge's and vhandoff's).
- `$S/queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->` — a merge that refuses (exit 2, a usage line naming `<pr-url>`) an argument that is not a GitHub PR URL before it takes the lock, then takes the merge lock with `merge-lock.sh take --pid`, fetches origin, pins a lease to origin/`<branch>`'s sha before rebasing onto origin/main (refusing, exit 2 and nothing pushed, when the worktree lacks a commit origin/`<branch>` has), pushes under `--force-with-lease=<branch>:<sha>`, then waits for CI on the pushed head through `wait-ci.sh` under `merge-lock.sh gate --pid` (called again on exit 3) and merges that head. Only a PR GitHub reports `merged: true` is tagged (on the merge commit GitHub reports for it, `merge_commit_sha`, fetched first; never a re-read origin/main, which a concurrent merge may have moved past it), its remote and local branch deleted, its worktree removed and the main clone's `main` fast-forwarded to origin/main (`--ff-only`), and the lock is released after those. Exit **0** merged and cleaned up; **1** stopped by red CI, or the PR not reported merged, the lock released; a rebase conflict or refused push exits with git's code, the lock kept; **2** no answer: a usage line when called with no argument, origin/`<branch>` or the pushed head unresolvable, origin/`<branch>` not an ancestor of the worktree's HEAD, or a cleanup step (tag, branch delete, worktree remove, lock release) that failed after the merge, or a `main` fast-forward that cannot be done (non-zero exit, reported on stderr after the tag and the lock release), each named on stderr; a failing `take` stops with its code. An operator's script; the conductor does not call it.
- `$S/prose-owed.sh <repo-root>` — print each prose unit that owes a grade. Exit **0** nothing owed, **1** something printed, **2** no argument. On a `tdd/<n>-…` branch it waives a unit named in backticks by an unchecked `⟦skill-edit⟧` line of that branch's ledger (`.tdd/issue-<n>.md`), since that step will regrade it, and writes a `prose-owed-waived` event (`unit=`, `step=`) for each; every other finding still exits 1. `make unit` and `make test` run it; the procedure does not call it.
- `$S/skill-edit-step.sh [--change "<change>"] [--added "<step>"] <issue-body-file> <unit-file> [<pin-file>...]` — with `--change "<change>"`, an author runs even on a unit already graded PASS, and the prose it leaves must differ from before, else exit **1** (no change is not exit 3); without `--change` a PASS unit launches no author. With `--added`, a unit already graded PASS before any author ran is refused with exit **2** only when the issue states no row new to its list, naming the step and committing nothing; when the issue states a row whose ID the list does not yet hold, the new rows and the regraded `GRADED` are committed with no author and the step exits **3**; an `--added` step whose text names a prose change runs with `--change`, so its author runs. A step with nothing left to commit (not claimed) under `--added` still exits **2** (not 3); both refusals (exit 2) leave `REQUIREMENTS.md`, the unit and `GRADED` unmodified. Add the `## Requirements` rows the issue states for the unit to its `REQUIREMENTS.md` list; each named pin file may change in the author attempt and is committed with the unit, the list and `GRADED`. Exit **0** applied, an author attempt passed the grader and the list committed; **1** the grader rejected every attempt; **2** bad arguments, budget or heading, or no answer; **3** nothing was left to commit after the step, without `--added` and without `--change`: either the list and `GRADED` were committed with no author run, or there was no list and none was stated; under `--added`, exit **3** is the new-rows case above, and the not-claimed case exits **2**. The conductor's skill-edit step calls it.
- `$S/skill-edit-guard.sh <unit-file> <base-sha> [<pin-file>...]` — check that every path changed since `<base-sha>` is the unit file, its `REQUIREMENTS.md` or a named pin file. Exit **0** it is, **2** bad arguments. The skill-edit step runner calls it.
- `$S/watch-runs.sh [--target <N>] [--max-wait <seconds>]` — block until a conductor that was live when it started exits, then print `exited <issue> <state>` (`done`, `bailed`, `stopped` or `stale`) and exit 0: the operator's helper. Exit **2** bad arguments, **3** timeout. Nothing in the procedure calls it.
- `$S/park-issue.sh <issue-number> <cause> <unblock> [<pr-number|PR-URL>]` — park an issue in one call: add the label `parked` and post one comment headed `### ⏸ Parked`, with a `Cause:` line and an `Unblock:` line from the arguments. Exit **0** parked, **2** bad arguments, or no answer from `gh`. Nothing in the procedure calls it.
- `$S/parked-issues.sh` — read the parked set from GitHub alone: for each open issue labelled `parked`, print one tab-separated line — the issue's number, its title, and the cause and unblock text of its `### ⏸ Parked` comment. Exit **0** printed, **2** any argument, or no answer from `gh`. Nothing in the procedure calls it.
- `$S/preflight-refused.sh <issue-number> <check>` — record a preflight refusal: write one `preflight-refused` event carrying the check, `cause=preflight-refused` and its classification to the run's event log (`.tdd/wt/<n>/.tdd/events.jsonl` under the main checkout), and post one issue comment headed `### ⛔ Preflight refused — <check>`. Exit **0** recorded; **3** the run's standing end mark is already a `preflight-refused` event, so nothing is written or posted; **2** a missing or empty argument, or no answer (a comment GitHub refuses, after the event is written). Preflight calls it on every refusal.
- `$S/pr-ready.sh <pr-number> <sha>` — mark draft PR `<pr-number>` ready for review once `<sha>` is its head, by running `gh_pr_ready` (`veri/github.py`) behind a `/bin/sh` shim over `veri/pr_ready.py`, whatever shell calls it. Exit **0** marked ready, **2** bad arguments, or no answer from GitHub. The conductor calls it.
- `$S/restore-production.sh <test-path>...` — restore a worktree's production code to `HEAD`, keeping the named tests. A `/bin/sh` shim over `veri/restore_production.py`, run inside a worktree: it restores every tracked path except the named test paths to `HEAD` (`git checkout HEAD`) and removes every untracked, unignored file except the named test paths (`git clean`), so the tree holds no production change beyond `HEAD` while the named test paths are left exactly as they were. Exit **0** restored, **2** no argument (usage line on stderr) or git refused. The revise loop calls it before relaunching a red leaf.
- `$S/update-veri.sh [--consent yes|no]` — fast-forward veri's own clone to its upstream default branch, and only when the clone is on that branch with a clean tree. **Exit 0** = moved, **3** = already current, **1** = not allowed (the record or `VERI_SELF_UPDATE=0` says no, or the clone is off the default branch or dirty) or not a fast-forward, **2** = no answer. It honours the consent record at `~/.veri-tools/self-update` (`VERI_SELF_UPDATE_FILE` names another path), which `--consent yes|no` writes, and `VERI_SELF_UPDATE=0` turns it off. `run-conductor.sh` calls it before pinning a fresh run, never on a resume.
- `$S/pinned-scripts.sh <n>` — print the directory holding run `<n>`'s pinned scripts, under the run's worktree `.tdd/`. **Exit 0** = the directory, which exists. **Exit 2** = that directory is absent: the diagnostic names the pinned commit read from `.tdd/issue-<n>-skill-commit` and the recovery line `git archive <pin> skills/tdd/scripts`, or says no pin is recorded when there is no such file.
