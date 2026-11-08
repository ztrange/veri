file 41
skills/tdd/scripts/veri/mutation_probe.py
old 34
    path = Path(argv[0])
    saved
new 74
    if "@" in argv[2]:
        return 2
    path = Path(argv[0])
    saved
command 168
make test TESTS=skills/tdd/scripts/tests/py/unit/test_mutation_probe.py::test_main_accepts_and_records_an_outside_address_when_the_address_domain_is_unset_or_empty_3330

