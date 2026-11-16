# Plan for #3837 — PRD 030.1b: under the test suite, an event the table does not allow fails the case that wrote it

- [x] with `VERI_EVENT_STRICT=1`, `event.sh` and `event.mark` given an event name the table does not hold exit 2, write no line to either journal file, and name the event on stderr ⟦criterion 1⟧
- [ ] with `VERI_EVENT_STRICT=1`, the same for a key the table does not declare for that event, naming the event and the key ⟦criterion 2⟧
- [ ] with `VERI_EVENT_STRICT=1`, the same when a key the table marks required is missing, naming the event and the key ⟦criterion 3⟧
- [ ] without `VERI_EVENT_STRICT`, each of those three calls writes its line and exits 0 with nothing on stderr ⟦criterion 4⟧
- [ ] the `hermetic_environment` fixture sets `VERI_EVENT_STRICT=1`: a case that emits an undeclared key through `event.mark` gets exit 2 ⟦criterion 5⟧
- [ ] the environment `run_conductor.py` gives a run's conductor never carries `VERI_EVENT_STRICT`, also when the launching environment sets it ⟦criterion 6⟧
- [ ] `SCRIPTS.md`'s `event.sh` entry states the strict mode, graded by the issue's `## Requirements` rows ⟦criterion 7⟧
