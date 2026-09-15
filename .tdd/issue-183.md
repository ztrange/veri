# Plan for #183 — docs-read-guard.test.sh passes vacuously when its fixture plant fails

- [x] A failed plant (no marked line, or missing reader fixture) makes the case FAIL naming the broken premise
- [x] With the plant intact the suite still passes against the real guard and fails against a stub guard that always passes
