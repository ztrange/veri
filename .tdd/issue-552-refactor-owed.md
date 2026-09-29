### wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧
- wait-ci.sh's sha_state repeats the passing-conclusion set ("success","neutral","skipped") that rollup_state already holds as ("SUCCESS","NEUTRAL","SKIPPED"); sharing one set across the two python snippets would remove it, but only once step 3 (sha green) uses the set too
- wait-ci.sh's sha_state works out the owner/repo from $pr again on every poll; it could be set once, next to pr=
### wait-ci.sh reads every page of the given sha's check runs, so a failed run beyond the first page of results still exits 1 ⟦added⟧ ⟦criterion 1⟧
- skills/tdd/scripts/wait-ci.sh sha_state: `pages if isinstance(pages, list) else [pages]` is now dead code, because `gh api --paginate --slurp` always returns a list and the stub now always serves that list. It is dead-code removal rather than duplication removal, so it is out of this phase's scope.
- skills/tdd/scripts/tests/wait-ci.test.sh gh stub: wait-ci.sh never takes the stub's non-`--paginate` and non-`--slurp` output branches. Those branches are dead code in this suite.
