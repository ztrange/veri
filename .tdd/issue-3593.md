# Plan for #3593 — dispatch.sh reports a bail as silent-exit when the skill-drift note follows the Bailed comment

- [x] `dispatch.exit_line()` returns `bail <issue>` when the newest issue comment is the `Skill drift for the bail above:` note and the comment before it starts `### ⛔ Bailed` (a small unit case, comments faked at the `last_comment`/GitHub boundary, no production change beyond `dispatch.py`) ⟦criterion 1⟧
- [ ] Pin: dispatch.exit_line() keeps a newest `### ✅ Done — <pr-url>` over an older `### ⛔ Bailed` behind it; the case fails on a mutant of step 1's backward scan without that guard; every guard the step adds is pinned by a case only it decides ⟦criterion 2⟧
