### The same guard also names a pipeline that ends in `head` ⟦criterion 2⟧
- merge probe_plant_is_what_it_claims and probe_head_plant_is_what_it_claims — the head one's three assertions are the pair version's first three verbatim; the parameterized premises probe takes \<reader\>, and the innocent's two assertions become a probe of their own
- inline plant_offender and plant_innocent into plant — each is now a single write_plant call, and the indirection names nothing the call site does not say
### `prompt-test-tiers.test.sh`'s prompt probes give the same verdict on a matching and a non-matching prompt whether or not the writer is preempted ⟦criterion 1⟧
- `runs_fast_plus_affected` and `timed_through` each fold the prompt and then call `runs_affected`, which folds the same prompt a third time; one fold passed down would do
