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
- `VERI_STEP=<step> $S/wrong-test-route.sh <green-report> <red-test-id>` — routes a green report's `WRONG_TEST:`, or a report carrying `MISSING_TEST:` (a verify-green REJECT reason, a mutation-parity stderr saved to a file, a revise-green report answering `IMPOSSIBLE`): **exit 0** prints `missing <behaviour>` (a behaviour no test pins; the report file is the `red-missing` brief), `red <case>` (an existing case other than the step's own that the criterion contradicts), `repair <case> <superseded>…` (a case the step's own Red wrote, per its red record or as `<red-test-id>`, with the older cases listed on `SUPERSEDED:` lines) or `supersede <case> <case>…` (two or more older cases named on `SUPERSEDED:` lines, which one `red-supersede` Red updates together), **exit 3** prints `revise`, **exit 2** bad arguments. Only a step's first reroute is free: once `.tdd/events.jsonl` holds a `reroute` event with `VERI_STEP`, a later `WRONG_TEST:`, `SUPERSEDED:` or `MISSING_TEST:` in that step answers `revise` and spends one `REVISE_BUDGET` attempt.
- `$S/pin-fast-tier.sh '<fast-cmd>'` — run the fast tier over the tree a pin would commit,
  from the worktree. Takes the fast command as its one argument. On failure it writes the
  command's output to `.tdd/verify-pin.reason`. **Exit 0 = the command passed, 1 = it failed
  (output in the reason file), 2 = no command given.**
- `$S/tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase>] .tdd/issue-<n>.md "<substring>"` — check a step off
  in the **committed ledger**, in place (staged + committed together with that step's green
  code). **Exit 3** if no unchecked step matched the substring — the file is left untouched,
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
  again (see the exhausted-contract paragraph under *A `⟦phases: …⟧` step*). `$S/ledger-steps.sh next-phase < .tdd/issue-<n>.md` prints the first phased step's next
  unmarked phase, **exit 3** when none is left. The cycle loop runs a phased step through
  both — see *A `⟦phases: …⟧` step* under *3. The cycle loop*.
- `$S/reorder-ledger-steps.sh .tdd/issue-<n>.md "<step>" before|after "<anchor>"` — the one sanctioned way to change the order of **unchecked** steps, committed on its own as a `plan:` commit; running it is an operator's decision, never the conductor's own.
- `$S/next-pending-refactor.sh < .tdd/issue-<n>.md` — print the **first ticked step whose
  refactor is unverified**: the description of the first `- [x]` step carrying the
  ` ⟂ refactor pending` mark, with the mark stripped, so what comes back is the same text
  `next-unchecked.sh` hands the loop and the tick wrappers match on. **Exit 0** when it
  printed one; **exit 3** with empty stdout when no step carries the mark — every green step
  has been tidied, so a resume has no refactor loop to re-enter.
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md "<substring>"` — the counterpart of
  `tick-ledger.sh --refactor-pending`: **strip the ` ⟂ refactor pending` mark** from the first
  ticked step matching the substring, in place, once that step's refactor has been verified.
  Nothing on stdout. **Exit 0** when it cleared the mark; **exit 3** when no ticked step both
  matched and carried it — the file is left byte-identical, because nothing is written unless
  the transform found its line.
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
- `$S/tests-frozen.sh record <record-file>|--step "<step>" <test-file>… | check <record-file>|--step "<step>" | path "<step>"` — **freeze a step's tests between verify-red and verify-green.** `record --step` digests the given test files and also every test file (`transform-touches-tests.sh`'s rule) differing from `HEAD`: modified, deleted (recorded as deleted, so its deletion is not an unrecorded change) or untracked. `check --step` exits 1 naming a recorded file whose digest changed, and also naming a test file outside the record that now differs from `HEAD`; a recorded-deleted file that exists again, and a tracked test file deleted after the record, are named too; a changed non-test file is never named. Exceptions: a `⟦replaces-case⟧` step may change the suite it names (any other unrecorded test file is still flagged), a `⟦guard-subject: <path>⟧` step may change the file it names (a guard suite or sourced test helper; any other unrecorded test file, the case Red wrote included, is still flagged), and a `⟦suite-repair⟧` or `⟦ci-repair⟧` step is never frozen, `record` writing nothing and `check` exiting 0. Exit 2 = no answer (bad arguments, record missing or malformed).
- `$S/classify-bail.sh <cause>` — deterministically classify a bail cause
  (`killed-stuck`/`no-verdict` → `system`, `revise-exhausted` → `process`; unknown → exit
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
  conductor**: `.tdd/conductor.pid` there names a process that still answers `kill -0`, so it
  names that pid instead of printing the path (#170) — a second conductor `cd`'ing into a live
  run's worktree reads that run's ledger as its own and `RESUME.md` throws the live leaf's
  uncommitted work away. A **dead** pid is a bailed or killed run, still a resume, still the path.
  `$S/issue-worktree.sh --remove <n>` removes the worktree once the PR has landed, and
  **refuses** (exit 2) one holding uncommitted changes.
- `$S/detect-test-command.sh [--tier fast|all] [--issue <body-file>] [repo-root]` — print the one command that
  runs the **target repo's** full suite on stdout; **exit 3** — the repo-wide *nothing to do*
  code — when no marker it trusts matched, which is your cue to ask the user. First match
  wins: the issue body's own `Test command:` line (for `--tier all`, unless it equals the fast
  tier's command — #1225), then the repo's `.veri/test-command`,
  then every inference (see *Detecting the test command*).
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
  every GitHub read and write takes, through `veri/github.py` and `lib/github.sh` alike:
  `rest` (the default when unset) runs only `gh api`, `graphql` runs only the `gh issue` /
  `gh pr` command with no fallback, and `auto` tries GraphQL then REST. Set but empty, or any
  other value, is **exit 2**, with a stderr line naming `VERI_GH_DRIVER` and the value, checked
  at call time. Operations with no GraphQL route — issue edit and create, `gh_rest_list`,
  `gh_json` with no gh args — use REST under every value, and `VERI_GH_JSON` takes precedence
  over it. A Claude Code cloud session, where GraphQL is refused, needs nothing set: the
  default is already `rest`. The conductor does not call this —
  it is rung 2's, driven by the loop branch of this skill.
- `$S/stop-reason.sh <issue>` — why a run ended with no ✅ Done or ⛔ Bailed comment: the operator's helper. Exit 2 on no argument, an issue with no run under `.tdd/wt`, a missing events log, or a run whose `conductor-<n>.log` has no result record. Nothing in the procedure calls it.
- `$S/handoff-state.sh` — print a read-only snapshot of the run state for a context reset. Its first line is `main <sha> <tag>`: main's commit and the highest version tag by `git tag --sort=-v:refname`. Exit **0**, **2** no answer. The conductor does not call this; it is an operator's.
- `$S/prose-owed.sh <repo-root>` — print each prose unit that owes a grade. Exit **0** nothing owed, **1** something printed, **2** no argument. `make unit` and `make test` run it; the procedure does not call it.
- `$S/skill-edit-guard.sh <unit-file> <base-sha>` — check that every path changed since `<base-sha>` is the unit file or its `REQUIREMENTS.md`. Exit **0** it is, **2** bad arguments. The skill-edit step runner calls it.
- `$S/skill-edit-step.sh <issue-body-file> <unit-file>` — add the `## Requirements` rows the issue states for the unit to its `REQUIREMENTS.md` list. Exit **0** applied, an author attempt passed the grader and the list committed; **1** the grader rejected every attempt; **2** bad arguments, budget or heading, or no answer; **3** nothing was left to commit after the step: either the list and `GRADED` were committed with no author run, or there was no list and none was stated. The conductor's skill-edit step calls it.
- `$S/watch-runs.sh [--target <N>] [--max-wait <seconds>]` — block until a conductor that was live when it started exits, then print `exited <issue> <state>` (`done`, `bailed`, `stopped` or `stale`) and exit 0: the operator's helper. Exit **2** bad arguments, **3** timeout. Nothing in the procedure calls it.
