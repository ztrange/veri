### the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧
- extract a helper in harvest-usage.test.sh that writes a fixture log into a fresh work dir and runs the harvester there, shared by the "leaf-role.sh refuses" case and the new modelUsage case (worth it once steps 2–4 add more such cases)
### a result record with no `modelUsage` still yields a `usage` event with `model` empty, and harvest-usage.sh's exit code and stderr for it are unchanged ⟦criterion 2⟧
- the refused-leaf and unmodeled cases repeat the same "capture stderr and exit code from running the harvester in a work dir" line; it could become one helper, but at two uses the helper adds indirection for little gain
