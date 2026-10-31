### `status.sh` text output lists a run with a live conductor, no ledger and no `events.jsonl` under its worktree's issue number as `running`, with `step` and `title` empty ⟦criterion 1⟧
- out-of-scope | `render` and `run_activity` both test for `events.jsonl`. Merging the two checks needs a signature change that this step's tests don't ask for.
