# Plan for #3154 — The coordinator and dev session are unmetered and read 55.8M cache tokens in a day: double supervision, no context reset

- [x] With `VERI_SESSION_TRANSCRIPTS` naming a directory of fixture Claude Code session transcripts, `metrics.sh <n>` reports the coordinator session's spend — the transcript whose first user prompt invokes `/vcoord` — as its turns, its cache tokens read and its $ priced from the price table ⟦criterion 1⟧
- [ ] Beside the coordinator's, `metrics.sh <n>` reports the dev session's spend the same way — the transcript whose first user prompt invokes `/vdev` — as its turns, cache tokens read and $ ⟦criterion 1⟧
- [ ] A session's assistant turn timestamped before the issue's first event in the event log is left out of that session's reported turns, cache tokens and $ ⟦criterion 1⟧
- [ ] A session's assistant turn timestamped after the issue's `done` event in the event log is left out of that session's reported turns, cache tokens and $ ⟦criterion 1⟧
- [ ] An assistant message written to a session transcript as several records sharing one message id counts as one turn, its usage counted once, in the reported spend ⟦criterion 1⟧
