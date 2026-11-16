# Plan for #4022 — PRD 030.6: under the test suite, a value breaking its key's format fails its case

- [x] with `VERI_EVENT_STRICT=1`, `event.sh` and `event.mark` given a value its key's declared format rejects exit 2, write no line to either journal file, and name the event, the key and its format on stderr ⟦criterion 1⟧
- [x] with `VERI_EVENT_STRICT=1`, the same for an empty value of a key the table does not allow to be empty ⟦criterion 2⟧
- [x] without `VERI_EVENT_STRICT`, each of those two calls writes its line and exits 0 with nothing on stderr ⟦criterion 3⟧
- [x] every case that writes an event through the real path writes values its keys' formats accept, each fix taken from what the real writer emits
- [x] `SCRIPTS.md`'s `$S/event.sh` entry adds the format check to the strict mode ⟦criterion 4⟧
