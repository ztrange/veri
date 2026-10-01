### claude-md-guards-green.test.sh starts none of the four guard suites as a child process, and passes on a roster holding all four even when a guard itself would fail ⟦criterion 3⟧
- delete the dead passing-guard stubs (and the HERE they swap in) from probe_names_each_guard_missing_from_a_planted_roster and probe_fails_when_a_planted_roster_names_no_suite — the probe no longer reads HERE
- rename probe_every_guard_is_rostered_and_green (and the first case's `name` text) — it no longer checks that any guard is green
