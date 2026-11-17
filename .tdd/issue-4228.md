# Plan for #4228 — PRD 035.5a1: stages are marked, and preflight and the baseline suite are counted

- [x] under VERI_EVENT_STRICT=1 `stage-start` (`stage`) and `stage-end` (`stage`, `status` whole, `secs` whole) are accepted with `stage` one of preflight, baseline; JOURNAL.md states both ⟦criterion 1⟧
- [x] `event.stage` writes `stage-start`, runs its body and writes `stage-end` with the body's exit code and whole seconds, for a body exiting 0, 1 and 2 and one raising (status 2) ⟦criterion 2⟧
- [x] with the journal directory unwritable the stage helper returns the body's exit code unchanged ⟦criterion 3⟧
- [ ] `preflight.sh` runs inside stage `preflight` and its baseline suite inside stage `baseline` ⟦criterion 4⟧
- [ ] `metrics.sh <n> --json` holds `stages` keyed by stage with `runs`, `ok`, `failed`, `no_answer`, `nothing`, `unended` and `wall_seconds` ⟦criterion 5⟧
- [ ] a `stage-end` carrying an issue rewrites `<issue>.metrics.json` ⟦criterion 6⟧
- [ ] a journal with no stage event folds with `stages` `{}` ⟦criterion 7⟧
- [ ] `SCRIPTS.md`'s `preflight.sh` entry states the stages (SC271) and `PUBLISHED.md` states `stages` (PB20) ⟦criterion 8⟧
