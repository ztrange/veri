# Plan for #3997 — PRD 019.2: a ci-conflict after the run's one rebase is judged once before the run bails

- [x] `build-adjudicate-prompt.sh <n> ci-conflict 2 <stderr-file> <command…>` exits 0 and its prompt carries `Routes: rebase`, `ADJUDICATE.md` listing `ci-conflict` with its route `rebase` ⟦criterion 1⟧
- [x] `adjudicate.sh record <n> ci-timeout <leaf-output>` on `ADJUDICATION: route rebase — <reason>` writes `outcome=unparsed` and exits 2: a route token is accepted only when `ADJUDICATE.md` lists it for that cause ⟦criterion 2⟧
- [x] `adjudicate.sh record <n> ci-conflict <leaf-output>` on `ADJUDICATION: route rebase — <reason>` prints `route rebase`, writes one `adjudicated cause=ci-conflict outcome=route reason=<reason>` event and exits 1 ⟦criterion 2⟧
- [x] `adjudicate.sh left <n>` exits 0 when every `adjudicated cause=ci-conflict` event precedes the issue's last `conductor-start`, however many there are ⟦criterion 5⟧
- [ ] `JOURNAL.md`'s `adjudicated` row names `ci-conflict` among its causes and `route` among its outcomes ⟦criterion 7⟧
- [ ] `ADJUDICATE.md`, `DRAFT-PR.md` and `BAIL.md` carry the issue's `## Requirements` rows, graded PASS ⟦criterion 6⟧
