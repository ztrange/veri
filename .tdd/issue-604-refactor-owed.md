### the `usage` event harvest-usage.sh appends carries a `model` key naming the one model a result record's `modelUsage` lists ⟦criterion 1⟧
- extract a helper in harvest-usage.test.sh that writes a fixture log into a fresh work dir and runs the harvester there, shared by the "leaf-role.sh refuses" case and the new modelUsage case (worth it once steps 2–4 add more such cases)
