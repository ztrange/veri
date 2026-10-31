# Plan for #2724 — A step's frozen-record ownership holds through phased ledger lines and its own refactor's renames

- [x] A re-record of a step whose ledger line went through phased `⟂ <phase> done` marks keeps the pins and renames that step committed, and no later step's, pinned by one real-git process case in test_tests_frozen_process.py whose committed ledger has that phased shape ⟦criterion 1⟧
- [x] A re-record of a fixture-repair step, whose ledger line ends in the fixture-repair marker, keeps the pins and renames that step committed, pinned by one real-git process case in test_tests_frozen_process.py whose committed ledger has that shape
- [x] A case renamed by a step's own refactor commit, landed between its green tick and its refactor-verified commit, is attributed on a later re-record to that step and not to the next step, pinned by one real-git process case in test_tests_frozen_process.py ⟦criterion 2⟧
- [x] Breaking the phased-line handling reddens the first case, watched going red and restored ⟦human-owed⟧ ⟦criterion 3⟧
