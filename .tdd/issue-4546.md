# Plan for #4546 — A repair or missing reroute after green launches its leaf with green's production edits still in the tree

- [x] reroute.sh on a `repair <case> <superseded>…` answer restores green's uncommitted production edit to HEAD through restore-production.sh, keeping the step's test path and every routed case's file, before the develop-red-repair leaf launches ⟦criterion 1⟧
- [x] reroute.sh on a `missing <behaviour>` answer restores green's uncommitted production edit to HEAD through restore-production.sh, keeping the step's test path, before the develop-red-missing leaf launches ⟦criterion 2⟧
- [x] SCRIPTS.md, SKILL.md and REQUIREMENTS.md name the restore on repair and missing, regraded
