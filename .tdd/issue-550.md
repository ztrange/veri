# Plan for #550 — wait-ci.sh reads the previous head's green right after a push

- [x] `wait-ci.sh` takes the head sha it waits for as an argument, and while the PR's reported `headRefOid` is a different commit it exits 3 (pending) at the end of its slice even when that other commit's checks all completed SUCCESS ⟦criterion 1⟧
- [x] `wait-ci.sh`'s total bound is recorded against the head sha it was given, not the PR's reported head: a later call for the same sha that still finds the PR reporting a different head past that recorded deadline exits 2 ⟦criterion 1⟧
- [x] SKILL.md's Draft PR step passes the sha it just pushed (`git rev-parse HEAD`) to every `wait-ci.sh` call ⟦criterion 2⟧ ⟂ refactor pending
- [ ] a legacy StatusContext row carrying no `state` key makes `wait-ci.sh` exit 2 (no answer could be obtained) on its first read, instead of waiting out the bound ⟦criterion 3⟧
- [ ] SKILL.md's Draft PR step bails on the `metrics:` push's CI wait with a command in its block — `ci-red` on exit 1, `ci-timeout` on exit 2 — not only in prose after the `done` mark
