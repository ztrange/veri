# Event journal

`event.sh <event> [key=value …]` appends one JSON line to `.tdd/events.jsonl`. Every line carries the event name and the run context; the keys below are the ones each event adds.

| Event | Keys | Meaning |
|---|---|---|
| `bail` | `cause`, `classification`, `failed`, `suites` | The run stopped: why, whether the methodology or the plumbing failed, the CI output, the suites still red. |
| `conductor-start` | — | A conductor began a run. |
| `criterion-unticked` | — | An issue acceptance criterion was unticked. |
| `done` | `pr` | The run finished; the PR url. |
| `merged` | `issue` | The PR was merged. |
| `pin` | — | The skill snapshot was pinned to a commit. |
| `plan` | — | The plan was written to the ledger. |
| `prediction-diverged` | — | A step's predicted outcome differed from the observed one. |
| `rebase-refresh-retry` | — | A merge rebase was retried after a ref refresh. |
| `refactor` | `transforms`, `budget`, `stopped`, `pass` | A refactor leaf finished: transforms applied, budget, why it stopped. |
| `reroute` | `case`, `kind` | A step was rerouted (`red`, `later`, missing test). |
| `resume` | — | A run resumed. |
| `resume-rebase` | `from`, `rebased` | A resume rebased: the pre-rebase sha and the new tip. |
| `revise` | `budget` | A verdict was REJECT and the step was redone. |
| `skill-repin` | — | The skill pin was moved (`VERI_NEW_SKILL=1`). |
| `step-added` | `anchor`, `added` | Steps were added to the ledger. |
| `step-done` | — | A step finished. |
| `step-escalated` | `anchor`, `at` | A step was escalated to a stronger model. |
| `step-over-budget` | `spent`, `budget` | A step spent more than its budget. |
| `step-split` | `anchor`, `added`, `at` | A step was split into smaller steps. |
| `step-start` | — | A step began. |
| `stop` | `mode`, `at` | The run stopped on request. |
| `structural-pass` | `transforms`, `budget`, `stopped` | The issue-wide structural pass finished. |
| `suite-repair-retired` | — | A suite-repair step was retired. |
| `verify-refactor-skipped` | `reason` | The refactor verifier was skipped (`nothing-landed`, `switched-off`). |
