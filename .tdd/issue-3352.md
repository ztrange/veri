# Plan for #3352 — A step whose text only quotes the mutation-record marker in prose exempts the record from restore

- [x] A step whose text names a record as a directive (`mutation-record: <path>` outside backticks and quotes) has that record left deleted by the leaf, and no `mutation-record-restored` event is emitted for it ⟦criterion 1⟧
- [ ] A step whose text quotes the marker only inside backticks (prose such as "the `mutation-record: <path>` marker") does not exempt the record: the leaf's deletion is restored and the `mutation-record-restored` event is emitted ⟦criterion 2⟧
- [ ] A step whose text quotes the marker only inside double quotes ("mutation-record: <path>") does not exempt the record: the leaf's deletion is restored and the `mutation-record-restored` event is emitted ⟦criterion 2⟧
- [ ] A step whose text quotes the marker only inside single quotes ('mutation-record: <path>') does not exempt the record: the leaf's deletion is restored and the `mutation-record-restored` event is emitted ⟦criterion 2⟧
- [ ] Go-red: with the directive-only matching broken on purpose (the regex scanning the whole step text again), the quoted-prose case goes red; restored afterwards ⟦human-owed⟧ ⟦criterion 3⟧
