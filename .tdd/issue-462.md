# Plan for #462 — workqueue.sh's argument guards are unwritten: the five steps #271 filed as owed

- [x] workqueue.sh assign with no worker, or with a worker and no issue, exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 1⟧
- [x] workqueue.sh assign naming the same issue twice in one call exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 2⟧
- [x] workqueue.sh assign given an empty issue argument exits 2 and leaves .tdd/workqueue byte-identical ⟦added⟧ ⟦criterion 2⟧
- [x] workqueue.sh done with a worker and an issue but no merge sha exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 3⟧
- [x] workqueue.sh done with an empty merge sha argument ("") exits 2 and leaves .tdd/workqueue byte-identical ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending
- [ ] workqueue.sh park with a reason containing a tab or a newline treats both characters the same way, either keeping the queue one line per item with four tab-separated fields or refusing with the file untouched ⟦criterion 4⟧
- [ ] workqueue.sh show <worker> prints only that worker's group, and for a worker with no items prints nothing and exits 0 ⟦criterion 5⟧
