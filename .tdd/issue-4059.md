# Plan for #4059 — PRD 020.3: a merge that errored is never re-merged over a landed PR

- [ ] skills/vmerge/SKILL.md step 5 re-reads an errored merge's state over the settle window, treats MERGED as success, and never rebases or pushes a PR whose head is an ancestor of origin/main; rows M23–M24, graded PASS ⟦criterion 1⟧
