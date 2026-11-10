# Plan for #3250 — status.sh --report's Waiting lists merged PRs as ready to merge

- [x] A fixture repo whose local `main` holds a commit with subject ending `(#N)`, and a journal for issue N whose last `done` event carries a `pr` and which has no `merged` event: `status.sh --report` does not list N under Waiting (merged-ness read from local `main` only, no network call) ⟦criterion 1⟧
- [x] The same fixture without that commit on `main` (no commit subject on `main` ends `(#N)`): `status.sh --report` still lists N under Waiting as ready to merge ⟦criterion 2⟧
- [x] Deciding merged-ness makes no `gh` call: with a `gh` on PATH that records its invocations, `status.sh --report` never invokes it, both with and without the `(#N)` commit on `main` ⟦criterion 3⟧ ⟂ retired unpinnable
- [ ] A journal for issue N whose last `done` event carries a `pr` whose PR number is P, and local `main` holding a commit with subject ending `(#P)` but none ending `(#N)`: `status.sh --report` does not list N under Waiting
- [ ] Go-red: with the `main`-subject check removed from `status.py`, the first criterion's case fails (N is listed); restored, it passes ⟦human-owed⟧ ⟦criterion 4⟧
