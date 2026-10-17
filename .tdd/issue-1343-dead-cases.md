# Dead cases for #1343

- `this suite lives in tests/, with the suites that run their script through its entry point` (skills/tdd/scripts/tests/stop-requested.test.sh): not ported, no replacement. Its only subject is the bash suite's own file, which this issue deletes, so no production mutation can turn a replacement red.
