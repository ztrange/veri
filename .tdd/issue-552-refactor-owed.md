### wait-ci.sh exits 1 when the given sha's own check runs hold a completed failure, even while the PR rollup reads all green ⟦criterion 1⟧
- wait-ci.sh's sha_state repeats the passing-conclusion set ("success","neutral","skipped") that rollup_state already holds as ("SUCCESS","NEUTRAL","SKIPPED"); sharing one set across the two python snippets would remove it, but only once step 3 (sha green) uses the set too
- wait-ci.sh's sha_state works out the owner/repo from $pr again on every poll; it could be set once, next to pr=
