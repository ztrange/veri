# Plan for #1896 — wait-ci.sh starts its deadline while the PR still reports an older head, so a late push lands with the budget already spent

- [x] While the PR's head differs from the given head-sha, wait-ci.sh records no .tdd/ci-deadline-<head-sha> file and does not exit 2 for that sha: the call ends its slice with exit 3 ⟦criterion 1⟧
- [x] The first wait-ci.sh call that sees the PR's head equal to the given head-sha records .tdd/ci-deadline-<head-sha>, counted from that call's moment, and a later call inherits that recorded deadline ⟦criterion 1⟧
- [x] With no head-sha given, wait-ci.sh still records .tdd/ci-deadline-<head> on the first pending call for the PR's current head ⟦criterion 2⟧
