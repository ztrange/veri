# Plan for #2700 — status.sh hides any run without a ledger, so a preflight refusal and a run still in preflight are both invisible

- [x] status.sh text lists a run with a worktree and an events.jsonl but no ledger whose only event is preflight-refused, as a line naming its issue number (the run directory's name) and `refused <check>` ⟦criterion 1⟧
- [x] status.sh text lists a run with no ledger, an events.jsonl holding no launch and no end mark, and a live conductor, as a line naming its issue number and `running` ⟦criterion 1⟧
- [x] status.sh --json never counts a run in the scope totals that it does not list: a run with no ledger whose run_activity returns None, an empty events.jsonl with no live conductor, is either both listed and counted or neither ⟦added⟧ ⟦criterion 3⟧
- [x] status.sh text shows `running` for a run with no ledger and a live conductor whose events.jsonl holds only a preflight-refused event from an earlier launch, the relaunch the issue observed for run 1059 ⟦criterion 1⟧
- [ ] status.sh text lists a run with no ledger, an events.jsonl holding no launch and no end mark, and no live conductor, as `stale` rather than omitting it
- [ ] status.sh text lists a run with no ledger, a live conductor and an empty events.jsonl as `running`, with exit 0 and no traceback
- [ ] status.sh --json includes a run with no ledger whose only event is preflight-refused, with `issue` its run directory's name, `state` `refused`, and `step` and `title` both empty ⟦criterion 2⟧
- [ ] status.sh --json includes a run with no ledger, an events.jsonl holding no launch and no end mark, and a live conductor, with `issue` its run directory's name, `state` `running`, and `step` and `title` both empty ⟦criterion 2⟧
- [ ] The scope totals' `attempted` counts a run with no ledger exactly once and the run is listed, so with one ledger run and one ledger-less refused run both the listed lines and `attempted` say 2 ⟦criterion 3⟧
- [ ] The scope totals' `attempted` counts a listed run that has a ledger and no events.jsonl, so `attempted` equals the runs listed for it too; a run whose events vanish after render read them stays out of the totals as test_main_json_leaves_a_run_out_of_the_scope_totals_when_its_events_vanish_after_render_read_them_2559 pins ⟦criterion 3⟧
