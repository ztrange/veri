### `workqueue.sh <unknown-subcommand> …` (e.g. `workqueue.sh frobnicate alpha 12`) exits 2 and leaves `.tdd/workqueue` byte-identical (absent if it was absent) ⟦added⟧ ⟦criterion 1⟧
- both cases in `workqueue.test.sh` repeat the same pass/fail block (`pass=$((pass + 1))` / `fail=…; echo "FAIL - …"`). With only two cases and a different diagnostic in each, that repetition doesn't justify a helper yet. It will once the `next`/`start`/`done`/`park` cases arrive.
### `workqueue.sh next <worker>` prints that worker's first `queued` issue whose `## Blocked by` names no open issue, skipping a blocked one, read from `VERI_GH_JSON` fixtures ⟦criterion 2⟧
- extract `blocked_by.unblocked(body, repo, open_issues)` for the duplicated check in solvable-issues.sh and workqueue.sh `next`; this needs blocked-by.test.sh case 5's stand-in module to define it too, and that file is outside this step
### `workqueue.sh start <worker> <issue>` moves that worker's `queued` item to `running` ⟦criterion 3⟧
- fold case 12 (start leaves another worker's item queued) into expect_queue once the ownership step pins its exit code
### `workqueue.sh done <worker> <issue> <sha>` moves that worker's `running` item to `merged`, recording the sha as its detail ⟦criterion 3⟧
- the `repo="$work/<case>"; new_repo "$repo"; seed_queue …` setup repeated across 12 cases of workqueue.test.sh could become one helper — mostly code earlier cycles wrote, so out of this step's bounds
### `start`, `done` or `park` naming an item another worker owns exits 1 and leaves the file byte-identical ⟦criterion 3⟧
- fold the repeated `repo="$work/<case>"; new_repo "$repo"; seed_queue …` setup into one helper — code earlier cycles wrote, out of this step's bounds
- extract `blocked_by.unblocked(body, repo, open_issues)` shared by solvable-issues.sh and workqueue.sh `next` — needs blocked-by.test.sh's stand-in module, outside this step
