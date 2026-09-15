# Plan for #183 — docs-read-guard.test.sh passes vacuously when its fixture plant fails

- [ ] A failed plant (no marked line, or missing reader fixture) makes the case FAIL naming the broken premise
- [ ] With the plant intact the suite still passes against the real guard and fails against a stub guard that always passes
