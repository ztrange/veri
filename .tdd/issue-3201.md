# Plan for #3201 — metrics.sh raises TypeError when VERI_SESSION_TRANSCRIPTS is set and no event has a timestamp

- [x] With `VERI_SESSION_TRANSCRIPTS` naming a directory that holds a timestamped `/vcoord` transcript, and an event log with no timestamped event, `metrics.sh <n>` exits 0 and reports the coordinator session's turns, cache tokens read and $ counting that transcript's turns (a missing window start bounds nothing, as `until=None` already does) ⟦criterion 1⟧ ⟂ refactor pending
