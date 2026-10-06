### A suite run through run-suite.sh reads maintenance.auto=false from its git config (git config --get maintenance.auto prints false inside the suite), as it does under make test ⟦criterion 1⟧
- `maintenance.auto=false` is now set in two places, `Makefile` `OFFLINE_ENV` (`GIT_CONFIG_KEY_3`/`GIT_CONFIG_VALUE_3`) and `run-suite.sh`, which could share one source so the two runners can't drift apart
