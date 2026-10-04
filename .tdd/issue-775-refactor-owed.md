### refactor-overflow.sh, when gh fails filing the issue with any non-zero status (1, 3 and 5 alike), exits 2 ⟦criterion 2⟧
- test-only | rename the case at skills/tdd/scripts/tests/refactor-overflow.test.sh:285 from "refactor-overflow exits 1 …" to "exits 2 …": its assertion at :299 now expects exit 2, so the name contradicts what it checks
- test-only | fold the gh stub of the new case "exits 2 when gh fails filing the issue with status 1, 3 or 5" (refactor-overflow.test.sh:346-363) and the `failing_stubdir` stub at :288-295 into one stub with a parameterised status
