# Plan for #1553 — wait-ci.sh exits 2 on one transient GitHub API failure, so a green PR bails ci-timeout

- [x] A failed read of a PR's checks (the PR, its check-runs or its status, answered non-zero by gh) counts as one pending poll: wait-ci.sh sleeps its poll interval and reads again within the same slice and deadline, so a faked gh that fails twice and then answers green gets exit 0 ⟦criterion 1⟧
- [x] wait-ci.sh exits 2 ("could not read the checks of …") only after three consecutive polls whose read failed: a faked gh that always fails gets exit 2 after exactly three reads ⟦criterion 1⟧
- [x] A successful poll resets the consecutive-failure count, so failures that don't come three in a row never end the wait: a faked gh that alternates failure and pending, then answers green, gets exit 0 ⟦criterion 2⟧
