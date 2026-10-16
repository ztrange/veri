### The unit-tier admission guard fails when a planted suite under tests/unit/ runs a script under skills/tdd/scripts/ as a subprocess rather than sourcing it and mocking what it shells out to, naming that suite as `<suite>:<line>` ⟦criterion 1⟧
- test-only | the `flat()` helper is defined identically in both guard suites; it could move to `lib/harness.sh`
