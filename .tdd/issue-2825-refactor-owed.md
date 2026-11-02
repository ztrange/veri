not-done | transform-rejected | Extract the HEAD-presence pre-check in `rerecord_rebased` into a named helper
not-done | transform-rejected | Share one record iterator between the new pre-check and `_rewrite_records`
### `tests-frozen.sh rerecord-rebased` given an earlier step's frozen record whose case title is missing at HEAD exits 2 with no traceback and no `KeyError`, its stderr naming the record file and the missing title, and rewrites no record ⟦criterion 1⟧
- extract the missing-title pre-pass in `rerecord_rebased` (`tests_frozen.py` ~line 671) into a named function; extraction, not duplication removal
- cache the HEAD case map per recorded file so the pre-pass and `rewrite` don't each run `git show` per record; repeated subprocess work, not duplicated code
- test-only | shorten the new test name `test_rerecord_rebased_with_a_recorded_title_missing_at_head_exits_2_naming_the_record_and_the_title_and_rewrites_no_record_2825`
