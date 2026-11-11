# Plan for #3593 — dispatch.sh reports a bail as silent-exit when the skill-drift note follows the Bailed comment

- [x] `dispatch.exit_line()` returns `bail <issue>` when the newest issue comment is the `Skill drift for the bail above:` note and the comment before it starts `### ⛔ Bailed` (a small unit case, comments faked at the `last_comment`/GitHub boundary, no production change beyond `dispatch.py`) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `dispatch.exit_line()` returns `done <issue> <pr>` when a `### ✅ Done — <pr-url>` comment is followed by a newer non-closing comment (a small unit case, comments faked at the GitHub boundary) ⟦criterion 2⟧
