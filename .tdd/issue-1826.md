# Plan for #1826 — unreplaced-cases.sh never accepts a parametrized pytest case as a replacement

- [x] unreplaced-cases.sh counts a bash case as replaced when its REPLACES: line names a parametrized pytest case `<path>::<test>[<param id>]` and `<path>` defines `def <test>` (exit 0, the case not printed) ⟦criterion 1⟧
- [x] unreplaced-cases.sh still counts a bash case as unreplaced when its REPLACES: line names a parametrized node id `<path>::<test>[<param id>]` whose `def <test>` is absent from `<path>` (exit 1, the case printed) ⟦criterion 2⟧
- [ ] unreplaced-cases.sh still counts a bash case as unreplaced when its REPLACES: line names a node id `<path>::<test>` with no `[…]` suffix whose `def <test>` is absent from `<path>` (exit 1, the case printed) ⟦criterion 2⟧
