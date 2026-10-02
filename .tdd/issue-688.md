# Plan for #688 — wait-ci.sh exits at once, naming the conflict, for a PR that conflicts with its base, and the conductor rebases instead of timing out

- [x] wait-ci.sh, for a PR GitHub reports as mergeable CONFLICTING with no check on its head, exits 2 at its first poll — without waiting out its slice or a recorded deadline — with a stderr line naming the PR and saying it conflicts with its base branch, so no workflow will start until it is rebased ⟦criterion 1⟧
- [x] wait-ci.sh, for a CONFLICTING PR with no check whose reported head differs from the head-sha it was given, also exits 2 at its first poll naming the conflict, rather than holding it as pending until its slice ends ⟦added⟧ ⟦criterion 1⟧
- [x] wait-ci.sh, for a PR reported mergeable UNKNOWN with no check yet, keeps polling and ends its slice in exit 3, as today ⟦criterion 2⟧
- [x] wait-ci.sh, for a CONFLICTING PR whose head already has checks, decides by those checks exactly as today — 0 green, 1 red, 3 pending within the slice, 2 pending past the recorded deadline ⟦criterion 3⟧
- [x] a mergeable PR is handled exactly as today in every case wait-ci.test.sh holds ⟦full-suite⟧ ⟦criterion 4⟧
- [x] SKILL.md's CI step says that on wait-ci.sh exit 2 whose stderr names a conflict the conductor rebases onto origin/<default> through the existing rebase path (rebase verifier, full suite, push under a pinned lease) and waits for CI again, once, and that a second conflict bails with cause ci-conflict ⟦criterion 5⟧
- [x] classify-bail.sh classifies ci-conflict as a system failure, and SKILL.md's Bailing list names ci-conflict among the cause tokens a human reads ⟦criterion 6⟧
