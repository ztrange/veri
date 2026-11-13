before 40
19456e9a131bb7c4b3cf0c5801b6d77892655bf7
keep 55
skills/tdd/scripts/tests/py/test_pin_recheck_process.py
command 200
make test TESTS=skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_3740_a_pin_green_under_its_mutation_beside_a_record_whose_file_is_absent_still_exits_1_naming_it_and_leaves_its_file_alone

file 38
skills/tdd/scripts/veri/pin_recheck.py
old 95
        if not path.exists():
            sys.stdout.write(f"stale: {ledger} {mutated_file}\n")
new 83
        if False:
            sys.stdout.write(f"stale: {ledger} {mutated_file}\n")
command 180
make test TESTS=skills/tdd/scripts/tests/py/test_pin_recheck_process.py::test_3740_a_mutation_record_whose_file_is_absent_and_not_deleted_in_the_range_is_reported_stale_and_skipped

