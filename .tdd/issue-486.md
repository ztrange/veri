# Plan for #486 — Every wall-time figure metrics.sh reports counts the hours the machine was asleep

- [x] event.sh writes an awake-clock reading on every event it appends, taken from the clock VERI_AWAKE_CLOCK names when set and otherwise from the same sleep-excluding clock supervise.sh uses for its windows ⟦criterion 1⟧
- [ ] supervise.sh's per-attempt secs on its exit event is the difference of two awake-clock readings, so a wall-clock jump the awake clock does not make is not counted ⟦criterion 6⟧
- [ ] metrics.sh's issue wall, given a log whose wall timestamps span a gap its awake-clock readings do not, excludes the gap and a figure beside it names the excluded seconds ⟦criterion 3⟧
- [ ] metrics.sh computes each step's wall from the awake-clock readings of its step-start and step-done events, so a sleep gap inside a step is not counted in that step's wall ⟦criterion 2⟧
- [ ] metrics.sh computes each phase's wall from awake-clock readings, so a sleep gap inside a leaf's attempt is not counted in that phase's wall ⟦criterion 2⟧
- [ ] metrics.sh, given a log with no awake-clock readings at all, prints every figure as the wall-clock one it prints today and says in its output that the figures are wall-clock ⟦criterion 4⟧
- [ ] metrics.sh, given a log where only some events carry an awake-clock reading, prints no figure computed from a mix of the two clocks and says which clock its figures are on ⟦criterion 5⟧
