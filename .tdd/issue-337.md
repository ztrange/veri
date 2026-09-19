# Plan for #337 — `affected-suites.sh` prints the suites one change affects, per PRD's five rules, fail-closed

- [x] affected-suites.sh <base>..<head> prints one suite path per line, sorted, with no duplicate, for a range git can resolve ⟦criterion 1⟧
- [x] A malformed argument (missing `..`, or either side not a resolvable revision) exits 2 with a diagnostic ⟦criterion 2⟧
- [x] A range whose diff is empty exits 3 and prints nothing ⟦criterion 3⟧
- [x] Rule 1: a change to skills/tdd/scripts/foo.sh with a suite skills/tdd/scripts/tests/foo.test.sh prints exactly that suite ⟦criterion 4⟧
- [ ] Rule 1 via tests/unit/: a change to a script whose suite lives under skills/tdd/scripts/tests/unit/ prints that unit suite ⟦criterion 4⟧
- [ ] Rule 2: a change to skills/tdd/scripts/lib/bar.sh prints the suite of every script that sources it, and no others ⟦criterion 5⟧
- [ ] Rule 3: a change to a suite file itself prints that suite ⟦criterion 6⟧
- [ ] Rule 3: a change to a fixture under tests/fixtures/ prints every suite that references the fixture by name ⟦criterion 6⟧
- [ ] Rule 4: a change to SKILL.md, CLAUDE.md, or Makefile prints their guard suites ⟦criterion 7⟧
- [ ] Rule 5: a diff carrying one rule-1 file and one file no rule matches prints every suite (the full tier), not the rule-1 suite alone ⟦criterion 8⟧
- [ ] A diff touching only files rules 1–4 match never falls back to the full suite ⟦criterion 9⟧
