# Event journal

`event.sh <event> [key=value …]` (or `event.mark` from a Python module) appends one JSON line to `.tdd/events.jsonl`. Every line carries `ts` (epoch seconds), `awake` (awake-clock reading), `issue`, `actor`, `phase`, `step`, `event` (the name), `attempt` and `skill_commit` (the run context, empty when unset), then the keys below, in the order the emitter gives them. Every value is a string.

Keys and events are append-only: a key or event is never removed or renamed, only added. No event carries a schema version key.

| Event | Keys | Meaning |
|---|---|---|
| `bail` | `cause`, `classification`, `suites` | The run stopped: `cause` is why (`needs-user`, `killed-stuck`, `no-verdict`, `step-too-big`, `revise-exhausted`, `ci-red`, `ci-timeout`, `ci-conflict`, `suite-red`, `pr-ready-failed`, `step-add-refused`, …); `classification` is `process` (the methodology spoke) or `system` (the plumbing broke), absent when the conductor stopped unmarked; `suites`, carried only by `cause=suite-red`, names every suite still red after the repair step. |
| `comment` | `kind`, `url` | comment.sh posted a routine comment: its `kind` (`step-done`, `red`, `verify-red`, `green`, `verify-green`, `refactor`, `verify-refactor`, `verify-revised`, `plan`, `verify-plan`, `resuming` or `done`) and the posted comment's url. |
| `conductor-start` | `pid`, `started` | A conductor began a run: its process id and start time. |
| `conductor-restart` | `growth`, `knob` | restart-conductor.sh relaunched a run's conductor: the plan-growth count that triggered it and the knob whose change it picks up. |
| `criterion-unticked` | `issue`, `matcher` | An issue acceptance criterion was unticked: the issue number and the text that matched it. |
| `diff-leaf-deviation` | `leaf`, `base`, `head`, `commits` | A diff-checked leaf strayed from its one commit: the leaf, the step base sha, `HEAD` and the commit count. |
| `done` | `pr`, `wall_seconds`, `awake_seconds`, `lane` | The run finished: the PR url, wall-clock seconds since the opening event (or last `resume`), awake-clock seconds over the same span (absent without both clocks), and the lane label. |
| `exit` | `status`, `cause`, `secs` | A supervised leaf exited: its exit status, why when it was killed or refused (`cause`, absent otherwise), and the seconds it ran. |
| `launch` | `name`, `cmd`, `model` | The supervisor launched a leaf: its name, the command line after the binary, the model. |
| `launch-refused` | `name`, `reason` | The supervisor refused to launch a leaf, and why. |
| `merged` | `issue`, `pr`, `tag`, `message` | The PR was merged: `issue` is the issue number; `pr` the PR url; `tag` the version tag cut (empty when none); `message` the tag's capability message (empty when no tag). |
| `mutation-record-restored` | `name`, `file` | A mutation record a leaf disturbed was restored: the record's name and file. |
| `pin` | — | The skill snapshot was pinned to a commit. |
| `pin-retired` | `reason` | pin-recheck.sh retired a pin that a later issue's design supersedes: the reason the declaration gave. |
| `plan` | `steps` | The plan was written to the ledger: the number of steps. |
| `prediction-diverged` | — | A step's predicted outcome differed from the observed one. |
| `preflight-refused` | `check`, `cause`, `classification` | A preflight check refused the run's start: `check` names the failing check, `cause` is always `preflight-refused`, and `classification` is its bail classification (`system`). |
| `production-file-restored` | `name`, `file` | A production file a leaf changed was put back as it was before the leaf ran: `name` is the leaf, `file` the restored path. |
| `push-failed` | `error`, `attempts` | Pushing the branch failed after `attempts` tries: the git error. |
| `push-rejected` | `remote_sha`, `error` | The remote refused the push: the remote tip sha and the git error. |
| `rebase-refresh-retry` | — | A merge rebase was retried after a ref refresh. |
| `refactor` | `transforms`, `budget`, `stopped`, `pass` | A refactor leaf finished: transforms applied, the `VERI_REFACTOR_BUDGET`, why it stopped, and whether the pass landed. |
| `relaunch` | `cause` | A verifier was launched again: `tree-change` (the tree moved under it) or `no-verdict` (it finished without a `VERDICT:` line). |
| `report-missing` | `name`, `missing` | A suite's output left no report line: the suite's name and the missing line (`SUITE`). |
| `reroute` | `case`, `kind` | A step was rerouted: the case id (absent for `later`) and the kind (`red`, `later`, `missing`). |
| `resume` | — | A run resumed. |
| `resume-rebase` | `from`, `rebased` | A resume rebased: the pre-rebase sha and the new tip. |
| `retry` | `cause` | The supervisor relaunched a stuck leaf: why. |
| `revise` | `budget` | A verdict was REJECT and the step was redone: the `REVISE_BUDGET`. |
| `skill-repin` | `commit` | The skill pin was moved (`VERI_NEW_SKILL=1`): the new commit. |
| `step-added` | `anchor`, `added` | Steps were added to the ledger after `anchor`: how many. |
| `step-done` | — | A step finished. |
| `step-escalated` | `anchor`, `at` | A step was escalated to a stronger model: the step, and where (`over-budget`; absent for a revise escalation). |
| `step-over-budget` | `spent`, `budget` | A step crossed its budget: what it spent and the budget. |
| `step-split` | `anchor`, `added`, `at` | A step was split into smaller steps: the step, how many were added, and where (`over-budget`; absent otherwise). |
| `step-start` | — | A step began. |
| `stop` | `mode`, `at` | The run stopped on request: the mode and the point it stopped at. |
| `structural-pass` | `transforms`, `budget`, `stopped` | The issue-wide structural pass finished: transforms applied, the `VERI_ISSUE_REFACTOR_BUDGET`, and why it stopped (`candidates-done`, `budget-spent`, `nothing-structural`; required). |
| `suite-repair-retired` | — | A suite-repair step was retired. |
| `test-run` | `tier`, `suites`, `seconds`, `status` | A timed test run ended: its tier (`fast`, `affected`, `full`), the suites it ran, seconds taken, exit status. |
| `usage` | `duration_ms`, `duration_api_ms`, `num_turns`, `total_cost_usd`, `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `model`, `model_usage` | What a leaf cost, from its closing result record: durations, turns, dollars, the four token counts, the model names (comma-joined) and a JSON object of per-model usage (`model_usage` absent when the record has none). |
| `verdict` | `verdict`, `reason`, `cause` | A verifier ruled: `PASS`, `REJECT` or `malformed`; the first line of its reason; `cause=no-verdict` only when it never wrote a `VERDICT:` line. |
| `verify-refactor-skipped` | `reason` | The refactor verifier was skipped (`nothing-landed`, `switched-off`). |
