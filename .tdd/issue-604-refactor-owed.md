### the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧
- extract a helper in harvest-usage.test.sh that writes a fixture log into a fresh work dir and runs the harvester there, shared by the "leaf-role.sh refuses" case and the new modelUsage case (worth it once steps 2–4 add more such cases)
### a result record with no `modelUsage` still yields a `usage` event with `model` empty, and harvest-usage.sh's exit code and stderr for it are unchanged ⟦criterion 2⟧
- the refused-leaf and unmodeled cases repeat the same "capture stderr and exit code from running the harvester in a work dir" line; it could become one helper, but at two uses the helper adds indirection for little gain
### metrics.sh prints a "By model" table with one row per (role, model) — role developer or verifier — carrying the same columns as "By phase" ⟦criterion 3⟧
- the By model rendering loop in metrics.sh repeats `section()`'s row loop; folding it in would mean teaching `section` about tuple keys and a text column ahead of the figures, which is more code than it removes
- `by_model_says` in metrics.test.sh re-implements the table-body parsing that `tables_in` in `PROBE_PRELUDE` already does (the cells/SEPARATOR filter), scoped to one heading
