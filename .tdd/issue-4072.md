# Plan for #4072 — PRD 013.13: judge decisions are recorded where the owner audits them

- [x] `decision-log.sh record <question> <decision> <rule> <by>` appends one JSON line with keys question, decision, rule, by and at (ISO-8601 with offset) to `.tdd/decisions.jsonl` in the main working tree, exit 0 ⟦criterion 1⟧
- [x] `decision-log.sh record` with an argument missing or empty exits 2 and writes nothing ⟦criterion 2⟧
- [x] a token-shaped credential or a `VERI_REDACT_VARS` value in a recorded field is written as `[redacted]`
- [x] `status.sh --report` lists, under Waiting, each `.tdd/decisions.jsonl` line whose `at` is after the time in `.tdd/status-last`, with its question, decision and rule, and none at or before it ⟦criterion 3⟧
- [x] `status.sh --report` exits 2 naming the line when `.tdd/decisions.jsonl` holds a line that is not a decision record
- [x] `skills/vjudge/SKILL.md` *Recording* says a decision about one issue is a comment on it naming the rule applied and the option not taken, and one about no issue is recorded with `$S/decision-log.sh record` ⟦criterion 4⟧
- [x] `decision-log.sh record` takes `<by>` only as `coord`, `dev` or `owner`; anything else exits 2 and writes nothing
