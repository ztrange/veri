# Plan for #2309 — metrics.sh reports each conductor session's first-turn and largest context

- [x] metrics.sh <n> prints, in the Conductor own spending section, one line per conductor session, `Conductor context: first turn <a> tokens, largest <b> tokens`, where <a> and <b> are the first and the largest context the per-turn table shows for that session; pinned by an in-process unit case over a conductor log of two sessions (each closed by a result record) with known per-turn usage ⟦criterion 1⟧
- [x] a run whose log holds no conductor usage prints no `Conductor context:` line and the report still exits 0; pinned by an in-process unit case ⟦criterion 2⟧
