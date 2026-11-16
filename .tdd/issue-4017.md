# Plan for #4017 — PRD 028.3: `reuse` re-times a stale full-tier time

- [x] `full-tier-time.sh --record <seconds> <command>` writes the epoch seconds it recorded at for `<command>` into `.tdd/full-tier-time-at.json`, while `full-tier-time.json` still holds `{"<command>": "<seconds>"}` and the read form prints the seconds ⟦criterion 1⟧
- [x] `--record` replaces only `<command>`'s recorded-at entry, keeping the others, and replaces an unreadable `full-tier-time-at.json` whole ⟦criterion 1⟧
- [x] `VERI_FULL_TIER_MAX_AGE_DAYS` is a `tunables.TABLE` entry, default `7`, refusal "a whole number of days >= 1", and `run-conductor.sh` given `0` or a non-whole value exits 2 before preflight naming it and its value ⟦criterion 2⟧
- [x] Under `reuse`, a recorded time with no recorded-at (no `full-tier-time-at.json`, no entry for the command, or an unreadable file) makes `baseline-full-tier.sh` print `run`, exit 0, and write one stderr line naming the command, `unknown` and the knob's value ⟦criterion 4⟧
- [x] Under `reuse`, a recorded-at older than `VERI_FULL_TIER_MAX_AGE_DAYS` × 86,400 s makes it print `run`, exit 0, with one stderr line naming the command, the age in whole days and the knob's value; one at most that old prints `reuse <seconds>` ⟦criterion 4⟧ ⟦criterion 3⟧
- [x] After a stale `run`, a `--record` of new seconds makes the next `baseline-full-tier.sh` print `reuse` with the new seconds ⟦criterion 5⟧
- [x] Under `reuse`, an unreadable `full-tier-time.json` makes `baseline-full-tier.sh` exit 2 naming the error, and no `full-tier-time.json` prints `run` ⟦criterion 6⟧
- [ ] Under `reuse`, a `VERI_FULL_TIER_MAX_AGE_DAYS` that is not a whole number >= 1 makes `baseline-full-tier.sh` exit 2 naming it and its value; under `run` it changes nothing ⟦criterion 7⟧
- [ ] `SCRIPTS.md`'s `full-tier-time.sh` and `baseline-full-tier.sh` entries and `PREFLIGHT.md` step 3 state the recorded-at file and the age rule, graded ⟦criterion 8⟧
