# Plan for #251 — A run executes the primary clone's skill, which nothing keeps current, so merged fixes are not live — pin the fetched origin tip instead

- [x] A run launched by `run-conductor.sh` while the skill's clone is behind `origin/<default>` executes the skill at `origin/<default>`'s tip: a script changed only on the remote is the version in the base directory the conductor is handed
- [x] Launching a run leaves the skill clone's `HEAD`, branch and working tree unchanged — no pull, no checkout
- [x] A failed fetch of `origin` exits 2 before any conductor is launched, with a stderr diagnostic naming the fetch ⟂ refactor pending
- [ ] The pinned skill commit reaches the run: every event a launched run writes carries it as `skill_commit`, and the conductor's prompt names it for the plan comment, equal to `origin/<default>`'s commit at launch
- [ ] A resumed run keeps its recorded pin even when `origin/<default>` has moved since the first launch
- [ ] A resume on which the operator explicitly asks for the new skill (`VERI_NEW_SKILL=1`) re-pins to `origin/<default>` as just fetched, not to the clone's `HEAD`
- [ ] `SKILL.md` no longer says pulling the primary clone changes the scripts under a live run
