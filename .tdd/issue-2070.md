# Plan for #2070 — A needs-user comment follows a ✅ Done comment on a finished run

- [ ] A conductor that exits 0 with a result record while its run's events.jsonl reads open (no standing done, bail or stop mark, e.g. a done followed by a resume, or a log that cannot be read) but whose issue thread already carries a `### ✅ Done` comment gets no `bail cause=needs-user` event appended and no needs-user comment posted: the launcher treats the posted Done as closing the run and stays silent ⟦criterion 1⟧
