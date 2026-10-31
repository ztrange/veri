# Plan for #2739 — status.sh lists a live conductor that has written no event yet

- [x] A worktree with no ledger, no `events.jsonl` and no live conductor (no `conductor.pid`, or one whose pid is dead) stays unlisted by `status.sh`, text and `--json`; no production change is expected, so this pins what holds today ⟦criterion 1⟧
- [ ] `status.sh` text output lists a run with a live conductor, no ledger and no `events.jsonl` under its worktree's issue number as `running`, with `step` and `title` empty ⟦criterion 1⟧
- [ ] `status.sh --json` lists a run with a live conductor, no ledger and no `events.jsonl` with `state` `running`, `issue` its worktree's number, and `step` and `title` empty strings ⟦criterion 1⟧
- [ ] `status.sh` (text and `--json`) reports `running` for a run with a live conductor and a ledger but no `events.jsonl`, keeping its ledger's title and step, and the scope totals still count that run once
