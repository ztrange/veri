# Plan for #51 — Stage-0 commentary: fix mislabeled preflight timing, document the caller's side of the ignore-rule contract

- [x] commentary.py's stage-0 intro no longer claims ensure-run-state-ignored.sh runs "at preflight" — it names step 1.4, right after branching, matching SKILL.md's actual phase order
- [ ] the ensure-run-state-ignored commentary states what the conductor does with each stdout outcome (added -> commit as the branch's first commit with the exact "chore: ignore veri run state (#<n>)" message; already present -> nothing to do)
