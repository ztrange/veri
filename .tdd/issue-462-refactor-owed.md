### workqueue.sh assign naming the same issue twice in one call exits 2 and leaves .tdd/workqueue byte-identical ⟦criterion 2⟧
- assign's check against the existing queue could look up each held issue in the `named` table instead of looping over "$@", but only once an empty issue argument is refused first; until then it changes stderr for an empty-issue queue line
