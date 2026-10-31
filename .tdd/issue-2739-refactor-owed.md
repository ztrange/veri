### `status.sh` text output lists a run with a live conductor, no ledger and no `events.jsonl` under its worktree's issue number as `running`, with `step` and `title` empty ⟦criterion 1⟧
- out-of-scope | `render` and `run_activity` both test for `events.jsonl`. Merging the two checks needs a signature change that this step's tests don't ask for.
### `status.sh` (text and `--json`) reports `running` for a run with a live conductor and a ledger but no `events.jsonl`, keeping its ledger's title and step, and the scope totals still count that run once
- test-only | extract the repeated live-conductor run setup (mkdir, `live_conductor`, `main_working_tree` and `branch_of` monkeypatches) and the repeated `listed` tuple comprehension in the new `test_2739_*` cases into a helper
not-done | transform-rejected | `render` and `run_activity` both test for `events.jsonl`. Merging the two checks needs a signature change that this step's tests don't ask for.
