# Plan for #4734 — revise.sh revises the next unchecked step instead of the step whose refactor is pending

- [x] With step 1 ticked `⟂ refactor pending` and a REJECT recorded for step 1's red phase, the revise names step 1 in its `revise` mark and prompt ⟦criterion 1⟧
- [x] With step 1 ticked `⟂ refactor pending` and an open re-pin step directly after it, a red revise names the re-pin step, as run-step.sh takes it
- [x] With step 1 ticked `⟂ refactor pending` and an open re-pin step directly after it, a refactor revise still names step 1, the step whose refactor was rejected
