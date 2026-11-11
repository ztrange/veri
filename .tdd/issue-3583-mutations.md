file 37
skills/tdd/scripts/veri/role_state.py
old 42
if argv[2] not in LISTS or len(argv) != 4:
new 93
if argv[2] not in LISTS or len(argv) != 4 or (argv[2] == "timed-n" and " until " in argv[3]):
context 46
    if argv[2] not in LISTS or len(argv) != 4:
command 136
make test TESTS=skills/tdd/scripts/tests/py/test_role_state_process.py::test_coord_add_to_each_list_prints_an_id_and_show_lists_the_text

