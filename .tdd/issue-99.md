# Plan for #99 — Every CI job carries timeout-minutes, so a hung job bills minutes and not six hours

- [ ] the gates job in .github/workflows/ci.yml declares timeout-minutes: 3, with a comment beside it naming the 6-hour default ceiling it protects against, citing the ~40 s the job observably takes and the ~230 s it took when the docs gates ran in CI, and saying the budget assumes those gates stay out of CI
- [ ] the deploy job in .github/workflows/pages.yml declares timeout-minutes: 10, with a comment beside it naming the same 6-hour ceiling, citing the 11-23 s the job observably takes, and saying why its number is larger than the gates job's — it waits on GitHub's Pages service rather than on local deterministic work
- [ ] every job defined under .github/workflows/ declares a timeout-minutes, so a job added later without one is caught
